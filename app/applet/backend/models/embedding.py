from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base
from pgvector.sqlalchemy import Vector
import uuid

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String, ForeignKey("transcript_segments.id"), nullable=False, unique=True)
    # Using a common dimension for embeddings (e.g. OpenAI ada-002 is 1536, some local models are 384)
    # We will use 1536 as a default compatible with popular models
    embedding = Column(Vector(1536), nullable=False)

    segment = relationship("TranscriptSegment", back_populates="embedding")
