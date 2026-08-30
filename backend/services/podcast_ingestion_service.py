import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.models.podcast import Podcast
from backend.models.episode import Episode
from backend.repositories.podcast_repo import PodcastRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.services.feed_parser_service import feed_parser_service, FeedParserService

logger = logging.getLogger("backend.services.podcast_ingestion")

class PodcastIngestionService:
    """Coordinates podcast RSS ingestion, deduplication, and database persistence."""

    def __init__(self, parser_service: Optional[FeedParserService] = None):
        self.parser = parser_service or feed_parser_service

    async def ingest_feed_url(
        self,
        db: Session,
        feed_url: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetches, parses, deduplicates, and stores podcast and episode records from an RSS feed URL.
        Does NOT download heavy audio files automatically (imports metadata-first).
        """
        logger.info(f"Starting RSS ingestion for feed URL: {feed_url}")
        
        # 1. Fetch & Parse RSS
        feed_result = await self.parser.parse_url(feed_url)
        return self.ingest_parsed_data(db, feed_result, project_id=project_id, feed_url=feed_url)

    def ingest_parsed_data(
        self,
        db: Session,
        feed_result: Dict[str, Any],
        project_id: Optional[str] = None,
        feed_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ingests structured feed data into the database with deduplication."""
        podcast_repo = PodcastRepository(db)
        episode_repo = EpisodeRepository(db)

        pod_data = feed_result.get("podcast", {})
        episodes_data = feed_result.get("episodes", [])
        resolved_feed_url = feed_url or pod_data.get("feed_url")

        # 2. Upsert Podcast Record
        podcast = None
        if resolved_feed_url:
            podcast = podcast_repo.get_by_feed_url(resolved_feed_url)

        if not podcast:
            podcast = Podcast(
                title=pod_data.get("title", "Untitled Podcast"),
                description=pod_data.get("description"),
                author=pod_data.get("author"),
                publisher=pod_data.get("publisher"),
                artwork_url=pod_data.get("artwork_url"),
                language=pod_data.get("language", "en"),
                feed_url=resolved_feed_url,
                website_url=pod_data.get("website_url"),
            )
            podcast = podcast_repo.create(podcast)
            logger.info(f"Created new podcast record: '{podcast.title}' (ID: {podcast.id})")
        else:
            # Update existing podcast metadata if updated in RSS
            if pod_data.get("title"):
                podcast.title = pod_data["title"]
            if pod_data.get("description"):
                podcast.description = pod_data["description"]
            if pod_data.get("author"):
                podcast.author = pod_data["author"]
            if pod_data.get("artwork_url"):
                podcast.artwork_url = pod_data["artwork_url"]
            if pod_data.get("website_url"):
                podcast.website_url = pod_data["website_url"]
            podcast = podcast_repo.update(podcast)
            logger.info(f"Updated existing podcast record: '{podcast.title}' (ID: {podcast.id})")

        # 3. Deduplicate and Persist Episodes
        new_imported_count = 0
        updated_count = 0
        processed_episodes: List[Episode] = []

        for ep_item in episodes_data:
            guid = ep_item.get("guid")
            audio_url = ep_item.get("audio_url")
            title = ep_item.get("title", "Untitled Episode")

            # Check deduplication
            existing_ep = None
            if guid:
                existing_ep = episode_repo.get_by_guid(podcast.id, guid)
            if not existing_ep:
                existing_ep = episode_repo.get_by_audio_url_or_title(podcast.id, audio_url, title)

            if existing_ep:
                # Update missing fields if available
                updated = False
                if not existing_ep.publication_date and ep_item.get("publication_date"):
                    existing_ep.publication_date = ep_item["publication_date"]
                    updated = True
                if not existing_ep.duration and ep_item.get("duration"):
                    existing_ep.duration = ep_item["duration"]
                    updated = True
                if not existing_ep.artwork_url and ep_item.get("artwork_url"):
                    existing_ep.artwork_url = ep_item["artwork_url"]
                    updated = True
                if not existing_ep.episode_number and ep_item.get("episode_number"):
                    existing_ep.episode_number = ep_item["episode_number"]
                    updated = True
                if not existing_ep.season_number and ep_item.get("season_number"):
                    existing_ep.season_number = ep_item["season_number"]
                    updated = True
                if updated:
                    episode_repo.update(existing_ep)
                    updated_count += 1
                processed_episodes.append(existing_ep)
            else:
                # Create new episode in 'uploaded' status (metadata only)
                new_ep = Episode(
                    podcast_id=podcast.id,
                    project_id=project_id if project_id and project_id != "none" else None,
                    guid=guid,
                    title=title,
                    description=ep_item.get("description"),
                    publication_date=ep_item.get("publication_date"),
                    duration=ep_item.get("duration") or 0.0,
                    episode_number=ep_item.get("episode_number"),
                    season_number=ep_item.get("season_number"),
                    artwork_url=ep_item.get("artwork_url"),
                    audio_url=audio_url,
                    file_size=ep_item.get("file_size"),
                    mime_type=ep_item.get("mime_type", "audio/mpeg"),
                    status="uploaded",
                )
                created_ep = episode_repo.create(new_ep)
                new_imported_count += 1
                processed_episodes.append(created_ep)

        logger.info(
            f"Completed RSS ingestion for '{podcast.title}': "
            f"{len(episodes_data)} total in feed, {new_imported_count} new imported, {updated_count} updated."
        )

        return {
            "podcast": podcast,
            "total_episodes_in_feed": len(episodes_data),
            "new_episodes_imported": new_imported_count,
            "updated_episodes": updated_count,
            "episodes": processed_episodes,
        }

podcast_ingestion_service = PodcastIngestionService()
