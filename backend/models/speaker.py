import uuid
from sqlalchemy import Column, String, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Speaker(Base):
    __tablename__ = "speakers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String, nullable=False)  # e.g., "Speaker 1"
    display_name = Column(String, nullable=True)  # e.g., "Alex Morgan"
    speaking_duration = Column(Float, default=0.0)  # total seconds
    segment_count = Column(Integer, default=0)

    # Relationships
    episode = relationship("Episode", back_populates="speakers")
    transcript_segments = relationship("TranscriptSegment", back_populates="speaker")
