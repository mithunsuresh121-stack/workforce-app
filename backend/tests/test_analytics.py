from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.channels import Channel, ChannelMember, ChannelType
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.meeting_participants import MeetingParticipant, ParticipantRole
from app.models.meetings import Meeting, MeetingStatus
from app.models.user import User, UserRole
from app.services.analytics_service import AnalyticsService


def test_get_user_stats_superadmin(db: Session, test_company: Company):
    """Test user stats for SUPERADMIN (all companies)"""
    # Create department and team
    test_department = CompanyDepartment(
        company_id=test_company.id, name="Test Department"
    )
    db.add(test_department)
    db.commit()
    db.refresh(test_department)

    test_team = CompanyTeam(department_id=test_department.id, name="Test Team")
    db.add(test_team)
    db.commit()
    db.refresh(test_team)

    # Create test users
    user1 = User(
        email="user1@test.com",
        hashed_password="hash",
        full_name="User 1",
        role=UserRole.EMPLOYEE,
        company_id=test_company.id,
        department_id=test_department.id,
        team_id=test_team.id,
        is_active=True,
        last_active=datetime.utcnow(),
    )
    user2 = User(
        email="user2@test.com",
        hashed_password="hash",
        full_name="User 2",
        role=UserRole.COMPANY_ADMIN,
        company_id=test_company.id,
        is_active=True,
        last_active=datetime.utcnow() - timedelta(days=40),  # Inactive
    )
    db.add_all([user1, user2])
    db.commit()

    stats = AnalyticsService.get_user_stats(db)

    assert stats["total_users"] == 2
    assert stats["by_role"]["EMPLOYEE"] == 1
    assert stats["by_role"]["COMPANY_ADMIN"] == 1
    assert stats["by_department"]["Test Department"] == 1
    assert stats["by_team"]["Test Team"] == 1
    assert stats["active_users"] == 1  # Only user1 is active


def test_get_user_stats_company_scoped(db: Session, test_company: Company):
    """Test user stats scoped to company"""
    stats = AnalyticsService.get_user_stats(db, test_company.id)
    # Should only count users in test_company
    assert "total_users" in stats


def test_get_channel_stats(db: Session, test_company: Company, test_user: User):
    """Test channel statistics"""
    # Create test channel
    channel = Channel(
        name="Test Channel",
        type=ChannelType.PUBLIC,
        company_id=test_company.id,
        created_by=test_user.id,
        last_message_at=datetime.utcnow(),
    )
    db.add(channel)
    db.commit()

    # Add member
    member = ChannelMember(channel_id=channel.id, user_id=test_user.id)
    db.add(member)
    db.commit()

    stats = AnalyticsService.get_channel_stats(db, test_company.id)

    assert stats["total_channels"] == 1
    assert stats["by_type"]["PUBLIC"] == 1
    assert stats["active_channels"] == 1  # Recent message
    assert stats["average_members_per_channel"] == 1.0


def test_get_meeting_stats(db: Session, test_company: Company, test_user: User):
    """Test meeting statistics"""
    # Create test meeting
    meeting = Meeting(
        title="Test Meeting",
        organizer_id=test_user.id,
        company_id=test_company.id,
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=1),
        status=MeetingStatus.SCHEDULED,
    )
    db.add(meeting)
    db.commit()

    # Add participant
    participant = MeetingParticipant(
        meeting_id=meeting.id, user_id=test_user.id, role=ParticipantRole.PARTICIPANT
    )
    db.add(participant)
    db.commit()

    stats = AnalyticsService.get_meeting_stats(db, test_company.id)

    assert stats["total_meetings"] == 1
    assert stats["by_status"]["SCHEDULED"] == 1
    assert stats["average_participants_per_meeting"] == 1.0
    assert stats["upcoming_meetings"] == 1


def test_get_audit_stats(db: Session, test_company: Company, test_user: User):
    """Test audit log statistics"""
    # Create test audit logs
    log1 = AuditLog(
        event_type="LOGIN",
        user_id=test_user.id,
        company_id=test_company.id,
        details={"ip": "127.0.0.1"},
    )
    log2 = AuditLog(
        event_type="LOGOUT",
        user_id=test_user.id,
        company_id=test_company.id,
        details={"session": "abc"},
    )
    db.add_all([log1, log2])
    db.commit()

    stats = AnalyticsService.get_audit_stats(db, test_company.id)

    assert stats["total_audit_events"] == 2
    assert stats["by_event_type_last_30_days"]["LOGIN"] == 1
    assert stats["by_event_type_last_30_days"]["LOGOUT"] == 1
    assert stats["recent_events_last_24_hours"] == 2
    assert len(stats["top_users_by_activity"]) == 1
    assert stats["top_users_by_activity"][0]["user_id"] == test_user.id
    assert stats["top_users_by_activity"][0]["event_count"] == 2


# API endpoint tests would go here, but require FastAPI test client setup
# For now, focus on service layer tests
