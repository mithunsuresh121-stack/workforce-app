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

def test_create_leave_request(db: Session):
    import time
    unique_id = str(int(time.time()))
    # Create test company and user with unique domain and email
    company = create_company(db, f"Test Company {unique_id}", f"test{unique_id}.com", contact_email=f"test{unique_id}@test.com")
    user = create_user(db, f"test{unique_id}@example.com", "password", "Test User", Role.EMPLOYEE, company.id)

    # Login to get token
    response = client.post("/api/auth/login", json={"email": f"test{unique_id}@example.com", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create leave request
    leave_data = {
        "company_id": company.id,
        "employee_id": user.id,
        "type": "ANNUAL",
        "start_at": "2024-06-01T00:00:00Z",
        "end_at": "2024-06-05T00:00:00Z",
        "reason": "Vacation time",
        "status": "PENDING"
    }
    response = client.post("/api/leaves/request", json=leave_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "ANNUAL"
    assert data["status"] == "PENDING"
    assert data["reason"] == "Vacation time"

def test_approve_leave_request(db: Session):
    # Create test company and users
    company = create_company(db, "Test Company 2", "test2.com")
    employee = create_user(db, "employee@example.com", "password", "Employee", Role.Employee, company.id)
    manager = create_user(db, "manager@example.com", "password", "Manager", Role.Manager, company.id)

    # Login as employee and create leave
    response = client.post("/api/auth/login", json={"email": "employee@example.com", "password": "password"})
    token_employee = response.json()["access_token"]

    leave_data = {
        "company_id": company.id,
        "employee_id": employee.id,
        "type": "SICK",
        "start_at": "2024-06-10T00:00:00Z",
        "end_at": "2024-06-10T00:00:00Z",
        "reason": "Feeling unwell",
        "status": "PENDING"
    }
    response = client.post("/api/leaves/request", json=leave_data, headers={"Authorization": f"Bearer {token_employee}"})
    leave_id = response.json()["id"]

    # Login as manager and approve
    response = client.post("/api/auth/login", json={"email": "manager@example.com", "password": "password"})
    token_manager = response.json()["access_token"]

    response = client.put(f"/api/leaves/{leave_id}/approve", headers={"Authorization": f"Bearer {token_manager}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert data["approver_id"] == manager.id

def test_get_pending_leaves(db: Session):
    # Create test company and users
    company = create_company(db, "Test Company 3", "test3.com", contact_email="test3@test.com")
    employee = create_user(db, "employee2@example.com", "password", "Employee2", Role.EMPLOYEE, company.id)
    manager = create_user(db, "manager2@example.com", "password", "Manager2", Role.MANAGER, company.id)

    # Login as employee and create leave
    response = client.post("/api/auth/login", json={"email": "employee2@example.com", "password": "password"})
    token_employee = response.json()["access_token"]

    leave_data = {
        "company_id": company.id,
        "employee_id": employee.id,
        "type": "PERSONAL",
        "start_at": "2024-06-15T00:00:00Z",
        "end_at": "2024-06-15T00:00:00Z",
        "reason": "Personal matters",
        "status": "PENDING"
    }
    client.post("/api/leaves/request", json=leave_data, headers={"Authorization": f"Bearer {token_employee}"})

    # Login as manager and get pending leaves
    response = client.post("/api/auth/login", json={"email": "manager2@example.com", "password": "password"})
    token_manager = response.json()["access_token"]

    response = client.get("/api/leaves/pending", headers={"Authorization": f"Bearer {token_manager}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["status"] == "PENDING"

def test_get_my_leaves(db: Session):
    # Create test company and user
    company = create_company(db, "Test Company 4", "test4.com", contact_email="test4@test.com")
    user = create_user(db, "test4@example.com", "password", "Test User 4", Role.EMPLOYEE, company.id)

    # Login
    response = client.post("/api/auth/login", json={"email": "test4@example.com", "password": "password"})
    token = response.json()["access_token"]

    # Get my leaves
    response = client.get("/api/leaves/my", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
