from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .project_schemas import ProjectResponse

class SpeakerBase(BaseModel):
    label: str
    display_name: Optional[str] = None
    speaking_duration: float = 0.0
    segment_count: int = 0

class SpeakerResponse(SpeakerBase):
    id: str
    episode_id: str

    class Config:
        from_attributes = True

class TranscriptSegmentBase(BaseModel):
    start_time: float
    end_time: float
    text: str
    sequence_number: int
    confidence: Optional[float] = None

class TranscriptSegmentResponse(TranscriptSegmentBase):
    id: str
    episode_id: str
    speaker_id: Optional[str] = None
    speaker: Optional[SpeakerResponse] = None

    class Config:
        from_attributes = True

class EpisodeInsightBase(BaseModel):
    overview: Optional[str] = None
    competencies: List[str] = []
    technologies: List[str] = []
    architecture: List[str] = []
    resume_bullet: Optional[str] = None

class EpisodeInsightResponse(EpisodeInsightBase):
    id: str
    episode_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = None

class EpisodeCreate(EpisodeBase):
    project_id: Optional[str] = None

class EpisodeResponse(EpisodeBase):
    id: str
    project_id: Optional[str] = None
    original_filename: Optional[str] = None
    audio_url: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EpisodeUploadResponse(BaseModel):
    id: str
    status: str
