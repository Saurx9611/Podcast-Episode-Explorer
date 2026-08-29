from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .episode_schemas import TranscriptSegmentResponse

class SearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    episode_ids: Optional[List[str]] = []
    speaker_ids: Optional[List[str]] = []
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    limit: int = Field(10, ge=1, le=100)

class SearchResultItem(BaseModel):
    episode_id: str
    episode_title: str
    speaker: Optional[str] = None
    start_time: float
    end_time: float
    text: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]

class SavedSearchBase(BaseModel):
    name: str
    description: Optional[str] = None
    query: str
    filters: List[str] = []

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[List[str]] = None

class SavedSearchResponse(SavedSearchBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    run_count: int = 0
    # For UI mapping
    lastRun: Optional[str] = None
    lastRunDate: Optional[datetime] = None

    class Config:
        from_attributes = True
