from abc import ABC, abstractmethod
from typing import Tuple, Optional
from fastapi import UploadFile

class BaseStorageService(ABC):
    """Abstract interface for audio file storage (local, S3, GCS)."""

    @abstractmethod
    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        """
        Saves an uploaded audio file.
        Returns:
            audio_url: str (access URL or storage key)
            saved_filename: str
            file_size: int (bytes)
            mime_type: str
        """
        pass

    @abstractmethod
    def save_bytes(self, contents: bytes, filename: str, content_type: Optional[str] = None) -> Tuple[str, str, int, str]:
        """
        Saves raw audio bytes (e.g. downloaded from RSS podcast feeds).
        Returns:
            audio_url: str (access URL or storage key)
            saved_filename: str
            file_size: int (bytes)
            mime_type: str
        """
        pass

    @abstractmethod
    async def save_stream(
        self,
        stream_iterator,
        filename: str,
        content_type: Optional[str] = None,
        max_size_bytes: Optional[int] = None,
    ) -> Tuple[str, str, int, str]:
        """
        Saves audio from an async chunked byte stream directly to storage without memory buffering.
        Returns:
            audio_url: str (access URL or storage key)
            saved_filename: str
            file_size: int (bytes)
            mime_type: str
        """
        pass

    @abstractmethod
    def delete_file(self, audio_url: str) -> bool:
        """Deletes the stored file by URL or storage key."""
        pass

    @abstractmethod
    def get_file_path(self, audio_url: str) -> Optional[str]:
        """Returns the local filesystem path if available."""
        pass

    @abstractmethod
    def file_exists(self, audio_url: str) -> bool:
        """Checks if a file exists at the given audio URL or key."""
        pass

# Alias for standard domain terminology
AudioStorageService = BaseStorageService
