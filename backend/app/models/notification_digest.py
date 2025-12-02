import enum

from sqlalchemy import (JSON, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class DigestType(str, enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class DigestStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class DigestMode(str, enum.Enum):
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"


class NotificationDigest(Base):
    __tablename__ = "notification_digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    digest_type = Column(Enum(DigestType), nullable=False)
    status = Column(Enum(DigestStatus), default=DigestStatus.PENDING, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    notification_count = Column(Integer, nullable=False)
    notification_ids = Column(
        JSON, nullable=True
    )  # Store IDs of notifications included in digest
    scheduled_for = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<NotificationDigest {self.digest_type} for user {self.user_id}>"
