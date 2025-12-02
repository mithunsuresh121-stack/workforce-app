from uuid import uuid4

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        LargeBinary, String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class AIMemoryEntry(Base):
    __tablename__ = "ai_memory_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    department_id = Column(
        UUID(as_uuid=True),
        ForeignKey("company_departments.id"),
        nullable=True,
        index=True,
    )
    team_id = Column(
        UUID(as_uuid=True), ForeignKey("company_teams.id"), nullable=True, index=True
    )
    key = Column(String(255), nullable=False, index=True)
    value_encrypted = Column(LargeBinary, nullable=False)
    purpose = Column(String(100), nullable=False, index=True)
    ttl = Column(Integer, nullable=True)  # Time to live in seconds
    consent = Column(Boolean, default=False, nullable=False)
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    hash_chain_ref = Column(String(64), nullable=True, index=True)

    # Relationships
    creator = relationship("User", back_populates="ai_memory_entries")
    company = relationship("Company", back_populates="ai_memory_entries")

    # Composite indexes for tenant isolation and queries
    __table_args__ = (
        Index(
            "idx_ai_memory_tenant_scope",
            "company_id",
            "department_id",
            "team_id",
            "key",
        ),
        Index("idx_ai_memory_expiry", "expires_at"),
        Index("idx_ai_memory_purpose", "company_id", "purpose"),
    )

    def __repr__(self):
        return f"<AIMemoryEntry(id='{self.id}', key='{self.key}', purpose='{self.purpose}', company_id='{self.company_id}')>"
