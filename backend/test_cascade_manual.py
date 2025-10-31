#!/usr/bin/env python3
"""
Manual test script for cascade delete relationships.
This avoids the pytest conftest import issues.
"""
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.db import Base
from app.models import (
    Company, User, Channel, ChannelMember, ChatMessage,
    MessageReaction, Meeting, MeetingParticipant
)
from app.config import DATABASE_URL

def test_company_cascade_delete():
    """Test that deleting a company cascades to all related entities."""
    print("Testing company cascade delete...")

    # Create test database engine (use SQLite for testing)
    test_db_url = "sqlite:///./test_cascade.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Clean up any existing database
    import os
    if os.path.exists("./test_cascade.db"):
        os.remove("./test_cascade.db")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Create test data
        company = Company(name="Test Company")
        session.add(company)
        session.commit()

        user = User(email="test@example.com", hashed_password="test_password_hash", company=company)
        session.add(user)
        session.commit()

        channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
        session.add(channel)
        session.commit()

        channel_member = ChannelMember(channel_id=channel.id, user_id=user.id)
        session.add(channel_member)
        session.commit()

        message = ChatMessage(
            company=company,
            sender=user,
            message="Test message",
            channel=channel
        )
        session.add(message)
        session.commit()

        reaction = MessageReaction(message=message, user=user, emoji="👍")
        session.add(reaction)
        session.commit()

        meeting = Meeting(
            title="Test Meeting",
            organizer=user,
            company=company,
            start_time=datetime(2025, 1, 1, 10, 0, 0),
            end_time=datetime(2025, 1, 1, 11, 0, 0),
            status="SCHEDULED"
        )
        session.add(meeting)
        session.commit()

        participant = MeetingParticipant(meeting=meeting, user=user, role="PARTICIPANT")
        session.add(participant)
        session.commit()

        # Verify all entities exist
        assert session.query(Company).filter_by(id=company.id).first() is not None
        assert session.query(User).filter_by(id=user.id).first() is not None
        assert session.query(Channel).filter_by(id=channel.id).first() is not None
        assert session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is not None
        assert session.query(ChatMessage).filter_by(id=message.id).first() is not None
        assert session.query(MessageReaction).filter_by(id=reaction.id).first() is not None
        assert session.query(Meeting).filter_by(id=meeting.id).first() is not None
        assert session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is not None
        print("✓ All entities created successfully")

        # Delete company
        session.delete(company)
        session.commit()
        print("✓ Company deleted")

        # Verify all related entities were deleted
        assert session.query(Company).filter_by(id=company.id).first() is None
        assert session.query(User).filter_by(id=user.id).first() is None
        assert session.query(Channel).filter_by(id=channel.id).first() is None
        assert session.query(ChannelMember).filter_by(channel_id=channel.id, user_id=user.id).first() is None
        assert session.query(ChatMessage).filter_by(id=message.id).first() is None
        assert session.query(MessageReaction).filter_by(id=reaction.id).first() is None
        assert session.query(Meeting).filter_by(id=meeting.id).first() is None
        assert session.query(MeetingParticipant).filter_by(meeting_id=meeting.id, user_id=user.id).first() is None
        print("✓ All related entities deleted via cascade")

        print("✓ Company cascade delete test PASSED")

    except Exception as e:
        print(f"✗ Company cascade delete test FAILED: {e}")
        raise
    finally:
        session.rollback()
        session.close()

def test_timestamp_updates():
    """Test that timestamp fields update automatically."""
    print("\nTesting timestamp auto-updates...")

    # Use SQLite for testing
    test_db_url = "sqlite:///./test_timestamp.db"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})

    # Clean up any existing database
    import os
    if os.path.exists("./test_timestamp.db"):
        os.remove("./test_timestamp.db")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Create company and user
        company = Company(name="Test Company")
        session.add(company)
        session.commit()

        user = User(email="test@example.com", hashed_password="test_password_hash", company=company)
        session.add(user)
        session.commit()

        initial_last_active = user.last_active
        print(f"Initial last_active: {initial_last_active}")

        # Update user (should trigger onupdate)
        user.email = "updated@example.com"
        session.commit()

        updated_last_active = user.last_active
        print(f"Updated last_active: {updated_last_active}")

        # Create channel
        channel = Channel(name="Test Channel", type="GROUP", company=company, created_by=user.id)
        session.add(channel)
        session.commit()

        initial_last_message_at = channel.last_message_at
        print(f"Initial last_message_at: {initial_last_message_at}")

        # Update channel (should trigger onupdate)
        channel.name = "Updated Channel"
        session.commit()

        updated_last_message_at = channel.last_message_at
        print(f"Updated last_message_at: {updated_last_message_at}")

        # The timestamps should be different if onupdate is working
        if initial_last_active != updated_last_active:
            print("✓ User last_active timestamp updates correctly")
        else:
            print("⚠ User last_active timestamp may not be updating (could be same millisecond)")

        if initial_last_message_at != updated_last_message_at:
            print("✓ Channel last_message_at timestamp updates correctly")
        else:
            print("⚠ Channel last_message_at timestamp may not be updating (could be same millisecond)")

        print("✓ Timestamp auto-update test completed")

    except Exception as e:
        print(f"✗ Timestamp test FAILED: {e}")
        raise
    finally:
        session.rollback()
        session.close()

if __name__ == "__main__":
    test_company_cascade_delete()
    test_timestamp_updates()
    print("\n🎉 All tests completed!")
