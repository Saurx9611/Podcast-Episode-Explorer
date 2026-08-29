import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base
from pgvector.sqlalchemy import Vector
from backend.core.config import settings

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String, ForeignKey("transcript_segments.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    # Vector column using pgvector with configured dimension (default: 1536)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION).with_variant(JSON, "sqlite"), nullable=False)

    # Relationships
    segment = relationship("TranscriptSegment", back_populates="embedding")
