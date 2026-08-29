from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.api.dependencies import get_db, get_current_user_id
from backend.schemas.notification_schemas import NotificationResponse, NotificationUpdate
from backend.models import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

@router.patch("/{id}/read", response_model=NotificationResponse)
def mark_read(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    notif = db.query(Notification).filter(Notification.id == id, Notification.user_id == user_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.read = True
    db.commit()
    db.refresh(notif)
    return notif

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    db.query(Notification).filter(Notification.user_id == user_id, Notification.read == False).update({"read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
