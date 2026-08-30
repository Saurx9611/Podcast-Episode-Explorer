import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    podcast_id = Column(String, ForeignKey("podcasts.id", ondelete="CASCADE"), nullable=True, index=True)
    guid = Column(String, nullable=True, index=True)  # RSS unique identifier for deduplication
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    original_filename = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    mime_type = Column(String, nullable=True)
    duration = Column(Float, nullable=True)  # in seconds
    episode_number = Column(Integer, nullable=True)
    season_number = Column(Integer, nullable=True)
    publication_date = Column(DateTime(timezone=True), nullable=True, index=True)
    language = Column(String, default="en")
    status = Column(String, default="uploaded", index=True)  # uploaded, queued, transcribing, speaker_detection, chunking, embedding, indexing, completed, failed
    processing_model = Column(String, default="whisper-large-v3")
    index_time = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="episodes")
    podcast = relationship("Podcast", back_populates="episodes")
    speakers = relationship("Speaker", back_populates="episode", cascade="all, delete-orphan", order_by="Speaker.label")
    transcript_segments = relationship("TranscriptSegment", back_populates="episode", cascade="all, delete-orphan", order_by="TranscriptSegment.sequence_number")
    processing_jobs = relationship("ProcessingJob", back_populates="episode", cascade="all, delete-orphan", order_by="ProcessingJob.started_at.desc()")
    insight = relationship("EpisodeInsight", back_populates="episode", uselist=False, cascade="all, delete-orphan")

