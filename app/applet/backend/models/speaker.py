from sqlalchemy import Column, String, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base
import uuid

class Speaker(Base):
    __tablename__ = "speakers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    episode_id = Column(String, ForeignKey("episodes.id"), nullable=False)
    label = Column(String, nullable=False)
    display_name = Column(String)
    speaking_duration = Column(Float, default=0.0)
    segment_count = Column(Integer, default=0)

    episode = relationship("Episode", back_populates="speakers")
    transcript_segments = relationship("TranscriptSegment", back_populates="speaker")
