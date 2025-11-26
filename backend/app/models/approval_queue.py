from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import enum

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"

class ApprovalPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalQueue(Base):
    __tablename__ = "approval_queues"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=True, index=True)

    # Request details
    request_type = Column(String, nullable=False, index=True)  # "ai_capability", "policy_change", etc.
    request_data = Column(Text, nullable=False)  # JSON serialized request details
    risk_score = Column(Integer, nullable=True)  # Risk score at time of request

    # Approval workflow
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    priority = Column(Enum(ApprovalPriority), default=ApprovalPriority.MEDIUM, index=True)

    # Requestor
    requestor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requestor_notes = Column(Text, nullable=True)

    # Current approver
    current_approver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_at = Column(DateTime, nullable=True)

    # Approval details
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Escalation
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    escalation_level = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime, nullable=True)  # Auto-expire pending approvals

    # Relationships
    requestor = relationship("User", foreign_keys=[requestor_id], back_populates="approval_requests")
    current_approver = relationship("User", foreign_keys=[current_approver_id], back_populates="pending_approvals")
    approver = relationship("User", foreign_keys=[approved_by_id], back_populates="approved_requests")
    approval_steps = relationship("ApprovalQueueItem", back_populates="approval_queue", cascade="all, delete-orphan")

    class Config:
        from_attributes = True

class ApprovalQueueItem(Base):
    """Individual approval steps in a multi-step approval process"""

    __tablename__ = "approval_queue_items"

    id = Column(Integer, primary_key=True, index=True)
    approval_queue_id = Column(Integer, ForeignKey("approval_queues.id"), nullable=False, index=True)

    # Step details
    step_number = Column(Integer, nullable=False)
    step_type = Column(String, nullable=False)  # "auto_approve", "human_review", "escalation"
    required_role = Column(String, nullable=True)  # UserRole enum value
    required_clearance = Column(String, nullable=True)  # Additional clearance requirements

    # Step status
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    decision = Column(String, nullable=True)  # "approved", "rejected", "escalated"
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    approval_queue = relationship("ApprovalQueue", back_populates="approval_steps")
    assigned_to = relationship("User", back_populates="assigned_approvals")

    class Config:
        from_attributes = True

# Add relationships to User model (these would need to be added to the User model)
# approval_requests: List[ApprovalQueue]
# pending_approvals: List[ApprovalQueue]
# approved_requests: List[ApprovalQueue]
# assigned_approvals: List[ApprovalQueueItem]
