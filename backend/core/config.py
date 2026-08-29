import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Podcast Explorer Backend"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "podcast_explorer"
    DATABASE_URL: Union[str, None] = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://").replace("postgresql://", "postgresql+asyncpg://")
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # File Storage
    STORAGE_PATH: str = "./audio_storage"
    MAX_UPLOAD_SIZE_MB: int = 250
    ALLOWED_MIME_TYPES: List[str] = [
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/m4a",
        "audio/x-m4a",
        "audio/mp4",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
    ]

    # Embedding & AI
    EMBEDDING_DIMENSION: int = 1536
    DEFAULT_TRANSCRIPTION_MODEL: str = "whisper-large-v3"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Optional External AI API Keys
    OPENAI_API_KEY: Union[str, None] = None
    GEMINI_API_KEY: Union[str, None] = None
    ANTHROPIC_API_KEY: Union[str, None] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

settings = Settings()
