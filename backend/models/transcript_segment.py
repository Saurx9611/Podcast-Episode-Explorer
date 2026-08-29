import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id = Column(String, ForeignKey("speakers.id", ondelete="SET NULL"), nullable=True, index=True)
    start_time = Column(Float, nullable=False, index=True)  # in seconds (e.g. 112.4)
    end_time = Column(Float, nullable=False)    # in seconds (e.g. 138.8)
    text = Column(Text, nullable=False)
    sequence_number = Column(Integer, nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    episode = relationship("Episode", back_populates="transcript_segments")
    speaker = relationship("Speaker", back_populates="transcript_segments")
    embedding = relationship("Embedding", back_populates="segment", uselist=False, cascade="all, delete-orphan")
