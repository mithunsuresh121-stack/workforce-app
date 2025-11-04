from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, nullable=True, index=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # AI-specific audit fields
    ai_request_text = Column(Text, nullable=True)
    ai_capability = Column(String, nullable=True)
    ai_decision = Column(String, nullable=True)  # 'allowed', 'blocked', 'pending_approval'
    ai_scope_valid = Column(Boolean, nullable=True)
    ai_required_role = Column(String, nullable=True)
    ai_user_role = Column(String, nullable=True)
    ai_severity = Column(String, nullable=True)  # 'low', 'high'

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    class Config:
        from_attributes = True
