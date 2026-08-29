from typing import Generator
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, get_db
from backend.repositories.user_repo import UserRepository
from backend.repositories.project_repo import ProjectRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.search_repo import SearchRepository
from backend.repositories.processing_repo import ProcessingRepository
from backend.repositories.notification_repo import NotificationRepository

def get_current_user_id(x_user_id: str = Header(default="dev-user-id")) -> str:
    """Returns current user id. In dev/single-tenant mode, defaults to dev-user-id."""
    return x_user_id

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_project_repo(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

def get_episode_repo(db: Session = Depends(get_db)) -> EpisodeRepository:
    return EpisodeRepository(db)

def get_search_repo(db: Session = Depends(get_db)) -> SearchRepository:
    return SearchRepository(db)

def get_processing_repo(db: Session = Depends(get_db)) -> ProcessingRepository:
    return ProcessingRepository(db)

def get_notification_repo(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)
