from typing import List, Optional

from sqlalchemy.orm import Session
from structlog import get_logger

from app.models.notification import Notification, NotificationStatus
from app.services.email_service import email_service
from app.services.fcm_service import fcm_service

logger = get_logger()


def get_notifications_for_user(
    db: Session, user_id: int, company_id: int
) -> List[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.company_id == company_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def mark_notification_as_read(
    db: Session, notification_id: int, user_id: int, company_id: int
) -> Optional[Notification]:
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.company_id == company_id,
        )
        .first()
    )
    if notification:
        notification.status = NotificationStatus.READ
        db.commit()
        db.refresh(notification)

        # Invalidate cache for this user to ensure fresh data on next fetch
        import asyncio

        from app.services.redis_service import redis_service

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                redis_service.invalidate_notification_cache(company_id, user_id)
            )
        except RuntimeError:
            # No running event loop, skip async operation
            pass

    return notification


def create_notification(
    db: Session, user_id: int, company_id: int, title: str, message: str, type: str
) -> Optional[Notification]:
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
        status=NotificationStatus.UNREAD,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Send push notification if user has FCM token and push is enabled
    if notification:
        _send_push_notification_if_enabled(
            db, user_id, company_id, notification.id, title, message, type
        )
        # Send email notification if enabled
        _send_email_notification_if_enabled(
            db, user_id, notification.id, title, message, type
        )

        # Invalidate cache for this user to ensure fresh data includes new notification
        import asyncio

        from app.services.redis_service import redis_service

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                redis_service.invalidate_notification_cache(company_id, user_id)
            )
        except RuntimeError:
            # No running event loop, skip async operation
            pass

    return notification


def _send_push_notification_if_enabled(
    db: Session,
    user_id: int,
    company_id: int,
    notification_id: int,
    title: str,
    message: str,
    notification_type: str,
):
    """Send push notification if user has FCM token and push notifications are enabled"""
    try:
        # Get user's FCM token
        fcm_token = fcm_service.get_user_fcm_token(db, user_id)
        if not fcm_token:
            return  # No FCM token, skip push notification

        # Check if push notifications are enabled for this user and notification type
        from app.crud_notification_preferences import \
            should_send_push_notification

        if not should_send_push_notification(
            db, user_id, company_id, notification_type
        ):
            return  # Push notifications disabled for this type

        # Send push notification
        data = {
            "notification_id": str(notification_id),
            "type": notification_type,
            "user_id": str(user_id),
        }

        success = fcm_service.send_push_notification(fcm_token, title, message, data)
        if success:
            logger.info(
                "Push notification sent", user_id=user_id, type=notification_type
            )
        else:
            logger.warning(
                "Failed to send push notification",
                user_id=user_id,
                type=notification_type,
            )

    except Exception as e:
        logger.error("Error sending push notification", user_id=user_id, error=str(e))


def _send_email_notification_if_enabled(
    db: Session,
    user_id: int,
    notification_id: int,
    title: str,
    message: str,
    notification_type: str,
):
    """Send email notification if user has email notifications enabled"""
    try:
        # Get user email
        from app.models.user import User

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            return  # No email available

        # Check if email notifications are enabled for this user and notification type
        from app.crud_notification_preferences import \
            should_send_email_notification

        if not should_send_email_notification(
            db, user_id, user.company_id, notification_type
        ):
            return  # Email notifications disabled for this type

        # Send email notification with user name
        user_name = user.full_name or user.email
        success = email_service.send_notification_email(
            user.email, title, message, user_name
        )
        if success:
            logger.info(
                "Email notification sent", user_id=user_id, type=notification_type
            )
        else:
            logger.warning(
                "Failed to send email notification",
                user_id=user_id,
                type=notification_type,
            )

    except Exception as e:
        logger.error("Error sending email notification", user_id=user_id, error=str(e))
