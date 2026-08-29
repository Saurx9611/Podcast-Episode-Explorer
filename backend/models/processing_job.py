import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="queued", index=True)  # queued, processing, completed, failed
    current_stage = Column(String, default="upload")  # upload, transcription, speaker_detection, chunking, embedding, indexing, complete
    progress = Column(Integer, default=0)  # 0 to 100
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    episode = relationship("Episode", back_populates="processing_jobs")
