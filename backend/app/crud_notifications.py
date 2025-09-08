from sqlalchemy.orm import Session
from .models.notification import Notification, NotificationStatus
from typing import List, Optional

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
    from .crud_notification_preferences import should_send_notification
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
    return notification
