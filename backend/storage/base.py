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
    def delete_file(self, audio_url: str) -> bool:
        """Deletes the stored file by URL or storage key."""
        pass

    @abstractmethod
    def get_file_path(self, audio_url: str) -> Optional[str]:
        """Returns the local filesystem path if available."""
        pass
