from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String)
    original_filename = Column(String)
    audio_url = Column(String)
    mime_type = Column(String)
    file_size = Column(Integer)
    duration = Column(Float)
    status = Column(String, default="uploaded")
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime)

    project = relationship("Project", back_populates="episodes")
    speakers = relationship("Speaker", back_populates="episode", cascade="all, delete-orphan")
    transcript_segments = relationship("TranscriptSegment", back_populates="episode", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="episode", cascade="all, delete-orphan")
    insight = relationship("EpisodeInsight", back_populates="episode", uselist=False, cascade="all, delete-orphan")
