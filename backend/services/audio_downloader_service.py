import os
import asyncio
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import httpx
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.exceptions import ValidationException, NotFoundException
from backend.models.episode import Episode
from backend.models.processing_job import ProcessingJob
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.processing_repo import ProcessingRepository
from backend.services.feed_parser_service import validate_feed_url
from backend.storage.base import AudioStorageService
from backend.storage.local_storage import LocalStorageService

logger = logging.getLogger("backend.services.audio_downloader")

CHUNK_SIZE = 64 * 1024  # 64 KB
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 60.0
MAX_DOWNLOAD_RETRIES = 3
ALLOWED_AUDIO_MIME_PREFIXES = ("audio/", "video/mp4", "application/octet-stream", "binary/octet-stream")

def derive_clean_filename(episode: Episode, audio_url: str) -> str:
    """Derives a clean filename with extension for the episode."""
    parsed = urlparse(audio_url)
    path_name = os.path.basename(parsed.path)
    
    ext = os.path.splitext(path_name)[1].lower()
    if ext not in (".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac"):
        ext = ".mp3"

    base_title = episode.title or "episode"
    # Keep alphanumeric characters
    clean_title = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in base_title)[:50]
    return f"{clean_title}{ext}"

class AudioDownloaderService:
    """Service for streaming and downloading podcast episode audio from external URLs into storage."""

    def __init__(self, storage_service: Optional[AudioStorageService] = None):
        self.storage = storage_service or LocalStorageService()

    async def download_episode_audio(
        self,
        db: Session,
        episode_id: str,
        force_redownload: bool = False,
    ) -> Episode:
        """
        Downloads the remote audio for an episode in chunks, saving it directly to storage.
        Updates Episode status and tracks progress with ProcessingJob.
        """
        ep_repo = EpisodeRepository(db)
        proc_repo = ProcessingRepository(db)

        episode = ep_repo.get_by_id(episode_id)
        if not episode:
            raise NotFoundException("Episode", episode_id)

        if not episode.audio_url:
            raise ValidationException(f"Episode '{episode.title}' (ID: {episode_id}) has no audio URL.")

        # 1. Idempotency Check: Already downloaded and local?
        if not force_redownload and episode.audio_url.startswith("/storage/") and self.storage.file_exists(episode.audio_url):
            logger.info(f"Episode '{episode.title}' audio already downloaded at {episode.audio_url}. Skipping.")
            return episode

        # 2. Validate URL (SSRF and protocol protection)
        validated_url = validate_feed_url(episode.audio_url)

        # 3. Create or update ProcessingJob for tracking
        job = proc_repo.get_by_episode_id(episode_id)
        if not job:
            job = ProcessingJob(
                episode_id=episode_id,
                current_stage="download",
                status="in_progress",
                progress=5.0,
            )
            job = proc_repo.create(job)
        else:
            job.current_stage = "download"
            job.status = "in_progress"
            job.progress = 5.0
            job.error_message = None
            job = proc_repo.update(job)

        # Update Episode status
        episode.status = "downloading"
        ep_repo.update(episode)

        filename = derive_clean_filename(episode, validated_url)
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        # 4. Stream download with retries and exponential backoff
        last_error = None
        for attempt in range(1, MAX_DOWNLOAD_RETRIES + 1):
            try:
                logger.info(f"Downloading episode '{episode.title}' (attempt {attempt}/{MAX_DOWNLOAD_RETRIES}) from {validated_url}")
                
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT),
                    follow_redirects=True,
                    max_redirects=5,
                ) as client:
                    async with client.stream("GET", validated_url, headers={"User-Agent": "PodcastExplorer/1.0"}) as response:
                        if response.status_code == 404:
                            raise ValidationException(f"Audio file not found (HTTP 404) at '{validated_url}'.")
                        if response.status_code >= 400:
                            raise ValidationException(f"HTTP {response.status_code} error fetching audio: {response.reason_phrase}")

                        content_type = response.headers.get("content-type", "audio/mpeg").lower()
                        # Content-length check if provided
                        content_length_hdr = response.headers.get("content-length")
                        if content_length_hdr:
                            try:
                                content_length = int(content_length_hdr)
                                if content_length > max_bytes:
                                    raise ValidationException(
                                        f"Audio file size ({content_length / (1024*1024):.1f}MB) exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
                                    )
                            except (ValueError, TypeError):
                                pass

                        # Stream chunks directly into storage
                        async def chunk_streamer():
                            async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                                yield chunk

                        saved_url, saved_name, total_size, mime = await self.storage.save_stream(
                            stream_iterator=chunk_streamer(),
                            filename=filename,
                            content_type=content_type,
                            max_size_bytes=max_bytes,
                        )

                        # Update Episode on success
                        episode.original_filename = saved_name
                        episode.audio_url = saved_url
                        episode.file_size = total_size
                        episode.mime_type = mime
                        episode.status = "uploaded"
                        episode = ep_repo.update(episode)

                        # Update ProcessingJob
                        job.status = "completed"
                        job.progress = 100.0
                        proc_repo.update(job)

                        logger.info(f"Successfully downloaded '{episode.title}' ({total_size / (1024*1024):.2f}MB) -> {saved_url}")
                        return episode

            except ValidationException as ve:
                last_error = ve
                break  # Don't retry validation or 404 errors
            except (httpx.RequestError, httpx.TimeoutException, OSError) as net_err:
                last_error = net_err
                logger.warning(f"Download attempt {attempt} failed for '{episode.title}': {net_err}")
                if attempt < MAX_DOWNLOAD_RETRIES:
                    await asyncio.sleep(1.0 * (2 ** (attempt - 1)))  # Backoff: 1s, 2s

        # If all attempts failed
        error_msg = f"Failed to download audio for episode '{episode.title}': {str(last_error)}"
        logger.error(error_msg)

        episode.status = "failed"
        ep_repo.update(episode)

        job.status = "failed"
        job.error_message = str(last_error)
        proc_repo.update(job)

        if isinstance(last_error, ValidationException):
            raise last_error
        raise ValidationException(error_msg)

audio_downloader_service = AudioDownloaderService()
