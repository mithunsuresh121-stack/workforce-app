import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..models.notification import Notification, NotificationStatus
from ..models.announcement import Announcement
from ..crud_notifications import get_notifications_for_user, mark_notification_as_read
from ..crud_announcements import create_announcement, get_announcements_for_company
from ..deps import get_current_user
from ..schemas.schemas import NotificationOut, AnnouncementCreate, AnnouncementOut

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/notifications/", response_model=List[NotificationOut])
def get_notifications(
    type: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all notifications for the current user, optionally filtered by type"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if current_user.company_id is not None:
        query = query.filter(Notification.company_id == current_user.company_id)

    if type:
        query = query.filter(Notification.type == type)

    notifications = query.order_by(Notification.created_at.desc()).all()
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

@router.post("/announce", response_model=AnnouncementOut)
def create_announcement_endpoint(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Admin-only
    if current_user.role not in ["SUPERADMIN", "CompanyAdmin"]:
        raise HTTPException(status_code=403, detail="Only admins can create announcements")

    return create_announcement(db, announcement, current_user.company_id, current_user.id)

@router.get("/list", response_model=List[AnnouncementOut])
def list_announcements(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_announcements_for_company(db, current_user.company_id)
