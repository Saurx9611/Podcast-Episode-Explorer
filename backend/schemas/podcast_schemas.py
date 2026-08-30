from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PodcastBase(BaseModel):
    title: str
    description: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    artwork_url: Optional[str] = None
    language: Optional[str] = "en"
    feed_url: Optional[str] = None
    website_url: Optional[str] = None
    external_id: Optional[str] = None

class PodcastCreate(PodcastBase):
    pass

class PodcastUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    artwork_url: Optional[str] = None
    language: Optional[str] = None
    feed_url: Optional[str] = None
    website_url: Optional[str] = None
    external_id: Optional[str] = None

class PodcastResponse(PodcastBase):
    id: str
    created_at: datetime
    updated_at: datetime
    episode_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class PodcastListResponse(BaseModel):
    items: List[PodcastResponse]
    total: int

class PodcastImportRequest(BaseModel):
    feed_url: str
    project_id: Optional[str] = None

class PodcastImportResponse(BaseModel):
    podcast: PodcastResponse
    total_episodes_in_feed: int
    new_episodes_imported: int
    updated_episodes: int
    message: str = "Podcast feed imported successfully."
