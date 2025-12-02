from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base
from app.models.approval_queue import ApprovalQueue
from app.models.user import User


class ApprovalQueueItem(Base):
    __tablename__ = "approval_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    approval_queue_id = Column(
        Integer, ForeignKey("approval_queues.id"), nullable=False
    )
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    reviewed_at = Column(DateTime, nullable=True)
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    approval_queue = relationship("ApprovalQueue", back_populates="items")
    assigned_to = relationship("User", back_populates="assigned_approvals")

    def __repr__(self):
        return f"<ApprovalQueueItem {self.id} for queue {self.approval_queue_id}>"
