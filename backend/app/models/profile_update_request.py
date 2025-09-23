from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
from enum import Enum

class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ProfileUpdateRequest(Base):
    __tablename__ = "profile_update_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User whose profile is being updated
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who made the request (could be self or manager)
    request_type = Column(String, nullable=False)  # "update" or "delete"
    payload = Column(Text, nullable=True)  # JSON string of requested changes
    status = Column(String, default=RequestStatus.PENDING.value)
    created_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])

    def __repr__(self):
        return f"<ProfileUpdateRequest {self.id} - {self.request_type} - {self.status}>"
