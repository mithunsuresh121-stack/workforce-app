from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import enum

class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "TASK_ASSIGNED"
    SHIFT_SCHEDULED = "SHIFT_SCHEDULED"
    SYSTEM_MESSAGE = "SYSTEM_MESSAGE"
    ADMIN_MESSAGE = "ADMIN_MESSAGE"
    LEAVE_APPROVED = "LEAVE_APPROVED"
    LEAVE_REJECTED = "LEAVE_REJECTED"
    ATTENDANCE_CLOCK_IN = "ATTENDANCE_CLOCK_IN"
    ATTENDANCE_CLOCK_OUT = "ATTENDANCE_CLOCK_OUT"

class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User")
    company = relationship("Company")

    def __repr__(self):
        return f"<Notification {self.title} for user {self.user_id}>"
