import hashlib
import json

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class AuditChain(Base):
    __tablename__ = "audit_chains"

    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(String, nullable=False, index=True)  # Unique chain identifier
    sequence_number = Column(Integer, nullable=False, index=True)  # Position in chain
    previous_hash = Column(String(64), nullable=False)  # SHA-256 hash of previous entry
    current_hash = Column(
        String(64), nullable=True, unique=True, index=True
    )  # SHA-256 hash of this entry
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, nullable=True, index=True)
    data = Column(Text, nullable=False)  # JSON serialized event data
    signature = Column(Text, nullable=True)  # Cryptographic signature (future use)
    is_tampered = Column(Boolean, default=False, index=True)  # Tamper detection flag
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_chain_entries")

    class Config:
        from_attributes = True

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this audit entry"""
        # Create deterministic data for hashing
        hash_data = {
            "chain_id": self.chain_id,
            "sequence_number": self.sequence_number,
            "previous_hash": self.previous_hash,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

        # Serialize to JSON with sorted keys for consistency
        json_data = json.dumps(hash_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_data.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify that current_hash matches computed hash"""
        return self.current_hash == self.compute_hash()

    @staticmethod
    def create_entry(
        chain_id: str,
        sequence_number: int,
        previous_hash: str,
        event_type: str,
        user_id: int,
        company_id: int = None,
        data: dict = None,
        signature: str = None,
    ) -> "AuditChain":
        """Create a new audit chain entry"""
        entry = AuditChain(
            chain_id=chain_id,
            sequence_number=sequence_number,
            previous_hash=previous_hash,
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            data=json.dumps(data or {}, sort_keys=True),
            signature=signature,
        )

        # Hash will be computed after saving to include created_at
        return entry
