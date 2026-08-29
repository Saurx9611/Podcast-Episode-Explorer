import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, default="Engineer")
    avatar_url = Column(String, nullable=True)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
