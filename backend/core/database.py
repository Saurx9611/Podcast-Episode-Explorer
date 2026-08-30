import logging
from typing import Generator
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import settings

logger = logging.getLogger("backend.core.database")

# Engine configuration with pooling
engine_kwargs = {}
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initializes the database, creating the vector extension if running PostgreSQL and applying column updates."""
    try:
        with engine.connect() as conn:
            if conn.dialect.name == "postgresql":
                logger.info("Ensuring pgvector extension is enabled on PostgreSQL...")
                conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
        Base.metadata.create_all(bind=engine)

        # Check and add missing columns to ensure backward compatibility across local databases
        with engine.connect() as conn:
            inspector = sa.inspect(engine)
            if "episodes" in inspector.get_table_names():
                existing_cols = {c["name"] for c in inspector.get_columns("episodes")}
                columns_to_add = [
                    ("podcast_id", "VARCHAR"),
                    ("guid", "VARCHAR"),
                    ("artwork_url", "VARCHAR"),
                    ("episode_number", "INTEGER"),
                    ("season_number", "INTEGER"),
                    ("publication_date", "DATETIME" if conn.dialect.name == "sqlite" else "TIMESTAMP WITH TIME ZONE"),
                ]
                for col_name, col_type in columns_to_add:
                    if col_name not in existing_cols:
                        logger.info(f"Adding missing column {col_name} to episodes table...")
                        try:
                            conn.execute(sa.text(f"ALTER TABLE episodes ADD COLUMN {col_name} {col_type};"))
                            conn.commit()
                        except Exception as col_err:
                            logger.warning(f"Could not add column {col_name}: {col_err}")

            if conn.dialect.name == "postgresql":
                logger.info("Ensuring pgvector HNSW index is created on embeddings table...")
                try:
                    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_embeddings_hnsw ON embeddings USING hnsw (embedding vector_cosine_ops);"))
                    conn.commit()
                except Exception as idx_err:
                    logger.warning(f"Notice on HNSW index creation: {idx_err}")

        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")

def get_db() -> Generator:
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

