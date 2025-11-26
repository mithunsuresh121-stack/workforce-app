#!/usr/bin/env python3
"""
Unit tests for notification preferences CRUD operations
"""

import pytest
from sqlalchemy.orm import Session
from app.models.notification_preferences import NotificationPreferences
from app.models.user import User
from app.models.company import Company
from app.crud_notification_preferences import (
    get_user_preferences,
    create_user_preferences,
    update_user_preferences,
    delete_user_preferences,
    get_or_create_user_preferences,
    should_send_push_notification,
)
from app.db import SessionLocal


# -------------------------------------------------------------------
# Test Fixtures: Create valid company and user for FK integrity
# -------------------------------------------------------------------
@pytest.fixture
def db():
    """Database session fixture"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_company(db):
    import uuid
    unique_name = f"Test Company {uuid.uuid4().hex[:8]}"
    unique_domain = f"testco{uuid.uuid4().hex[:8]}.com"
    company = Company(name=unique_name, domain=unique_domain, contact_email="test@testco.com")
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@pytest.fixture
def test_company2(db):
    company = Company(name="Test Company 2", domain="testco2.com", contact_email="test2@testco2.com")
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture
def test_user(db, test_company):
    import uuid
    unique_email = f"testuser{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=unique_email,
        hashed_password="dummyhash",
        company_id=test_company.id,
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_get_user_preferences(db):
    """Test getting user preferences"""
    # Test with non-existent user
    prefs = get_user_preferences(db, user_id=999, company_id=78)
    assert prefs is None

    # Test with existing user (using user 302)
    prefs = get_user_preferences(db, user_id=302, company_id=78)
    if prefs:
        assert isinstance(prefs, NotificationPreferences)
        assert prefs.user_id == 302
        assert prefs.company_id == 78
        assert "mute_all" in prefs.preferences

def test_create_user_preferences(db: Session, test_user, test_company):
    custom_prefs = {
        "mute_all": False,
        "digest_mode": "immediate",
        "push_enabled": True,
        "notification_types": {
            "TASK_ASSIGNED": True,
            "SHIFT_SCHEDULED": True,
            "SYSTEM_MESSAGE": True,
            "ADMIN_MESSAGE": True
        }
    }
    prefs = create_user_preferences(db, user_id=test_user.id, company_id=test_company.id, preferences=custom_prefs)
    assert prefs.user_id == test_user.id
    assert prefs.company_id == test_company.id
    assert prefs.preferences["push_enabled"] is True

def test_update_user_preferences(db: Session, test_user, test_company):
    # First create preferences
    prefs = create_user_preferences(db, user_id=test_user.id, company_id=test_company.id)

    # Update them
    updated_prefs = {
        "mute_all": True,
        "digest_mode": "daily",
        "push_enabled": False,
        "notification_types": {
            "TASK_ASSIGNED": False,
            "SHIFT_SCHEDULED": True,
            "SYSTEM_MESSAGE": True,
            "ADMIN_MESSAGE": False
        }
    }

    result = update_user_preferences(db, user_id=test_user.id, company_id=test_company.id, preferences=updated_prefs)
    assert result is not None
    assert result.preferences["mute_all"] is True
    assert result.preferences["digest_mode"] == "daily"
    assert result.preferences["notification_types"]["SHIFT_SCHEDULED"] is True

def test_delete_user_preferences(db: Session, test_user, test_company):
    # Create preferences
    prefs = create_user_preferences(db, user_id=test_user.id, company_id=test_company.id)

    # Delete them
    success = delete_user_preferences(db, user_id=test_user.id, company_id=test_company.id)
    assert success is True

    # Verify deletion
    deleted_prefs = db.query(NotificationPreferences).filter_by(user_id=test_user.id).first()
    assert deleted_prefs is None

def test_get_or_create_user_preferences(db: Session, test_user, test_company):
    prefs = get_or_create_user_preferences(db=db, user_id=test_user.id, company_id=test_company.id)
    assert prefs.user_id == test_user.id
    assert prefs.company_id == test_company.id

def test_should_send_notification(db: Session, test_user, test_company):
    # Test with no preferences (should send)
    should_send = should_send_push_notification(db, user_id=999, company_id=78, notification_type="TASK_ASSIGNED")
    assert should_send is True

    # Test with push_enabled = False
    prefs = get_or_create_user_preferences(db, user_id=test_user.id, company_id=test_company.id)
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": False, "notification_types": {"TASK_ASSIGNED": True}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is False

    # Test with push_enabled = True and type enabled
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": True}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is True

    # Test with push_enabled = True but type disabled
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": False}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is False

    # Reset to default
    prefs.preferences = {
        "mute_all": False,
        "digest_mode": "immediate",
        "push_enabled": True,
        "notification_types": {
            "TASK_ASSIGNED": True,
            "SHIFT_SCHEDULED": True,
            "SYSTEM_MESSAGE": True,
            "ADMIN_MESSAGE": True
        }
    }
    db.commit()

def test_should_send_push_notification(db: Session, test_user, test_company):
    # Test with no preferences (should send)
    should_send = should_send_push_notification(db, user_id=999, company_id=78, notification_type="TASK_ASSIGNED")
    assert should_send is True

    # Test with push_enabled = False
    prefs = get_or_create_user_preferences(db, user_id=test_user.id, company_id=test_company.id)
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": False, "notification_types": {"TASK_ASSIGNED": True}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is False

    # Test with push_enabled = True and type enabled
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": True}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is True

    # Test with push_enabled = True but type disabled
    prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": False}}
    db.commit()
    should_send = should_send_push_notification(db, user_id=test_user.id, company_id=test_company.id, notification_type="TASK_ASSIGNED")
    assert should_send is False

    # Reset to default
    prefs.preferences = {
        "mute_all": False,
        "digest_mode": "immediate",
        "push_enabled": True,
        "notification_types": {
            "TASK_ASSIGNED": True,
            "SHIFT_SCHEDULED": True,
            "SYSTEM_MESSAGE": True,
            "ADMIN_MESSAGE": True
        }
    }
    db.commit()

if __name__ == "__main__":
    pytest.main([__file__])
