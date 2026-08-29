from sqlalchemy import Column, String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False)
    status = Column(String, default="queued") # queued, processing, completed, failed
    current_stage = Column(String, default="uploading") # uploading, transcription, speaker_detection, chunking, embedding, indexing, complete
    progress = Column(Integer, default=0)
    error_message = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    episode = relationship("Episode", back_populates="processing_jobs")
