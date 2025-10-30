from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationStatus
from app.services.fcm_service import fcm_service
from typing import List, Optional
from structlog import get_logger

logger = get_logger()

def get_notifications_for_user(db: Session, user_id: int, company_id: int) -> List[Notification]:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.company_id == company_id
    ).order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(db: Session, notification_id: int, user_id: int, company_id: int) -> Optional[Notification]:
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id,
        Notification.company_id == company_id
    ).first()
    if notification:
        notification.status = NotificationStatus.READ
        db.commit()
        db.refresh(notification)
    return notification

def create_notification(db: Session, user_id: int, company_id: int, title: str, message: str, type: str) -> Optional[Notification]:
    # Check user preferences before creating notification
    from app.crud_notification_preferences import should_send_notification
    if not should_send_notification(db, user_id, company_id, type):
        return None  # User has disabled this type of notification

    notification = Notification(
        user_id=user_id,
        company_id=company_id,
        title=title,
        message=message,
        type=type,
        status=NotificationStatus.UNREAD
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Send push notification if user has FCM token and push is enabled
    if notification:
        _send_push_notification_if_enabled(db, user_id, company_id, notification.id, title, message, type)

    return notification

def _send_push_notification_if_enabled(db: Session, user_id: int, company_id: int, notification_id: int, title: str, message: str, notification_type: str):
    """Send push notification if user has FCM token and push notifications are enabled"""
    try:
        # Get user's FCM token
        fcm_token = fcm_service.get_user_fcm_token(db, user_id)
        if not fcm_token:
            return  # No FCM token, skip push notification

        # Check if push notifications are enabled for this user and notification type
        from app.crud_notification_preferences import should_send_push_notification
        if not should_send_push_notification(db, user_id, company_id, notification_type):
            return  # Push notifications disabled for this type

        # Send push notification
        data = {
            "notification_id": str(notification_id),
            "type": notification_type,
            "user_id": str(user_id)
        }

        success = fcm_service.send_push_notification(fcm_token, title, message, data)
        if success:
            logger.info("Push notification sent", user_id=user_id, type=notification_type)
        else:
            logger.warning("Failed to send push notification", user_id=user_id, type=notification_type)

    except Exception as e:
        logger.error("Error sending push notification", user_id=user_id, error=str(e))
