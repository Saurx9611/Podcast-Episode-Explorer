from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# --- Speaker Schemas ---
class SpeakerBase(BaseModel):
    label: str
    display_name: Optional[str] = None
    speaking_duration: float = 0.0
    segment_count: int = 0

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    display_name: Optional[str] = None
    label: Optional[str] = None

class SpeakerResponse(SpeakerBase):
    id: str
    episode_id: str

    model_config = ConfigDict(from_attributes=True)


# --- Transcript Segment Schemas ---
class TranscriptSegmentBase(BaseModel):
    start_time: float
    end_time: float
    text: str
    sequence_number: int
    confidence: Optional[float] = None

class TranscriptSegmentCreate(TranscriptSegmentBase):
    speaker_id: Optional[str] = None

class TranscriptSegmentResponse(TranscriptSegmentBase):
    id: str
    episode_id: str
    speaker_id: Optional[str] = None
    speaker: Optional[SpeakerResponse] = None
    created_at: datetime

    # Convenience formatted properties for frontend
    start: Optional[str] = None
    startSec: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# --- Episode Insight Schemas ---
class EpisodeInsightBase(BaseModel):
    overview: Optional[str] = None
    competencies: List[str] = []
    technologies: List[str] = []
    architecture: List[str] = []
    resume_bullet: Optional[str] = None

class EpisodeInsightCreate(EpisodeInsightBase):
    pass

class EpisodeInsightResponse(EpisodeInsightBase):
    id: str
    episode_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Episode Schemas ---
class EpisodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    language: Optional[str] = "en"
    podcast_id: Optional[str] = None
    guid: Optional[str] = None
    artwork_url: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    publication_date: Optional[datetime] = None

class EpisodeCreate(EpisodeBase):
    project_id: Optional[str] = None

class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    podcast_id: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[float] = None
    language: Optional[str] = None
    artwork_url: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None
    publication_date: Optional[datetime] = None

class EpisodeResponse(EpisodeBase):
    id: str
    project_id: Optional[str] = None
    original_filename: Optional[str] = None
    audio_url: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    status: str
    processing_model: Optional[str] = "whisper-large-v3"
    index_time: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    # Nested relations when requested
    speakers: Optional[List[SpeakerResponse]] = []
    insight: Optional[EpisodeInsightResponse] = None

    # UI presentation fields
    project_name: Optional[str] = None
    podcast_title: Optional[str] = None
    duration_formatted: Optional[str] = None
    file_size_formatted: Optional[str] = None
    date_formatted: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EpisodeUploadResponse(BaseModel):
    id: str
    status: str
    title: str
    message: str = "Episode uploaded and queued for processing."

class EpisodeDownloadResponse(BaseModel):
    id: str
    status: str
    title: str
    audio_url: Optional[str] = None
    file_size: Optional[int] = None
    message: str = "Episode audio downloaded successfully."
