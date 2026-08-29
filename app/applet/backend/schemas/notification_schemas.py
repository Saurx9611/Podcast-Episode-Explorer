from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    read: bool = False

class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    created_at: datetime
    timestamp: Optional[str] = None # For UI mapping, e.g. "2 min ago"

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    read: bool
