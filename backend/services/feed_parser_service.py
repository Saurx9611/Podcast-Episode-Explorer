import re
import socket
import ipaddress
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import httpx
import feedparser
from dateutil import parser as date_parser

from backend.core.exceptions import ValidationException

MAX_FEED_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
FEED_FETCH_TIMEOUT_SECONDS = 12.0

BLOCKED_HOSTNAMES = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}

def is_private_or_loopback_ip(ip_str: str) -> bool:
    """Checks if an IP address string belongs to private, loopback, link-local, or reserved blocks."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )
    except ValueError:
        return False

def validate_feed_url(url: str) -> str:
    """Validates feed URL and protects against SSRF attacks."""
    if not url or not isinstance(url, str):
        raise ValidationException("Feed URL must be a valid non-empty string.")

    cleaned_url = url.strip()
    parsed = urlparse(cleaned_url)

    if parsed.scheme not in ("http", "https"):
        raise ValidationException(f"Unsupported URL scheme '{parsed.scheme}'. Only http and https are allowed.")

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValidationException("Invalid feed URL: missing hostname.")

    if hostname in BLOCKED_HOSTNAMES:
        raise ValidationException(f"Access to internal hostname '{hostname}' is forbidden for security.")

    # If hostname is an IP literal, verify it's not private
    if is_private_or_loopback_ip(hostname):
        raise ValidationException(f"Access to private/internal IP '{hostname}' is forbidden for security.")

    # Try DNS resolution to verify destination IP is public
    try:
        resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for family, socktype, proto, canonname, sockaddr in resolved_ips:
            ip_addr = sockaddr[0]
            if is_private_or_loopback_ip(ip_addr):
                raise ValidationException(f"Resolved destination IP '{ip_addr}' is private/internal and forbidden.")
    except socket.gaierror:
        # If DNS lookup fails during validation, raise a validation error
        raise ValidationException(f"Could not resolve hostname '{hostname}'.")

    return cleaned_url

def parse_duration_seconds(duration_raw: Any) -> Optional[float]:
    """Parses various podcast duration formats (HH:MM:SS, MM:SS, numeric seconds) to float seconds."""
    if duration_raw is None:
        return None
    
    if isinstance(duration_raw, (int, float)):
        return float(duration_raw) if duration_raw >= 0 else None

    duration_str = str(duration_raw).strip()
    if not duration_str:
        return None

    # Format: HH:MM:SS or MM:SS
    if ":" in duration_str:
        parts = duration_str.split(":")
        try:
            if len(parts) == 3:
                h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = float(parts[0]), float(parts[1])
                return m * 60 + s
        except ValueError:
            pass

    # Numeric seconds string
    try:
        return float(duration_str)
    except ValueError:
        return None

def parse_publication_date(entry: Dict[str, Any]) -> Optional[datetime]:
    """Extracts and parses publication date from feed entry."""
    # 1. published / pubDate
    date_str = entry.get("published") or entry.get("pubDate") or entry.get("updated")
    if date_str:
        try:
            dt = date_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            pass

    # 2. published_parsed time struct
    parsed_time = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed_time:
        try:
            return datetime(*parsed_time[:6], tzinfo=timezone.utc)
        except Exception:
            pass

    return None

class FeedParserService:
    """Service for fetching, validating, and parsing podcast RSS and Atom feeds."""

    async def fetch_feed_xml(self, url: str) -> str:
        """Fetches feed XML with timeout, redirect limits, and response size bounds."""
        validated_url = validate_feed_url(url)
        headers = {
            "User-Agent": "PodcastExplorer/1.0 (+https://podcastexplorer.ai; RSS Ingestion Engine)",
            "Accept": "application/rss+xml, application/rdf+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(FEED_FETCH_TIMEOUT_SECONDS, connect=5.0),
                follow_redirects=True,
                max_redirects=5,
            ) as client:
                response = await client.get(validated_url, headers=headers)
                response.raise_for_status()

                content_bytes = response.content
                if len(content_bytes) > MAX_FEED_SIZE_BYTES:
                    raise ValidationException(
                        f"Feed content ({len(content_bytes) / (1024*1024):.1f}MB) exceeds maximum limit of {MAX_FEED_SIZE_BYTES / (1024*1024):.0f}MB."
                    )

                return response.text
        except httpx.TimeoutException:
            raise ValidationException(f"Network timeout fetching feed from '{validated_url}'. Please verify URL is accessible.")
        except httpx.HTTPStatusError as e:
            raise ValidationException(f"HTTP error {e.response.status_code} fetching feed: {e.response.reason_phrase}")
        except httpx.RequestError as e:
            raise ValidationException(f"Network error fetching feed from '{validated_url}': {str(e)}")

    def parse_feed_content(self, xml_content: str, source_url: Optional[str] = None) -> Dict[str, Any]:
        """Parses RSS/Atom XML content and extracts structured podcast and episode metadata."""
        if not xml_content or not xml_content.strip():
            raise ValidationException("RSS feed content is empty.")

        parsed = feedparser.parse(xml_content)

        # Check for catastrophic parsing failure (bozo with empty entries and feed)
        if getattr(parsed, "bozo", 0) and not parsed.get("feed") and not parsed.get("entries"):
            bozo_exc = getattr(parsed, "bozo_exception", "Malformed XML structure")
            raise ValidationException(f"Failed to parse RSS feed: {bozo_exc}")

        feed_data = parsed.get("feed", {})
        entries = parsed.get("entries", [])

        # Extract Podcast Metadata
        title = feed_data.get("title") or "Untitled Podcast"
        description = feed_data.get("summary") or feed_data.get("description") or feed_data.get("subtitle")
        author = feed_data.get("author") or feed_data.get("itunes_author") or feed_data.get("publisher")
        publisher = feed_data.get("publisher") or author
        
        # Artwork
        artwork_url = None
        if feed_data.get("image"):
            artwork_url = feed_data["image"].get("href")
        if not artwork_url and feed_data.get("itunes_image"):
            artwork_url = feed_data.get("itunes_image")

        language = feed_data.get("language") or "en"
        website_url = feed_data.get("link")

        podcast_metadata = {
            "title": title.strip(),
            "description": description.strip() if description else None,
            "author": author.strip() if author else None,
            "publisher": publisher.strip() if publisher else None,
            "artwork_url": artwork_url,
            "language": language[:10] if language else "en",
            "feed_url": source_url,
            "website_url": website_url,
        }

        # Extract Episodes Metadata
        episodes_list: List[Dict[str, Any]] = []
        for idx, entry in enumerate(entries):
            ep_title = entry.get("title") or f"Episode {len(entries) - idx}"
            ep_desc = entry.get("summary") or entry.get("description") or entry.get("subtitle")
            pub_date = parse_publication_date(entry)
            
            # Duration
            raw_dur = entry.get("itunes_duration") or entry.get("duration")
            duration_sec = parse_duration_seconds(raw_dur)

            # GUID / ID
            guid = entry.get("id") or entry.get("guid") or entry.get("link")

            # Episode / Season Number
            ep_num = None
            if entry.get("itunes_episode"):
                try:
                    ep_num = int(entry.get("itunes_episode"))
                except (ValueError, TypeError):
                    pass

            season_num = None
            if entry.get("itunes_season"):
                try:
                    season_num = int(entry.get("itunes_season"))
                except (ValueError, TypeError):
                    pass

            # Episode Artwork
            ep_art = None
            if entry.get("image"):
                ep_art = entry["image"].get("href")
            if not ep_art and entry.get("itunes_image"):
                ep_art = entry.get("itunes_image")
            if not ep_art:
                ep_art = artwork_url

            # Enclosure audio URL and size
            audio_url = None
            file_size = None
            mime_type = "audio/mpeg"

            enclosures = entry.get("enclosures", [])
            for enc in enclosures:
                enc_href = enc.get("href") or enc.get("url")
                enc_type = enc.get("type", "")
                if enc_href and ("audio" in enc_type or enc_href.endswith((".mp3", ".m4a", ".wav", ".aac", ".ogg")) or not enc_type):
                    audio_url = enc_href
                    mime_type = enc_type or "audio/mpeg"
                    try:
                        file_size = int(enc.get("length"))
                    except (ValueError, TypeError):
                        pass
                    break

            # Fallback to media:content or links
            if not audio_url and entry.get("media_content"):
                for mc in entry.get("media_content", []):
                    mc_url = mc.get("url")
                    if mc_url and ("audio" in mc.get("type", "") or mc_url.endswith((".mp3", ".m4a", ".wav"))):
                        audio_url = mc_url
                        mime_type = mc.get("type", "audio/mpeg")
                        break

            episodes_list.append({
                "title": ep_title.strip(),
                "description": ep_desc.strip() if ep_desc else None,
                "publication_date": pub_date,
                "duration": duration_sec,
                "guid": guid,
                "episode_number": ep_num,
                "season_number": season_num,
                "artwork_url": ep_art,
                "audio_url": audio_url,
                "file_size": file_size,
                "mime_type": mime_type,
            })

        return {
            "podcast": podcast_metadata,
            "episodes": episodes_list,
        }

    async def parse_url(self, url: str) -> Dict[str, Any]:
        """Fetches and parses a remote RSS feed URL."""
        xml = await self.fetch_feed_xml(url)
        return self.parse_feed_content(xml, source_url=url)

feed_parser_service = FeedParserService()
