from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.notification_preferences import NotificationPreferences


def get_user_preferences(
    db: Session, user_id: int, company_id: int
) -> Optional[NotificationPreferences]:
    """Get notification preferences for a user"""
    return (
        db.query(NotificationPreferences)
        .filter(
            NotificationPreferences.user_id == user_id,
            NotificationPreferences.company_id == company_id,
        )
        .first()
    )


def create_user_preferences(
    db: Session, user_id: int, company_id: int, preferences: Dict[str, Any] = None
) -> NotificationPreferences:
    """Create notification preferences for a user"""
    if preferences is None:
        preferences = {
            "mute_all": False,
            "digest_mode": "immediate",
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": True,
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": True,
            },
        }

    db_preferences = NotificationPreferences(
        user_id=user_id, company_id=company_id, preferences=preferences
    )
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences


def update_user_preferences(
    db: Session, user_id: int, company_id: int, preferences: Dict[str, Any]
) -> Optional[NotificationPreferences]:
    """Update notification preferences for a user"""
    db_preferences = get_user_preferences(db, user_id, company_id)
    if db_preferences:
        db_preferences.preferences = preferences
        db.commit()
        db.refresh(db_preferences)
    return db_preferences


def delete_user_preferences(db: Session, user_id: int, company_id: int) -> bool:
    """Delete notification preferences for a user"""
    db_preferences = get_user_preferences(db, user_id, company_id)
    if db_preferences:
        db.delete(db_preferences)
        db.commit()
        return True
    return False


def get_or_create_user_preferences(
    db: Session, user_id: int, company_id: int
) -> NotificationPreferences:
    """Get existing preferences or create default ones for a user"""
    preferences = get_user_preferences(db, user_id, company_id)
    if not preferences:
        preferences = create_user_preferences(db, user_id, company_id)
    return preferences


def should_send_notification(
    db: Session, user_id: int, company_id: int, notification_type: str
) -> bool:
    """Check if a notification should be sent based on user preferences"""
    preferences = get_user_preferences(db, user_id, company_id)
    if not preferences:
        return True  # Default to sending if no preferences set

    prefs = preferences.preferences

    # Check if all notifications are muted
    if prefs.get("mute_all", False):
        return False

    # Check digest mode - for this phase, only send if immediate
    digest_mode = prefs.get("digest_mode", "immediate")
    if digest_mode != "immediate":
        return False  # Defer to digest scheduling (not implemented yet)

    # Check if this notification type is enabled
    notification_types = prefs.get("notification_types", {})
    return notification_types.get(notification_type, True)


def should_send_push_notification(
    db: Session, user_id: int, company_id: int, notification_type: str
) -> bool:
    """Check if a push notification should be sent based on user preferences"""
    # Get user preferences (company_id needed for consistency with other methods)
    from app.models.notification_preferences import NotificationPreferences

    preferences = (
        db.query(NotificationPreferences)
        .filter(
            NotificationPreferences.user_id == user_id,
            NotificationPreferences.company_id == company_id,
        )
        .first()
    )

    if not preferences:
        return True  # Default to sending push if no preferences set

    prefs = preferences.preferences

    # Check if push notifications are enabled globally
    if not prefs.get("push_enabled", True):
        return False

    # Check if all notifications are muted
    if prefs.get("mute_all", False):
        return False

    # Check if this notification type is enabled
    notification_types = prefs.get("notification_types", {})
    return notification_types.get(notification_type, True)


def should_send_email_notification(
    db: Session, user_id: int, company_id: int, notification_type: str
) -> bool:
    """Check if an email notification should be sent based on user preferences"""
    preferences = get_user_preferences(db, user_id, company_id)
    if not preferences:
        return False  # Default to not sending email if no preferences set

    prefs = preferences.preferences

    # Check if email notifications are enabled globally
    if not prefs.get("email_enabled", False):
        return False

    # Check if all notifications are muted
    if prefs.get("mute_all", False):
        return False

    # Check if this notification type is enabled
    notification_types = prefs.get("notification_types", {})
    return notification_types.get(notification_type, False)
