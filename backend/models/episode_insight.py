import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class EpisodeInsight(Base):
    __tablename__ = "episode_insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    overview = Column(Text, nullable=True)
    competencies = Column(JSON, default=list)  # List[str]
    technologies = Column(JSON, default=list)  # List[str]
    architecture = Column(JSON, default=list)  # List[str]
    resume_bullet = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    episode = relationship("Episode", back_populates="insight")
