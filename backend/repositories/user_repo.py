from typing import Optional, List
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.repositories.base_repo import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_or_create_default_user(self) -> User:
        user = self.get_by_id("dev-user-id")
        if not user:
            user = self.get_by_email("dev@example.com")
        if not user:
            user = User(
                id="dev-user-id",
                email="dev@example.com",
                name="Engineering Lead",
                role="Engineer",
                preferences={
                    "playback_speed": "1.0x",
                    "chunk_duration": 45,
                    "overlap": 10,
                    "transcription_model": "Whisper Large v3",
                    "similarity_threshold": 0.70,
                }
            )
            self.create(user)
        return user
