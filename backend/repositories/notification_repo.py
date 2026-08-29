from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.notification import Notification
from backend.repositories.base_repo import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(Notification, db)

    def get_by_user(self, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        q = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            q = q.filter(Notification.read == False)
        return q.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, user_id: str) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.read == False)
            .count()
        )

    def mark_as_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        notif = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if not notif:
            return None
        notif.read = True
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def mark_all_as_read(self, user_id: str) -> int:
        count = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.read == False)
            .update({"read": True})
        )
        self.db.commit()
        return count
