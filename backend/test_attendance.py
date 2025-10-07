import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.db import get_db, SessionLocal
from app.models.user import User, Role
from app.models.company import Company
from app.crud import create_user, create_company
from datetime import datetime, timezone

client = TestClient(app)

@pytest.fixture
def db():
    """Database session fixture"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

def test_clock_in_with_geo(db: Session):
    import time
    # Create test company and user with unique domain
    unique_id = str(int(time.time()))
    company = create_company(db, f"Test Company Clock In {unique_id}", f"test{unique_id}-clockin.com", contact_email=f"test{unique_id}@test.com")
    user = create_user(db, f"test{unique_id}-attendance@example.com", "password", "Test User", Role.EMPLOYEE, company.id)

    # Login to get token
    response = client.post("/api/auth/login", json={"email": f"test{unique_id}-attendance@example.com", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Clock in with geo data
    response = client.post(
        "/api/attendance/clock-in",
        json={"employee_id": user.id, "notes": "Test clock in"},
        params={"lat": 37.7749, "lng": -122.4194, "ip_address": "192.168.1.1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == user.id
    assert data["status"] == "CLOCKED_IN"
    assert data["lat"] == 37.7749
    assert data["lng"] == -122.4194
    assert data["ip_address"] == "192.168.1.1"

def test_clock_out_with_geo(db: Session):
    # Create test company and user
    company = create_company(db, "Test Company Clock Out 2", "test2-clockout.com", contact_email="test2@test.com")
    user = create_user(db, "test2-attendance@example.com", "password", "Test User 2", Role.EMPLOYEE, company.id)

    # Login
    response = client.post("/api/auth/login", json={"email": "test2-attendance@example.com", "password": "password"})
    token = response.json()["access_token"]

    # Clock in first
    response = client.post(
        "/api/attendance/clock-in",
        json={"employee_id": user.id, "notes": "Test clock in"},
        headers={"Authorization": f"Bearer {token}"}
    )
    attendance_id = response.json()["id"]

    # Clock out with geo
    response = client.put(
        "/api/attendance/clock-out",
        json={"attendance_id": attendance_id, "employee_id": user.id, "notes": "Test clock out"},
        params={"lat": 37.7749, "lng": -122.4194, "ip_address": "192.168.1.1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CLOCKED_OUT"
    assert data["total_hours"] is not None
    assert data["lat"] == 37.7749

def test_get_attendance_history(db: Session):
    # Create test company and user
    company = create_company(db, "Test Company History 3", "test3-history.com", contact_email="test3@test.com")
    user = create_user(db, "test3-attendance@example.com", "password", "Test User 3", Role.EMPLOYEE, company.id)

    # Login
    response = client.post("/api/auth/login", json={"email": "test3-attendance@example.com", "password": "password"})
    token = response.json()["access_token"]

    # Get history
    response = client.get("/api/attendance/history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
