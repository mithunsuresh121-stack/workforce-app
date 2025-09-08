from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models.notification import Notification, NotificationStatus
from ..crud_notifications import get_notifications_for_user, mark_notification_as_read
from ..deps import get_current_user
from ..schemas.schemas import NotificationOut

router = APIRouter()

@router.get("/notifications/", response_model=List[NotificationOut])
def get_notifications(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all notifications for the current user"""
    if current_user.company_id is None:
        # SuperAdmin or no company assigned, fetch all notifications for user regardless of company
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc()).all()
    else:
        notifications = get_notifications_for_user(
            db=db,
            user_id=current_user.id,
            company_id=current_user.company_id
        )
    return notifications

@router.post("/notifications/mark-read/{notification_id}")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark a specific notification as read"""
    if current_user.company_id is None:
        # SuperAdmin or no company assigned, mark notification as read without company filter
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        if notification:
            notification.status = NotificationStatus.READ
            db.commit()
            db.refresh(notification)
    else:
        notification = mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id,
            company_id=current_user.company_id
        )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}
