import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    publisher = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    language = Column(String, default="en")
    feed_url = Column(String, nullable=True, unique=True, index=True)
    website_url = Column(String, nullable=True)
    external_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    episodes = relationship("Episode", back_populates="podcast", cascade="all, delete-orphan", order_by="Episode.created_at.desc()")
