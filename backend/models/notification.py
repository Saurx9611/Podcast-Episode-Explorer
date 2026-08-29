import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)  # processing_complete, processing_failed, processing_started, saved_search, transcript_indexed, system
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    link = Column(String, nullable=True)
    read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    user = relationship("User", back_populates="notifications")
