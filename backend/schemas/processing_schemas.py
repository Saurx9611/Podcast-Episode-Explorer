from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProcessingJobBase(BaseModel):
    status: str = "queued"
    current_stage: str = "upload"
    progress: int = 0
    error_message: Optional[str] = None

class ProcessingJobCreate(ProcessingJobBase):
    episode_id: str

class ProcessingJobUpdate(BaseModel):
    status: Optional[str] = None
    current_stage: Optional[str] = None
    progress: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

class ProcessingJobResponse(ProcessingJobBase):
    id: str
    episode_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    # UI presentation fields
    episode_title: Optional[str] = None
    started_formatted: Optional[str] = None
    duration_formatted: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
