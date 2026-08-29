import os
from fastapi import UploadFile
from backend.core.config import settings

class AudioStorageService:
    @staticmethod
    def save_file(file: UploadFile) -> tuple[str, int, str]:
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        file_path = os.path.join(settings.STORAGE_PATH, file.filename)
        
        # Read file to get size and save it
        content = file.file.read()
        size = len(content)
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        return f"/mock/storage/{file.filename}", size, file.content_type
