from typing import Generator
from backend.core.database import SessionLocal

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# For a real app, this would verify JWT tokens or sessions
# For this preview, we'll return a stub user ID (or the first user)
def get_current_user_id(db = None) -> str:
    # Hardcoded stub user ID for development
    return "dev-user-id"
