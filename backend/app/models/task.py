import enum

from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base
from app.models.attachment import Attachment


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    # team_id = Column(Integer, ForeignKey("teams.id"), index=True, nullable=True)  # For future team assignments
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        server_default=TaskStatus.PENDING,
        index=True,
        nullable=False,
    )
    priority = Column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        server_default=TaskPriority.MEDIUM,
        nullable=False,
    )
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company")
    assignee = relationship("User", foreign_keys=[assignee_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    attachments = relationship(
        "Attachment", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Task id={self.id} title={self.title!r} "
            f"status={self.status} priority={self.priority} "
            f"assignee_id={self.assignee_id} company_id={self.company_id}>"
        )
