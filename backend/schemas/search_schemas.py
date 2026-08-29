from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# --- Semantic Search Schemas ---
class SearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    episode_ids: Optional[List[str]] = None
    speaker_ids: Optional[List[str]] = None
    similarity_threshold: float = Field(0.5, ge=0.0, le=1.0)
    limit: int = Field(10, ge=1, le=100)

class SearchResultItem(BaseModel):
    id: str
    episode_id: str
    episode_title: str
    project: Optional[str] = None
    speaker: Optional[str] = None
    speaker_color: Optional[str] = None
    start_time: float
    end_time: float
    timestamp: str  # e.g. "18:42"
    time_sec: float  # e.g. 1122
    text: str
    highlight: Optional[str] = None
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    score: float  # e.g. 0.98
    match_score: int  # e.g. 98

class SearchResponse(BaseModel):
    query: str
    total_matches: int
    execution_time_ms: float
    results: List[SearchResultItem]


# --- Saved Search Schemas ---
class SavedSearchBase(BaseModel):
    name: str
    description: Optional[str] = None
    query: str
    filters: List[Any] = []

class SavedSearchCreate(SavedSearchBase):
    pass

class SavedSearchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[List[Any]] = None

class SavedSearchResponse(SavedSearchBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    last_run_at: Optional[datetime] = None
    run_count: int = 0
    
    # UI formatted properties
    last_run_formatted: Optional[str] = "Never"

    model_config = ConfigDict(from_attributes=True)
