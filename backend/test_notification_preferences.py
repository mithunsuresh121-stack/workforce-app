#!/usr/bin/env python3
"""
Unit tests for notification preferences CRUD operations
"""

import pytest
from sqlalchemy.orm import Session
from app.crud_notification_preferences import (
    get_user_preferences,
    create_user_preferences,
    update_user_preferences,
    delete_user_preferences,
    get_or_create_user_preferences,
    should_send_notification
)
from app.models.notification_preferences import NotificationPreferences
from app.db import SessionLocal

def test_get_user_preferences():
    """Test getting user preferences"""
    db: Session = SessionLocal()
    try:
        # Test with non-existent user
        prefs = get_user_preferences(db, user_id=999, company_id=1)
        assert prefs is None

        # Test with existing user (assuming user 1 exists)
        prefs = get_user_preferences(db, user_id=1, company_id=1)
        if prefs:
            assert isinstance(prefs, NotificationPreferences)
            assert prefs.user_id == 1
            assert prefs.company_id == 1
            assert "mute_all" in prefs.preferences
    finally:
        db.close()

def test_create_user_preferences():
    """Test creating user preferences"""
    db: Session = SessionLocal()
    try:
        custom_prefs = {
            "mute_all": True,
            "digest_mode": "weekly",
            "push_enabled": False,
            "notification_types": {
                "TASK_ASSIGNED": False,
                "SHIFT_SCHEDULED": True,
                "SYSTEM_MESSAGE": False,
                "ADMIN_MESSAGE": True
            }
        }

        prefs = create_user_preferences(db, user_id=2, company_id=1, preferences=custom_prefs)
        assert isinstance(prefs, NotificationPreferences)
        assert prefs.user_id == 2
        assert prefs.company_id == 1
        assert prefs.preferences["mute_all"] is True
        assert prefs.preferences["digest_mode"] == "weekly"
        assert prefs.preferences["push_enabled"] is False
        assert prefs.preferences["notification_types"]["TASK_ASSIGNED"] is False

        # Clean up
        db.delete(prefs)
        db.commit()
    finally:
        db.close()

def test_update_user_preferences():
    """Test updating user preferences"""
    db: Session = SessionLocal()
    try:
        # First create preferences
        prefs = create_user_preferences(db, user_id=3, company_id=1)

        # Update them
        updated_prefs = {
            "mute_all": False,
            "digest_mode": "daily",
            "push_enabled": True,
            "notification_types": {
                "TASK_ASSIGNED": True,
                "SHIFT_SCHEDULED": False,
                "SYSTEM_MESSAGE": True,
                "ADMIN_MESSAGE": False
            }
        }

        result = update_user_preferences(db, user_id=3, company_id=1, preferences=updated_prefs)
        assert result is not None
        assert result.preferences["mute_all"] is False
        assert result.preferences["digest_mode"] == "daily"
        assert result.preferences["notification_types"]["SHIFT_SCHEDULED"] is False

        # Clean up
        db.delete(result)
        db.commit()
    finally:
        db.close()

def test_delete_user_preferences():
    """Test deleting user preferences"""
    db: Session = SessionLocal()
    try:
        # Create preferences
        prefs = create_user_preferences(db, user_id=4, company_id=1)

        # Delete them
        success = delete_user_preferences(db, user_id=4, company_id=1)
        assert success is True

        # Verify deletion
        deleted_prefs = get_user_preferences(db, user_id=4, company_id=1)
        assert deleted_prefs is None
    finally:
        db.close()

def test_get_or_create_user_preferences():
    """Test get_or_create functionality"""
    db: Session = SessionLocal()
    try:
        # Test with non-existent user - should create default
        prefs = get_or_create_user_preferences(db, user_id=5, company_id=1)
        assert isinstance(prefs, NotificationPreferences)
        assert prefs.user_id == 5
        assert prefs.company_id == 1
        assert prefs.preferences["mute_all"] is False  # Default
        assert prefs.preferences["digest_mode"] == "immediate"  # Default

        # Test with existing user - should return existing
        prefs2 = get_or_create_user_preferences(db, user_id=5, company_id=1)
        assert prefs2.id == prefs.id

        # Clean up
        db.delete(prefs)
        db.commit()
    finally:
        db.close()

def test_should_send_notification():
    """Test notification sending logic"""
    db: Session = SessionLocal()
    try:
        # Test with no preferences (should send)
        should_send = should_send_notification(db, user_id=999, company_id=1, notification_type="TASK_ASSIGNED")
        assert should_send is True

        # Test with mute_all = True
        prefs = get_or_create_user_preferences(db, user_id=1, company_id=1)
        prefs.preferences = {"mute_all": True, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": True}}
        db.commit()
        should_send = should_send_notification(db, user_id=1, company_id=1, notification_type="TASK_ASSIGNED")
        assert should_send is False

        # Test with digest_mode != immediate
        prefs.preferences = {"mute_all": False, "digest_mode": "daily", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": True}}
        db.commit()
        should_send = should_send_notification(db, user_id=1, company_id=1, notification_type="TASK_ASSIGNED")
        assert should_send is False

        # Test with type disabled
        prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": False}}
        db.commit()
        should_send = should_send_notification(db, user_id=1, company_id=1, notification_type="TASK_ASSIGNED")
        assert should_send is False

        # Test with type enabled
        prefs.preferences = {"mute_all": False, "digest_mode": "immediate", "push_enabled": True, "notification_types": {"TASK_ASSIGNED": True}}
        db.commit()
        should_send = should_send_notification(db, user_id=1, company_id=1, notification_type="TASK_ASSIGNED")
        assert should_send is True

        # Reset to default (don't delete since it might be used by other tests)
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
    finally:
        db.close()

if __name__ == "__main__":
    pytest.main([__file__])
