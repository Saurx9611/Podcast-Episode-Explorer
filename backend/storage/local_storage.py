import os
import re
import uuid
from datetime import datetime, timezone
from typing import Tuple, Optional
from fastapi import UploadFile
from backend.core.config import settings
from backend.core.exceptions import ValidationException
from backend.storage.base import BaseStorageService

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".mp4"}

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename by removing path separators and unsafe characters."""
    base = os.path.basename(filename)
    # Remove null bytes and non-printable characters
    base = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', base)
    # Keep alphanumeric, dashes, underscores, and periods
    clean = re.sub(r'[^a-zA-Z0-9._-]', '_', base)
    return clean or "uploaded_audio.mp3"

class LocalStorageService(BaseStorageService):
    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or settings.STORAGE_PATH
        os.makedirs(self.storage_dir, exist_ok=True)

    def validate_file(self, filename: str, content_type: Optional[str], file_size: int):
        # 1. Validate filename and extension
        if not filename:
            raise ValidationException("Filename cannot be empty.")
            
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Unsupported audio file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # 2. Validate MIME type
        if content_type:
            allowed_types = set(settings.ALLOWED_MIME_TYPES) | {"audio/*", "application/octet-stream"}
            # Check if matching any allowed type or prefix
            if not any(content_type.startswith(t.replace("*", "")) for t in allowed_types):
                raise ValidationException(
                    f"Unsupported audio MIME type '{content_type}'. Please upload a valid audio file."
                )

        # 3. Validate file size
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValidationException(
                f"File size ({file_size / (1024 * 1024):.1f}MB) exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )
        if file_size == 0:
            raise ValidationException("Uploaded audio file is empty (0 bytes).")

    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        raw_filename = file.filename or "audio.mp3"
        clean_name = sanitize_filename(raw_filename)
        content_type = file.content_type or "audio/mpeg"

        # Read contents
        contents = await file.read()
        file_size = len(contents)

        # Perform strict validation
        self.validate_file(raw_filename, content_type, file_size)

        # Create unique file name
        unique_prefix = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        saved_filename = f"{unique_prefix}_{clean_name}"
        destination_path = os.path.join(self.storage_dir, saved_filename)

        with open(destination_path, "wb") as f:
            f.write(contents)

        # URL path for static file serving
        audio_url = f"/storage/{saved_filename}"

        return audio_url, raw_filename, file_size, content_type

    def save_bytes(self, contents: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, int, str]:
        raw_filename = filename or "audio.mp3"
        clean_name = sanitize_filename(raw_filename)
        mime = content_type or "audio/mpeg"
        file_size = len(contents)

        # Perform strict validation
        self.validate_file(raw_filename, mime, file_size)

        # Create unique file name
        unique_prefix = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        saved_filename = f"{unique_prefix}_{clean_name}"
        destination_path = os.path.join(self.storage_dir, saved_filename)

        with open(destination_path, "wb") as f:
            f.write(contents)

        audio_url = f"/storage/{saved_filename}"
        return audio_url, raw_filename, file_size, mime

    async def save_stream(
        self,
        stream_iterator,
        filename: str,
        content_type: Optional[str] = None,
        max_size_bytes: Optional[int] = None,
    ) -> Tuple[str, str, int, str]:
        raw_filename = filename or "audio.mp3"
        clean_name = sanitize_filename(raw_filename)
        mime = content_type or "audio/mpeg"

        # Validate filename and extension upfront
        if not raw_filename:
            raise ValidationException("Filename cannot be empty.")
        _, ext = os.path.splitext(raw_filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Unsupported audio file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        limit_bytes = max_size_bytes or (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024)
        unique_prefix = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        saved_filename = f"{unique_prefix}_{clean_name}"
        destination_path = os.path.join(self.storage_dir, saved_filename)
        temp_path = destination_path + ".tmp"

        total_bytes = 0
        try:
            with open(temp_path, "wb") as f:
                async for chunk in stream_iterator:
                    if not chunk:
                        continue
                    total_bytes += len(chunk)
                    if total_bytes > limit_bytes:
                        raise ValidationException(
                            f"Streaming file size ({total_bytes / (1024 * 1024):.1f}MB) exceeded maximum limit of {limit_bytes / (1024 * 1024):.0f}MB."
                        )
                    f.write(chunk)

            if total_bytes == 0:
                raise ValidationException("Downloaded audio stream is empty (0 bytes).")

            # Rename temp file to final destination atomically
            os.replace(temp_path, destination_path)
        except Exception:
            # Clean up partial temporary file immediately on error
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

        audio_url = f"/storage/{saved_filename}"
        return audio_url, raw_filename, total_bytes, mime

    def delete_file(self, audio_url: str) -> bool:
        if not audio_url:
            return False
        filename = os.path.basename(audio_url)
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError:
                return False
        return False

    def get_file_path(self, audio_url: str) -> Optional[str]:
        if not audio_url:
            return None
        filename = os.path.basename(audio_url)
        filepath = os.path.join(self.storage_dir, filename)
        return filepath if os.path.exists(filepath) else None

    def file_exists(self, audio_url: str) -> bool:
        path = self.get_file_path(audio_url)
        return path is not None and os.path.exists(path)

# Domain aliases
LocalAudioStorage = LocalStorageService
