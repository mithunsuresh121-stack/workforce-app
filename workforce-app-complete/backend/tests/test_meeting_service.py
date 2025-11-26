import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.meeting_service import meeting_service
from app.models.user import User
from app.models.company import Company

def test_create_meeting(db: Session, test_company: Company, test_user: User, test_user2: User):
    """Test creating a meeting"""
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    meeting = meeting_service.create_meeting(
        db=db,
        title="Test Meeting",
        organizer_id=test_user.id,
        company_id=test_company.id,
        start_time=start_time,
        end_time=end_time,
        participant_ids=[test_user2.id]
    )
    assert meeting.title == "Test Meeting"
    assert meeting.organizer_id == test_user.id
    assert meeting.company_id == test_company.id

def test_join_meeting(db: Session, test_company: Company, test_user: User, test_user2: User):
    """Test joining a meeting"""
    # Create meeting first
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    meeting = meeting_service.create_meeting(
        db=db,
        title="Test Meeting",
        organizer_id=test_user.id,
        company_id=test_company.id,
        start_time=start_time,
        end_time=end_time,
        participant_ids=[test_user2.id]
    )

    # Join meeting (mock async call)
    import asyncio
    from unittest.mock import patch
    with patch('asyncio.create_task'):
        participant = meeting_service.join_meeting(db, meeting.id, test_user2.id)
    assert participant.user_id == test_user2.id
    assert participant.meeting_id == meeting.id
    assert participant.join_time is not None

def test_end_meeting(db: Session, test_company: Company, test_user: User, test_user2: User):
    """Test ending a meeting"""
    # Create and start meeting
    start_time = datetime.utcnow() - timedelta(minutes=30)  # Already started
    end_time = start_time + timedelta(hours=1)

    meeting = meeting_service.create_meeting(
        db=db,
        title="Test Meeting",
        organizer_id=test_user.id,
        company_id=test_company.id,
        start_time=start_time,
        end_time=end_time,
        participant_ids=[test_user2.id]
    )

    # End meeting
    meeting_service.end_meeting(db, meeting.id, test_user.id)

    # Refresh meeting from DB
    from app.crud.crud_meetings import get_meeting
    updated_meeting = get_meeting(db, meeting.id, test_company.id)
    assert updated_meeting.status.value == "ENDED"
    assert updated_meeting.end_time is not None

def test_get_meetings_for_user(db: Session, test_company: Company, test_user: User, test_user2: User):
    """Test getting meetings for a user"""
    # Create meeting
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    meeting_service.create_meeting(
        db=db,
        title="Test Meeting",
        organizer_id=test_user.id,
        company_id=test_company.id,
        start_time=start_time,
        end_time=end_time,
        participant_ids=[test_user2.id]
    )

    # Get meetings for user2
    meetings = meeting_service.get_meetings_for_user(db, test_user2.id, test_company.id)
    assert len(meetings) >= 1
    assert any(m.title == "Test Meeting" for m in meetings)
