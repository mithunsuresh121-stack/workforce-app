from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base

from .notification_digest import DigestMode


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Individual preference fields for better querying
    mute_all = Column(Boolean, default=False, nullable=False)
    digest_mode = Column(String(20), default=DigestMode.IMMEDIATE, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)

    # JSON field for notification types and any additional preferences
    notification_types = Column(
        JSON,
        nullable=False,
        default={
            "TASK_ASSIGNED": True,
            "SHIFT_SCHEDULED": True,
            "SYSTEM_MESSAGE": True,
            "ADMIN_MESSAGE": True,
        },
    )

    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<NotificationPreferences for user {self.user_id}>"

    @property
    def preferences(self):
        """Backward compatibility property"""
        return {
            "mute_all": self.mute_all,
            "digest_mode": self.digest_mode,
            "push_enabled": self.push_enabled,
            "notification_types": self.notification_types,
        }

    @preferences.setter
    def preferences(self, value):
        """Backward compatibility setter"""
        if isinstance(value, dict):
            self.mute_all = value.get("mute_all", False)
            self.digest_mode = value.get("digest_mode", DigestMode.IMMEDIATE)
            self.push_enabled = value.get("push_enabled", True)
            self.notification_types = value.get(
                "notification_types",
                {
                    "TASK_ASSIGNED": True,
                    "SHIFT_SCHEDULED": True,
                    "SYSTEM_MESSAGE": True,
                    "ADMIN_MESSAGE": True,
                },
            )
