from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    query = Column(String, nullable=False)
    filters = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)

    user = relationship("User", back_populates="saved_searches")
