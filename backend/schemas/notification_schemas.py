from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    type: str  # processing_complete, processing_failed, processing_started, saved_search, transcript_indexed, system
    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    read: bool = False

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationUpdate(BaseModel):
    read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    created_at: datetime
    timestamp: Optional[str] = None  # Formatted for UI, e.g., "2 min ago"

    model_config = ConfigDict(from_attributes=True)
