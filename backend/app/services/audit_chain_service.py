import structlog
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from app.db import SessionLocal
from app.models.audit_chain import AuditChain
from app.models.user import User

logger = structlog.get_logger(__name__)

class AuditChainService:
    # Genesis hash for chain initialization
    GENESIS_HASH = "0" * 64

    @staticmethod
    def get_or_create_chain_id(company_id: int = None) -> str:
        """Generate a consistent chain ID for a company or global chain"""
        if company_id:
            return f"company_{company_id}"
        return "global"

    @staticmethod
    def get_chain_head(db: Session, chain_id: str) -> Optional[AuditChain]:
        """Get the latest entry in the audit chain"""
        return db.query(AuditChain).filter(
            AuditChain.chain_id == chain_id
        ).order_by(desc(AuditChain.sequence_number)).first()

    @staticmethod
    def get_next_sequence_number(db: Session, chain_id: str) -> int:
        """Get the next sequence number for a chain"""
        head = AuditChainService.get_chain_head(db, chain_id)
        return (head.sequence_number + 1) if head else 0

    @staticmethod
    def append_to_chain(
        db: Session,
        chain_id: str,
        event_type: str,
        user_id: int,
        company_id: int = None,
        data: dict = None,
        signature: str = None
    ) -> AuditChain:
        """Append a new entry to the audit chain"""
        # Get chain head for previous hash and sequence number
        head = AuditChainService.get_chain_head(db, chain_id)
        previous_hash = head.current_hash if head else AuditChainService.GENESIS_HASH
        sequence_number = AuditChainService.get_next_sequence_number(db, chain_id)

        # Create new entry
        entry = AuditChain.create_entry(
            chain_id=chain_id,
            sequence_number=sequence_number,
            previous_hash=previous_hash,
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            data=data or {},
            signature=signature
        )

        # Save to database first to get created_at timestamp
        db.add(entry)
        db.commit()
        db.refresh(entry)

        # Now compute and set the hash with the actual created_at
        entry.current_hash = entry.compute_hash()
        db.commit()
        db.refresh(entry)

        logger.info(
            "Audit chain entry appended",
            chain_id=chain_id,
            sequence_number=sequence_number,
            event_type=event_type,
            user_id=user_id
        )

        return entry

    @staticmethod
    def verify_chain_integrity(db: Session, chain_id: str, max_entries: int = None) -> Tuple[bool, List[Dict]]:
        """Verify the integrity of an entire audit chain"""
        # Get all entries in sequence order
        query = db.query(AuditChain).filter(
            AuditChain.chain_id == chain_id
        ).order_by(AuditChain.sequence_number)

        if max_entries:
            query = query.limit(max_entries)

        entries = query.all()

        if not entries:
            return True, []  # Empty chain is valid

        issues = []
        previous_hash = AuditChainService.GENESIS_HASH
        expected_sequence = 0

        for entry in entries:
            # Check sequence continuity
            if entry.sequence_number != expected_sequence:
                issues.append({
                    "type": "sequence_gap",
                    "entry_id": entry.id,
                    "expected_sequence": expected_sequence,
                    "actual_sequence": entry.sequence_number
                })

            expected_sequence = entry.sequence_number + 1

            # Check hash chain continuity
            if entry.previous_hash != previous_hash:
                issues.append({
                    "type": "hash_chain_broken",
                    "entry_id": entry.id,
                    "expected_previous_hash": previous_hash,
                    "actual_previous_hash": entry.previous_hash
                })

            # Check entry integrity
            if not entry.verify_integrity():
                issues.append({
                    "type": "entry_tampered",
                    "entry_id": entry.id,
                    "stored_hash": entry.current_hash,
                    "computed_hash": entry.compute_hash()
                })

            # Update previous hash for next iteration
            previous_hash = entry.current_hash

        # Mark tampered entries
        for issue in issues:
            if issue["type"] in ["entry_tampered", "hash_chain_broken"]:
                db.query(AuditChain).filter(
                    AuditChain.id == issue["entry_id"]
                ).update({"is_tampered": True})

        db.commit()

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def replay_chain(db: Session, chain_id: str, start_sequence: int = 0, end_sequence: int = None) -> List[Dict]:
        """Replay audit chain entries in order"""
        query = db.query(AuditChain).filter(
            and_(
                AuditChain.chain_id == chain_id,
                AuditChain.sequence_number >= start_sequence
            )
        ).order_by(AuditChain.sequence_number)

        if end_sequence is not None:
            query = query.filter(AuditChain.sequence_number <= end_sequence)

        entries = query.all()

        replay_data = []
        for entry in entries:
            replay_data.append({
                "sequence_number": entry.sequence_number,
                "event_type": entry.event_type,
                "user_id": entry.user_id,
                "company_id": entry.company_id,
                "data": json.loads(entry.data),
                "created_at": entry.created_at.isoformat(),
                "is_tampered": entry.is_tampered
            })

        return replay_data

    @staticmethod
    def get_chain_stats(db: Session, chain_id: str) -> Dict:
        """Get statistics about an audit chain"""
        total_entries = db.query(func.count(AuditChain.id)).filter(
            AuditChain.chain_id == chain_id
        ).scalar()

        tampered_entries = db.query(func.count(AuditChain.id)).filter(
            and_(
                AuditChain.chain_id == chain_id,
                AuditChain.is_tampered == True
            )
        ).scalar()

        latest_entry = AuditChainService.get_chain_head(db, chain_id)

        return {
            "chain_id": chain_id,
            "total_entries": total_entries or 0,
            "tampered_entries": tampered_entries or 0,
            "integrity_percentage": ((total_entries - tampered_entries) / total_entries * 100) if total_entries > 0 else 100,
            "latest_sequence": latest_entry.sequence_number if latest_entry else -1,
            "latest_hash": latest_entry.current_hash if latest_entry else AuditChainService.GENESIS_HASH,
            "last_updated": latest_entry.created_at.isoformat() if latest_entry else None
        }

    @staticmethod
    def detect_tampering(db: Session, chain_id: str) -> List[Dict]:
        """Detect and return all tampering incidents in a chain"""
        # First verify integrity to mark any tampered entries
        AuditChainService.verify_chain_integrity(db, chain_id)

        tampered_entries = db.query(AuditChain).filter(
            and_(
                AuditChain.chain_id == chain_id,
                AuditChain.is_tampered == True
            )
        ).order_by(AuditChain.sequence_number).all()

        incidents = []
        for entry in tampered_entries:
            incidents.append({
                "entry_id": entry.id,
                "sequence_number": entry.sequence_number,
                "event_type": entry.event_type,
                "user_id": entry.user_id,
                "detected_at": datetime.utcnow().isoformat(),
                "tamper_type": "hash_mismatch" if not entry.verify_integrity() else "chain_broken"
            })

        return incidents

    @staticmethod
    def log_ai_event(
        db: Session,
        user_id: int,
        company_id: int,
        event_type: str,
        data: dict
    ):
        """Log AI-related events to the audit chain"""
        chain_id = AuditChainService.get_or_create_chain_id(company_id)

        AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type=f"AI_{event_type}",
            user_id=user_id,
            company_id=company_id,
            data=data
        )

    @staticmethod
    def log_policy_decision(
        db: Session,
        user_id: int,
        company_id: int,
        decision: str,
        policy_version: str,
        data: dict
    ):
        """Log policy decisions to the audit chain"""
        chain_id = AuditChainService.get_or_create_chain_id(company_id)

        AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="POLICY_DECISION",
            user_id=user_id,
            company_id=company_id,
            data={
                "decision": decision,
                "policy_version": policy_version,
                **data
            }
        )

    @staticmethod
    def log_trust_change(
        db: Session,
        user_id: int,
        company_id: int,
        old_score: int,
        new_score: int,
        reason: str
    ):
        """Log trust score changes to the audit chain"""
        chain_id = AuditChainService.get_or_create_chain_id(company_id)

        AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TRUST_SCORE_CHANGE",
            user_id=user_id,
            company_id=company_id,
            data={
                "old_score": old_score,
                "new_score": new_score,
                "change": new_score - old_score,
                "reason": reason
            }
        )

# Convenience functions
def append_audit_event(
    chain_id: str,
    event_type: str,
    user_id: int,
    company_id: int = None,
    data: dict = None
):
    """Convenience function to append audit events"""
    db = SessionLocal()
    try:
        AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            data=data
        )
    finally:
        db.close()

def verify_chain(chain_id: str) -> Tuple[bool, List[Dict]]:
    """Convenience function to verify chain integrity"""
    db = SessionLocal()
    try:
        return AuditChainService.verify_chain_integrity(db, chain_id)
    finally:
        db.close()
