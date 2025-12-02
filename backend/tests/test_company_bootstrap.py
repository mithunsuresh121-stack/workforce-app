from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from app.base_crud import create_user
from app.models.audit_log import AuditLog
from app.models.channels import Channel, ChannelMember, ChannelType
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.meeting_participants import MeetingParticipant, ParticipantRole
from app.models.meetings import Meeting, MeetingStatus
from app.models.user import User
from app.services.company_service import CompanyService


def test_bootstrap_company_success(db: Session, test_superadmin: User):
    """Test successful company bootstrap"""
    company_name = "Test Bootstrap Company"

    result = CompanyService.bootstrap_company(
        db=db, company_name=company_name, superadmin_user=test_superadmin
    )

    # Verify return structure
    assert "company" in result
    assert "first_admin_user" in result
    assert "bootstrap_status" in result
    assert "temporary_access_link" in result
    assert "token_expiry" in result
    assert result["bootstrap_status"] == "success"

    # Verify company created
    company = result["company"]
    assert company.name == company_name

    # Verify admin user created
    admin_user = result["first_admin_user"]
    assert admin_user.role == "COMPANY_ADMIN"
    assert admin_user.company_id == company.id
    assert "@" in admin_user.email

    # Verify database state
    # Company settings
    settings = (
        db.query(CompanySettings)
        .filter(CompanySettings.company_id == company.id)
        .first()
    )
    assert settings is not None

    # General channel
    channel = (
        db.query(Channel)
        .filter(Channel.company_id == company.id, Channel.name == "General")
        .first()
    )
    assert channel is not None
    assert channel.type == ChannelType.PUBLIC

    # Channel membership
    member = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == channel.id,
            ChannelMember.user_id == admin_user.id,
        )
        .first()
    )
    assert member is not None

    # Meeting room
    meeting = (
        db.query(Meeting)
        .filter(Meeting.company_id == company.id, Meeting.title == "Meeting Room")
        .first()
    )
    assert meeting is not None
    assert meeting.status == MeetingStatus.SCHEDULED

    # Meeting participant
    participant = (
        db.query(MeetingParticipant)
        .filter(
            MeetingParticipant.meeting_id == meeting.id,
            MeetingParticipant.user_id == admin_user.id,
        )
        .first()
    )
    assert participant is not None
    assert participant.role == ParticipantRole.ORGANIZER

    # Audit log
    audit_log = (
        db.query(AuditLog)
        .filter(
            AuditLog.event_type == "COMPANY_BOOTSTRAPPED",
            AuditLog.company_id == company.id,
        )
        .first()
    )
    assert audit_log is not None


def test_bootstrap_company_non_superadmin(db: Session, test_companyadmin: User):
    """Test that non-superadmin cannot bootstrap company"""
    with pytest.raises(ValueError, match="Only SUPERADMIN can bootstrap companies"):
        CompanyService.bootstrap_company(
            db=db, company_name="Test Company", superadmin_user=test_companyadmin
        )


def test_bootstrap_company_rollback_on_failure(db: Session, test_superadmin: User):
    """Test that transaction rolls back on failure"""
    # Mock a failure in the middle
    with patch.object(
        CompanyService, "_generate_temp_password", side_effect=Exception("Mock failure")
    ):
        with pytest.raises(Exception, match="Mock failure"):
            CompanyService.bootstrap_company(
                db=db, company_name="Test Company", superadmin_user=test_superadmin
            )

    # Verify nothing was committed
    company_count = db.query(Company).filter(Company.name == "Test Company").count()
    assert company_count == 0


def test_generate_temp_password():
    """Test temporary password generation"""
    password = CompanyService._generate_temp_password()
    assert len(password) == 12
    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)


def test_generate_temp_token():
    """Test temporary token generation"""
    token = CompanyService._generate_temp_token()
    assert len(token) > 0
    # URL-safe tokens should not contain certain characters
    assert "/" not in token
    assert "+" not in token
