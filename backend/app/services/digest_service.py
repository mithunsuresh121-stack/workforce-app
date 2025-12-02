from datetime import datetime, timedelta
from typing import Any, Dict, List

import structlog
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.notification_digest import (DigestStatus, DigestType,
                                            NotificationDigest)
from app.models.notification_preferences import (DigestMode,
                                                 NotificationPreferences)
from app.models.user import User

logger = structlog.get_logger(__name__)


class DigestService:
    def __init__(self, db: Session):
        self.db = db

    def create_daily_digest(
        self, user_id: int, company_id: int = None
    ) -> NotificationDigest:
        """Create a daily digest for a user"""
        # Get notifications from the last 24 hours that should be included in digest
        yesterday = datetime.utcnow() - timedelta(days=1)

        notifications = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.created_at >= yesterday,
                    Notification.status == "unread",
                )
            )
            .all()
        )

        if not notifications:
            return None

        # Group notifications by type
        type_counts = {}
        for notification in notifications:
            type_counts[notification.type.value] = (
                type_counts.get(notification.type.value, 0) + 1
            )

        # Create digest summary
        total_count = len(notifications)
        summary = f"You have {total_count} new notifications from the last 24 hours:\n"
        for notif_type, count in type_counts.items():
            summary += f"- {count} {notif_type.replace('_', ' ').lower()}\n"

        # Create digest record
        digest = NotificationDigest(
            user_id=user_id,
            company_id=company_id,
            digest_type=DigestType.DAILY,
            status=DigestStatus.PENDING,
            title="Daily Notification Digest",
            summary=summary,
            notification_count=total_count,
            notification_ids=[n.id for n in notifications],
            scheduled_for=datetime.utcnow() + timedelta(hours=1),  # Send in 1 hour
        )

        self.db.add(digest)
        self.db.commit()
        self.db.refresh(digest)

        logger.info(
            f"Created daily digest for user {user_id} with {total_count} notifications"
        )
        return digest

    def create_weekly_digest(
        self, user_id: int, company_id: int = None
    ) -> NotificationDigest:
        """Create a weekly digest for a user"""
        # Get notifications from the last 7 days
        last_week = datetime.utcnow() - timedelta(days=7)

        notifications = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.created_at >= last_week,
                    Notification.status == "unread",
                )
            )
            .all()
        )

        if not notifications:
            return None

        # Group notifications by type and day
        daily_counts = {}
        for notification in notifications:
            day = notification.created_at.date()
            if day not in daily_counts:
                daily_counts[day] = {}
            daily_counts[day][notification.type.value] = (
                daily_counts[day].get(notification.type.value, 0) + 1
            )

        # Create digest summary
        total_count = len(notifications)
        summary = (
            f"Weekly summary: {total_count} notifications from the past 7 days\n\n"
        )

        for day in sorted(daily_counts.keys(), reverse=True):
            day_str = day.strftime("%A, %B %d")
            summary += f"{day_str}:\n"
            for notif_type, count in daily_counts[day].items():
                summary += f"  - {count} {notif_type.replace('_', ' ').lower()}\n"
            summary += "\n"

        # Create digest record
        digest = NotificationDigest(
            user_id=user_id,
            company_id=company_id,
            digest_type=DigestType.WEEKLY,
            status=DigestStatus.PENDING,
            title="Weekly Notification Digest",
            summary=summary,
            notification_count=total_count,
            notification_ids=[n.id for n in notifications],
            scheduled_for=datetime.utcnow() + timedelta(hours=2),  # Send in 2 hours
        )

        self.db.add(digest)
        self.db.commit()
        self.db.refresh(digest)

        logger.info(
            f"Created weekly digest for user {user_id} with {total_count} notifications"
        )
        return digest

    def should_create_digest(self, user_id: int, digest_type: DigestType) -> bool:
        """Check if a digest should be created for the user based on their preferences"""
        prefs = (
            self.db.query(NotificationPreferences)
            .filter(NotificationPreferences.user_id == user_id)
            .first()
        )

        if not prefs:
            return False

        # Check if user has digest mode enabled
        if digest_type == DigestType.DAILY and prefs.digest_mode == DigestMode.DAILY:
            return True
        elif (
            digest_type == DigestType.WEEKLY and prefs.digest_mode == DigestMode.WEEKLY
        ):
            return True

        return False

    def mark_notifications_as_processed(self, notification_ids: List[int]):
        """Mark notifications as processed (read/archived) after digest creation"""
        self.db.query(Notification).filter(
            Notification.id.in_(notification_ids)
        ).update({"status": "read"})

        self.db.commit()
        logger.info(f"Marked {len(notification_ids)} notifications as processed")

    def get_pending_digests(self) -> List[NotificationDigest]:
        """Get all pending digests that are ready to be sent"""
        now = datetime.utcnow()

        return (
            self.db.query(NotificationDigest)
            .filter(
                and_(
                    NotificationDigest.status == DigestStatus.PENDING,
                    NotificationDigest.scheduled_for <= now,
                )
            )
            .all()
        )

    def send_digest(self, digest: NotificationDigest) -> bool:
        """Send a digest notification to the user"""
        try:
            # Create a new notification for the digest
            from app.crud_notifications import create_notification

            notification_data = {
                "user_id": digest.user_id,
                "company_id": digest.company_id,
                "title": digest.title,
                "message": digest.summary,
                "type": NotificationType.SYSTEM_MESSAGE,
                "status": "unread",
            }

            # Create the digest notification
            create_notification(self.db, notification_data)

            # Update digest status
            digest.status = DigestStatus.SENT
            digest.sent_at = datetime.utcnow()
            self.db.commit()

            # Mark original notifications as processed
            if digest.notification_ids:
                self.mark_notifications_as_processed(digest.notification_ids)

            logger.info(f"Sent digest {digest.id} to user {digest.user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send digest {digest.id}: {str(e)}")
            digest.status = DigestStatus.FAILED
            self.db.commit()
            return False

    def process_pending_digests(self):
        """Process all pending digests that are ready to be sent"""
        pending_digests = self.get_pending_digests()

        sent_count = 0
        failed_count = 0

        for digest in pending_digests:
            if self.send_digest(digest):
                sent_count += 1
            else:
                failed_count += 1

        logger.info(
            f"Processed {len(pending_digests)} digests: {sent_count} sent, {failed_count} failed"
        )
        return sent_count, failed_count

    def cleanup_old_digests(self, days_old: int = 30):
        """Clean up old digest records"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted_count = (
            self.db.query(NotificationDigest)
            .filter(NotificationDigest.created_at < cutoff_date)
            .delete()
        )

        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old digest records")
        return deleted_count
