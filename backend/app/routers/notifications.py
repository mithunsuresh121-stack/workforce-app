from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud_announcements import (create_announcement,
                                    get_announcements_for_company)
from app.crud_notifications import (get_notifications_for_user,
                                    mark_notification_as_read)
from app.db import get_db
from app.deps import get_current_user
from app.models.announcement import Announcement
from app.models.notification import Notification, NotificationStatus
from app.schemas.schemas import (AnnouncementCreate, AnnouncementOut,
                                 NotificationOut)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/notifications/", response_model=List[NotificationOut])
async def get_notifications(
    type: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get notifications for the current user with caching and pagination"""
    import json

    from app.services.redis_service import redis_service

    # Validate pagination parameters
    if limit < 1:
        limit = 50
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    company_id = current_user.company_id or 0  # Use 0 for superadmin

    # Try to get from cache first
    cached_notifications = await redis_service.get_notification_cache(
        company_id, current_user.id, offset, limit
    )
    if cached_notifications:
        logger.info(
            "Serving notifications from cache",
            user_id=current_user.id,
            offset=offset,
            limit=limit,
        )
        return cached_notifications

    # Cache miss - fetch from database
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if company_id != 0:
        query = query.filter(Notification.company_id == company_id)

    if type:
        query = query.filter(Notification.type == type)

    notifications = (
        query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    )

    # Convert to dict for caching
    notifications_dict = [
        {
            "id": n.id,
            "user_id": n.user_id,
            "company_id": n.company_id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "status": n.status.value if hasattr(n.status, "value") else str(n.status),
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in notifications
    ]

    # Cache the results
    await redis_service.set_notification_cache(
        company_id, current_user.id, offset, limit, notifications_dict
    )

    logger.info(
        "Serving notifications from database",
        user_id=current_user.id,
        offset=offset,
        limit=limit,
    )
    return notifications


@router.post("/notifications/mark-read/{notification_id}")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Mark a specific notification as read"""
    if current_user.company_id is None:
        # SuperAdmin or no company assigned, mark notification as read without company filter
        notification = (
            db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
            )
            .first()
        )
        if notification:
            notification.status = NotificationStatus.READ
            db.commit()
            db.refresh(notification)
    else:
        notification = mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id,
            company_id=current_user.company_id,
        )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.post("/announce", response_model=AnnouncementOut)
def create_announcement_endpoint(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Admin-only
    if current_user.role not in ["SUPERADMIN", "CompanyAdmin"]:
        raise HTTPException(
            status_code=403, detail="Only admins can create announcements"
        )

    return create_announcement(
        db, announcement, current_user.company_id, current_user.id
    )


@router.get("/list", response_model=List[AnnouncementOut])
def list_announcements(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return get_announcements_for_company(db, current_user.company_id)


@router.post("/publish")
async def publish_to_redis(
    channel: str, message: str, current_user=Depends(get_current_user)
):
    """Publish message to Redis pub/sub channel for testing"""
    from fastapi import Request

    from app.services.redis_service import redis_service

    # Log request metadata
    logger.info(
        "Publishing to Redis",
        method="POST",
        path="/api/notifications/publish",
        channel=channel,
        user_id=current_user.id,
    )

    # Publish to Redis
    await redis_service.publish(channel, message)

    return {"status": "published", "channel": channel}


@router.post("/notification-preferences")
def save_notification_preferences(
    preferences: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Save user notification preferences"""
    # For now, just log and return success (can be extended to store in user model or separate table)
    logger.info(
        "Saving notification preferences",
        user_id=current_user.id,
        preferences=preferences,
    )
    return {"message": "Notification preferences saved successfully"}
