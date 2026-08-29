from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api.dependencies import get_db
from backend.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if "disconnected" not in db_status else "unhealthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
