from .base import BaseStorageService
from .local_storage import LocalStorageService

# Default singleton instance for local filesystem storage
storage_service: BaseStorageService = LocalStorageService()

__all__ = ["BaseStorageService", "LocalStorageService", "storage_service"]
