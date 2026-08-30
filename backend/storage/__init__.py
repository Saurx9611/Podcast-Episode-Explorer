from .base import BaseStorageService, AudioStorageService
from .local_storage import LocalStorageService, LocalAudioStorage

# Default singleton instance for local filesystem storage
storage_service: BaseStorageService = LocalStorageService()

__all__ = [
    "BaseStorageService",
    "AudioStorageService",
    "LocalStorageService",
    "LocalAudioStorage",
    "storage_service",
]
