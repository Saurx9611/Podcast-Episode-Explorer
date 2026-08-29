from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False, index=True)
    speaker_id = Column(String, ForeignKey("speakers.id"), nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(String, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    episode = relationship("Episode", back_populates="transcript_segments")
    speaker = relationship("Speaker", back_populates="transcript_segments")
    embedding = relationship("Embedding", back_populates="segment", uselist=False, cascade="all, delete-orphan")
