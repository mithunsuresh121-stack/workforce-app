import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.db import Base
from app.models import (
    Company, User, Channel, ChannelMember, ChatMessage,
    MessageReaction, Meeting, MeetingParticipant
)
from app.config import settings


@pytest.fixture(scope="module")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_company_cascade_delete(db_session):
    """Test that deleting a company cascades to all related entities."""
    # Create test data
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()

    user = User(email="test@example.com", company=company)
    db_session.add(user)
    db_session.commit()

    channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
    db_session.add(channel)
    db_session.commit()

    channel_member = ChannelMember(channel_id=channel.id, user_id=user.id)
    db_session.add(channel_member)
    db_session.commit()

    message = ChatMessage(
        company=company,
        sender=user,
        message="Test message",
        channel=channel
    )
    db_session.add(message)
    db_session.commit()

    reaction = MessageReaction(message=message, user=user, emoji="👍")
    db_session.add(reaction)
    db_session.commit()

    meeting = Meeting(
        title="Test Meeting",
        organizer=user,
        company=company,
        start_time="2025-01-01T10:00:00",
        end_time="2025-01-01T11:00:00",
        status="SCHEDULED"
    )
    db_session.add(meeting)
    db_session.commit()

    participant = MeetingParticipant(meeting=meeting, user=user, role="PARTICIPANT")
    db_session.add(participant)
    db_session.commit()

    # Verify all entities exist
    assert db_session.query(Company).filter_by(id=company.id).first() is not None
    assert db_session.query(User).filter_by(id=user.id).first() is not None
    assert db_session.query(Channel).filter_by(id=channel.id).first() is not None
    assert db_session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is not None
    assert db_session.query(ChatMessage).filter_by(id=message.id).first() is not None
    assert db_session.query(MessageReaction).filter_by(id=reaction.id).first() is not None
    assert db_session.query(Meeting).filter_by(id=meeting.id).first() is not None
    assert db_session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is not None

    # Delete company
    db_session.delete(company)
    db_session.commit()

    # Verify all related entities were deleted
    assert db_session.query(Company).filter_by(id=company.id).first() is None
    assert db_session.query(User).filter_by(id=user.id).first() is None
    assert db_session.query(Channel).filter_by(id=channel.id).first() is None
    assert db_session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is None
    assert db_session.query(ChatMessage).filter_by(id=message.id).first() is None
    assert db_session.query(MessageReaction).filter_by(id=reaction.id).first() is None
    assert db_session.query(Meeting).filter_by(id=meeting.id).first() is None
    assert db_session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is None


def test_user_cascade_delete(db_session):
    """Test that deleting a user cascades to related entities."""
    # Create test data
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()

    user = User(email="test@example.com", company=company)
    db_session.add(user)
    db_session.commit()

    channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
    db_session.add(channel)
    db_session.commit()

    channel_member = ChannelMember(channel_id=channel.id, user_id=user.id)
    db_session.add(channel_member)
    db_session.commit()

    message = ChatMessage(
        company=company,
        sender=user,
        message="Test message",
        channel=channel
    )
    db_session.add(message)
    db_session.commit()

    reaction = MessageReaction(message=message, user=user, emoji="👍")
    db_session.add(reaction)
    db_session.commit()

    meeting = Meeting(
        title="Test Meeting",
        organizer=user,
        company=company,
        start_time="2025-01-01T10:00:00",
        end_time="2025-01-01T11:00:00",
        status="SCHEDULED"
    )
    db_session.add(meeting)
    db_session.commit()

    participant = MeetingParticipant(meeting=meeting, user=user, role="PARTICIPANT")
    db_session.add(participant)
    db_session.commit()

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify user-related entities were deleted
    assert db_session.query(User).filter_by(id=user.id).first() is None
    assert db_session.query(Channel).filter_by(id=channel.id).first() is None  # Created by user
    assert db_session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is None
    assert db_session.query(ChatMessage).filter_by(id=message.id).first() is None  # Sent by user
    assert db_session.query(MessageReaction).filter_by(id=reaction.id).first() is None  # Created by user
    assert db_session.query(Meeting).filter_by(id=meeting.id).first() is None  # Organized by user
    assert db_session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is None

    # Company should still exist
    assert db_session.query(Company).filter_by(id=company.id).first() is not None


def test_channel_cascade_delete(db_session):
    """Test that deleting a channel cascades to related entities."""
    # Create test data
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()

    user = User(email="test@example.com", company=company)
    db_session.add(user)
    db_session.commit()

    channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
    db_session.add(channel)
    db_session.commit()

    channel_member = ChannelMember(channel_id=channel.id, user_id=user.id)
    db_session.add(channel_member)
    db_session.commit()

    message = ChatMessage(
        company=company,
        sender=user,
        message="Test message",
        channel=channel
    )
    db_session.add(message)
    db_session.commit()

    reaction = MessageReaction(message=message, user=user, emoji="👍")
    db_session.add(reaction)
    db_session.commit()

    # Delete channel
    db_session.delete(channel)
    db_session.commit()

    # Verify channel-related entities were deleted
    assert db_session.query(Channel).filter_by(id=channel.id).first() is None
    assert db_session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is None
    assert db_session.query(ChatMessage).filter_by(id=message.id).first() is None
    assert db_session.query(MessageReaction).filter_by(id=reaction.id).first() is None

    # User and company should still exist
    assert db_session.query(User).filter_by(id=user.id).first() is not None
    assert db_session.query(Company).filter_by(id=company.id).first() is not None


def test_message_cascade_delete(db_session):
    """Test that deleting a message cascades to reactions."""
    # Create test data
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()

    user = User(email="test@example.com", company=company)
    db_session.add(user)
    db_session.commit()

    channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
    db_session.add(channel)
    db_session.commit()

    message = ChatMessage(
        company=company,
        sender=user,
        message="Test message",
        channel=channel
    )
    db_session.add(message)
    db_session.commit()

    reaction = MessageReaction(message=message, user=user, emoji="👍")
    db_session.add(reaction)
    db_session.commit()

    # Delete message
    db_session.delete(message)
    db_session.commit()

    # Verify message and reactions were deleted
    assert db_session.query(ChatMessage).filter_by(id=message.id).first() is None
    assert db_session.query(MessageReaction).filter_by(id=reaction.id).first() is None

    # Other entities should still exist
    assert db_session.query(User).filter_by(id=user.id).first() is not None
    assert db_session.query(Channel).filter_by(id=channel.id).first() is not None
    assert db_session.query(Company).filter_by(id=company.id).first() is not None


def test_meeting_cascade_delete(db_session):
    """Test that deleting a meeting cascades to participants."""
    # Create test data
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()

    user = User(email="test@example.com", company=company)
    db_session.add(user)
    db_session.commit()

    meeting = Meeting(
        title="Test Meeting",
        organizer=user,
        company=company,
        start_time="2025-01-01T10:00:00",
        end_time="2025-01-01T11:00:00",
        status="SCHEDULED"
    )
    db_session.add(meeting)
    db_session.commit()

    participant = MeetingParticipant(meeting=meeting, user=user, role="PARTICIPANT")
    db_session.add(participant)
    db_session.commit()

    # Delete meeting
    db_session.delete(meeting)
    db_session.commit()

    # Verify meeting and participants were deleted
    assert db_session.query(Meeting).filter_by(id=meeting.id).first() is None
    assert db_session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is None

    # User and company should still exist
    assert db_session.query(User).filter_by(id=user.id).first() is not None
    assert db_session.query(Company).filter_by(id=company.id).first() is not None


def test_foreign_key_constraints(db_session):
    """Test that foreign key constraints prevent invalid data."""
    # Try to create a user with non-existent company
    with pytest.raises(Exception):  # Should raise IntegrityError
        user = User(email="test@example.com", company_id=99999)
        db_session.add(user)
        db_session.commit()

    # Try to create a channel with non-existent company
    with pytest.raises(Exception):  # Should raise IntegrityError
        channel = Channel(name="Test", type="GROUP", company_id=99999, created_by=1)
        db_session.add(channel)
        db_session.commit()

    # Try to create a message with non-existent sender
    with pytest.raises(Exception):  # Should raise IntegrityError
        message = ChatMessage(company_id=1, sender_id=99999, message="Test")
        db_session.add(message)
        db_session.commit()
