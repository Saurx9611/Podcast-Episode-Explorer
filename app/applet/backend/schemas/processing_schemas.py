from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProcessingJobResponse(BaseModel):
    id: str
    episode_id: str
    status: str
    current_stage: str
    progress: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Convenience field for frontend
    episode_title: Optional[str] = None

    class Config:
        from_attributes = True
