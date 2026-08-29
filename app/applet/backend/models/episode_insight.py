from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class EpisodeInsight(Base):
    __tablename__ = "episode_insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False, unique=True)
    overview = Column(String)
    competencies = Column(JSONB, default=list)
    technologies = Column(JSONB, default=list)
    architecture = Column(JSONB, default=list)
    resume_bullet = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    episode = relationship("Episode", back_populates="insight")
