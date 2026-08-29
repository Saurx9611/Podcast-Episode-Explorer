from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime
import uuid

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    link = Column(String)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
