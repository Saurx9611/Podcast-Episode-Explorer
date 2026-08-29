import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    query = Column(String, nullable=False)
    filters = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    run_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="saved_searches")
