import hashlib
import json

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class AIMemoryEntry(Base):
    __tablename__ = "ai_memory_entries"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, nullable=True, index=True)
    team_id = Column(Integer, nullable=True, index=True)
    key = Column(String(255), nullable=False, index=True)  # Memory key for retrieval
    value_encrypted = Column(Text, nullable=False)  # AES-encrypted memory value
    purpose = Column(
        String(100), nullable=False, index=True
    )  # Purpose of memory storage
    ttl = Column(Integer, nullable=True)  # Time-to-live in seconds (None = permanent)
    consent = Column(Boolean, default=True, nullable=False)  # User consent for storage
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    expires_at = Column(
        DateTime, nullable=True, index=True
    )  # Computed from created_at + ttl
    hash_chain_ref = Column(
        String(64), nullable=True, index=True
    )  # Reference to audit chain hash
    is_deleted = Column(Boolean, default=False, index=True)  # Soft delete flag
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", back_populates="ai_memory_entries")

    # Composite indexes for efficient tenant-scoped queries
    __table_args__ = (
        Index(
            "idx_ai_memory_tenant_key", "company_id", "department_id", "team_id", "key"
        ),
        Index("idx_ai_memory_purpose", "company_id", "purpose"),
        Index("idx_ai_memory_expires", "expires_at", "is_deleted"),
        Index("idx_ai_memory_created_by", "created_by", "is_deleted"),
    )

    class Config:
        from_attributes = True

    def compute_memory_hash(self) -> str:
        """Compute hash of memory entry for integrity verification"""
        hash_data = {
            "company_id": self.company_id,
            "department_id": self.department_id,
            "team_id": self.team_id,
            "key": self.key,
            "purpose": self.purpose,
            "ttl": self.ttl,
            "consent": self.consent,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

        json_data = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_data.encode("utf-8")).hexdigest()

    def is_expired(self) -> bool:
        """Check if memory entry has expired"""
        if self.expires_at is None:
            return False
        from datetime import datetime

        return datetime.utcnow() > self.expires_at

    def is_accessible_by(
        self,
        user_company_id: int,
        user_department_id: int = None,
        user_team_id: int = None,
        user_role: str = None,
    ) -> bool:
        """Check if user can access this memory entry based on tenant isolation"""
        # Must be same company
        if self.company_id != user_company_id:
            return False

        # Department scope: user must be in same department or higher role
        if self.department_id is not None:
            if user_department_id != self.department_id:
                # Allow access if user has company-wide or superadmin role
                if user_role not in ["COMPANY_ADMIN", "SUPERADMIN"]:
                    return False

        # Team scope: user must be in same team or higher role
        if self.team_id is not None:
            if user_team_id != self.team_id:
                # Allow access if user has department-wide or higher role
                if user_role not in ["DEPARTMENT_ADMIN", "COMPANY_ADMIN", "SUPERADMIN"]:
                    return False

        return True

    @staticmethod
    def create_entry(
        company_id: int,
        department_id: int = None,
        team_id: int = None,
        key: str = None,
        value_encrypted: str = None,
        purpose: str = None,
        ttl: int = None,
        consent: bool = True,
        created_by: int = None,
    ) -> "AIMemoryEntry":
        """Create a new AI memory entry"""
        from datetime import datetime, timedelta

        entry = AIMemoryEntry(
            company_id=company_id,
            department_id=department_id,
            team_id=team_id,
            key=key,
            value_encrypted=value_encrypted,
            purpose=purpose,
            ttl=ttl,
            consent=consent,
            created_by=created_by,
        )

        # Calculate expiration time if TTL is provided
        if ttl is not None:
            entry.expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        return entry
