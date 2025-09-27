from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class ProfileUpdateRequest(Base):
    __tablename__ = "profile_update_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), index=True)
    request_type = Column(String(50), index=True)
    payload = Column(Text, nullable=True)  # JSON as text
    status = Column(String(20), default="pending")
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="profile_update_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
