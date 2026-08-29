from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from backend.api.dependencies import get_notification_repo, get_current_user_id
from backend.repositories.notification_repo import NotificationRepository
from backend.schemas.notification_schemas import NotificationResponse
from backend.models.notification import Notification
from backend.core.exceptions import NotFoundException

router = APIRouter(prefix="/notifications", tags=["notifications"])

def format_time_ago(dt: datetime) -> str:
    if not dt:
        return "Unknown"
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days > 1 else ''} ago"

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    notification_repo: NotificationRepository = Depends(get_notification_repo),
    user_id: str = Depends(get_current_user_id),
):
    notifs = notification_repo.get_by_user(user_id=user_id, unread_only=unread_only, limit=limit)
    results = []
    for n in notifs:
        resp = NotificationResponse.model_validate(n)
        resp.timestamp = format_time_ago(n.created_at)
        results.append(resp)
    return results

@router.patch("/{id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    id: str,
    notification_repo: NotificationRepository = Depends(get_notification_repo),
    user_id: str = Depends(get_current_user_id),
):
    notif = notification_repo.mark_as_read(id, user_id)
    if not notif:
        raise NotFoundException("Notification", id)
    resp = NotificationResponse.model_validate(notif)
    resp.timestamp = format_time_ago(notif.created_at)
    return resp

@router.post("/read-all")
def mark_all_notifications_read(
    notification_repo: NotificationRepository = Depends(get_notification_repo),
    user_id: str = Depends(get_current_user_id),
):
    count = notification_repo.mark_all_as_read(user_id)
    return {"message": "All notifications marked as read", "count": count}
