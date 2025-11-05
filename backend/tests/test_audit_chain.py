import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.audit_chain_service import AuditChainService
from app.models.audit_chain import AuditChain
from app.base_crud import create_user
from app.models.user import User, UserRole


@pytest.fixture
def test_user(db: Session):
    return create_user(db, email="test@example.com", password="pass", full_name="Test User", role=UserRole.EMPLOYEE)


class TestAuditChain:
    def test_chain_initialization(self, db: Session, test_user):
        """Test audit chain initialization"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Chain should start empty
        head = AuditChainService.get_chain_head(db, chain_id)
        assert head is None

        # Next sequence should be 0
        next_seq = AuditChainService.get_next_sequence_number(db, chain_id)
        assert next_seq == 0

    def test_append_to_chain(self, db: Session, test_user):
        """Test appending entries to audit chain"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Append first entry
        entry1 = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TEST_EVENT",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data1"}
        )

        assert entry1.sequence_number == 0
        assert entry1.previous_hash == AuditChainService.GENESIS_HASH
        assert entry1.event_type == "TEST_EVENT"
        assert entry1.verify_integrity() == True

        # Append second entry
        entry2 = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TEST_EVENT2",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data2"}
        )

        assert entry2.sequence_number == 1
        assert entry2.previous_hash == entry1.current_hash
        assert entry2.verify_integrity() == True

        # Check chain head
        head = AuditChainService.get_chain_head(db, chain_id)
        assert head.id == entry2.id

    def test_chain_integrity_verification_valid(self, db: Session, test_user):
        """Test integrity verification of valid chain"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Create a valid chain
        for i in range(3):
            AuditChainService.append_to_chain(
                db=db,
                chain_id=chain_id,
                event_type=f"TEST_EVENT_{i}",
                user_id=test_user.id,
                company_id=test_user.company_id,
                data={"index": i}
            )

        # Verify integrity
        is_valid, issues = AuditChainService.verify_chain_integrity(db, chain_id)
        assert is_valid == True
        assert len(issues) == 0

    def test_chain_integrity_verification_tampered(self, db: Session, test_user):
        """Test integrity verification detects tampering"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Create a chain
        entry = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TEST_EVENT",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data"}
        )

        # Tamper with the entry
        entry.current_hash = "tampered_hash"
        db.commit()

        # Verify integrity should detect tampering
        is_valid, issues = AuditChainService.verify_chain_integrity(db, chain_id)
        assert is_valid == False
        assert len(issues) > 0
        assert any(issue["type"] == "entry_tampered" for issue in issues)

        # Check that entry is marked as tampered
        db.refresh(entry)
        assert entry.is_tampered == True

    def test_chain_replay(self, db: Session, test_user):
        """Test chain replay functionality"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Create entries
        entries_data = []
        for i in range(5):
            entry = AuditChainService.append_to_chain(
                db=db,
                chain_id=chain_id,
                event_type=f"EVENT_{i}",
                user_id=test_user.id,
                company_id=test_user.company_id,
                data={"index": i, "value": f"test_{i}"}
            )
            entries_data.append({
                "sequence_number": entry.sequence_number,
                "event_type": entry.event_type,
                "data": {"index": i, "value": f"test_{i}"}
            })

        # Replay entire chain
        replay = AuditChainService.replay_chain(db, chain_id)
        assert len(replay) == 5
        for i, entry in enumerate(replay):
            assert entry["sequence_number"] == i
            assert entry["event_type"] == f"EVENT_{i}"
            assert entry["data"]["index"] == i

        # Replay partial chain
        partial_replay = AuditChainService.replay_chain(db, chain_id, start_sequence=2, end_sequence=3)
        assert len(partial_replay) == 2
        assert partial_replay[0]["sequence_number"] == 2
        assert partial_replay[1]["sequence_number"] == 3

    def test_chain_stats(self, db: Session, test_user):
        """Test chain statistics"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Empty chain stats
        stats = AuditChainService.get_chain_stats(db, chain_id)
        assert stats["total_entries"] == 0
        assert stats["tampered_entries"] == 0
        assert stats["integrity_percentage"] == 100

        # Add entries
        for i in range(3):
            AuditChainService.append_to_chain(
                db=db,
                chain_id=chain_id,
                event_type="TEST_EVENT",
                user_id=test_user.id,
                company_id=test_user.company_id,
                data={"test": "data"}
            )

        stats = AuditChainService.get_chain_stats(db, chain_id)
        assert stats["total_entries"] == 3
        assert stats["tampered_entries"] == 0
        assert stats["integrity_percentage"] == 100
        assert stats["latest_sequence"] == 2

    def test_tampering_detection(self, db: Session, test_user):
        """Test tampering detection"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Create entries
        entry1 = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="EVENT1",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data1"}
        )

        entry2 = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="EVENT2",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data2"}
        )

        # Tamper with entry1
        entry1.current_hash = "tampered"
        db.commit()

        # Detect tampering
        incidents = AuditChainService.detect_tampering(db, chain_id)
        assert len(incidents) >= 1
        assert any(incident["entry_id"] == entry1.id for incident in incidents)

    def test_ai_event_logging_to_chain(self, db: Session, test_user):
        """Test AI events are logged to audit chain"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Log AI event
        AuditChainService.log_ai_event(
            db=db,
            user_id=test_user.id,
            company_id=test_user.company_id,
            event_type="AI_REQUEST",
            data={
                "request_text": "Test AI request",
                "capability": "READ_TEAM_DATA",
                "decision": "allowed",
                "scope_valid": True,
                "severity": "low"
            }
        )

        # Verify entry was created
        head = AuditChainService.get_chain_head(db, chain_id)
        assert head is not None
        assert head.event_type == "AI_AI_REQUEST"
        data_dict = json.loads(head.data)
        assert "request_text" in data_dict
        assert data_dict["request_text"] == "Test AI request"

    def test_policy_decision_logging(self, db: Session, test_user):
        """Test policy decisions are logged to chain"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        AuditChainService.log_policy_decision(
            db=db,
            user_id=test_user.id,
            company_id=test_user.company_id,
            decision="allowed",
            policy_version="1.0",
            data={"capability": "READ_COMPANY_DATA"}
        )

        head = AuditChainService.get_chain_head(db, chain_id)
        assert head.event_type == "POLICY_DECISION"
        data_dict = json.loads(head.data)
        assert data_dict["decision"] == "allowed"
        assert data_dict["policy_version"] == "1.0"

    def test_trust_score_change_logging(self, db: Session, test_user):
        """Test trust score changes are logged to chain"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        AuditChainService.log_trust_change(
            db=db,
            user_id=test_user.id,
            company_id=test_user.company_id,
            old_score=100,
            new_score=85,
            reason="Policy violation"
        )

        head = AuditChainService.get_chain_head(db, chain_id)
        assert head.event_type == "TRUST_SCORE_CHANGE"
        data_dict = json.loads(head.data)
        assert data_dict["old_score"] == 100
        assert data_dict["new_score"] == 85
        assert data_dict["change"] == -15
        assert data_dict["reason"] == "Policy violation"

    def test_hash_collision_prevention(self, db: Session, test_user):
        """Test that duplicate hashes are prevented"""
        chain_id = AuditChainService.get_or_create_chain_id(test_user.company_id)

        # Create entry
        entry = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TEST_EVENT",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data"}
        )

        # Try to create another entry with same data (should have different sequence/hash)
        entry2 = AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id,
            event_type="TEST_EVENT",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data"}
        )

        # Hashes should be different due to sequence number
        assert entry.current_hash != entry2.current_hash
        assert entry2.sequence_number == 1

    def test_chain_isolation_by_company(self, db: Session, test_user):
        """Test chains are isolated by company"""
        # Create user from different company
        other_user = create_user(db, email="other@test.com", password="pass", full_name="Other User", role=UserRole.EMPLOYEE)
        other_user.company_id = 999
        db.commit()

        chain_id1 = AuditChainService.get_or_create_chain_id(test_user.company_id)
        chain_id2 = AuditChainService.get_or_create_chain_id(other_user.company_id)

        assert chain_id1 != chain_id2

        # Add to first chain
        AuditChainService.append_to_chain(
            db=db,
            chain_id=chain_id1,
            event_type="TEST",
            user_id=test_user.id,
            company_id=test_user.company_id,
            data={"test": "data"}
        )

        # Second chain should still be empty
        head2 = AuditChainService.get_chain_head(db, chain_id2)
        assert head2 is None
