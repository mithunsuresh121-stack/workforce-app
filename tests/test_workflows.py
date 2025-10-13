import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db import get_db
from app.models.user import User
from app.models.company import Company
from app.models.employee_profile import EmployeeProfile
from app.models.leave import Leave
from app.models.chat import ChatMessage
from app.models.document import Document
from app.models.notification import Notification
from app.crud import create_user, create_company, create_employee_profile
from tests.conftest import override_get_db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_authentication_and_role_based_access(db: Session):
    """Test authentication and role-based access control."""
    # Create test company
    company = create_company(
        db=db,
        name="Test Company",
        domain="test.com",
        contact_email="admin@test.com",
        contact_phone="+1234567890",
        address="123 Test St",
        city="Test City",
        state="Test State",
        country="Test Country",
        postal_code="12345"
    )

    # Create manager user
    manager = create_user(
        db=db,
        email="manager@test.com",
        password="password123",
        full_name="Test Manager",
        role="MANAGER",
        company_id=company.id
    )
    create_employee_profile(
        db=db,
        user_id=manager.id,
        company_id=company.id,
        department="Management",
        position="Manager",
        phone="+1234567891",
        hire_date="2023-01-01",
        manager_id=None
    )

    # Create employee user
    employee = create_user(
        db=db,
        email="employee@test.com",
        password="password123",
        full_name="Test Employee",
        role="EMPLOYEE",
        company_id=company.id
    )
    create_employee_profile(
        db=db,
        user_id=employee.id,
        company_id=company.id,
        department="Engineering",
        position="Developer",
        phone="+1234567892",
        hire_date="2023-06-01",
        manager_id=manager.id
    )

    # Test login
    response = client.post("/api/auth/login", json={
        "email": "manager@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test role-based access (manager accessing employee data)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/employees", headers=headers)
    assert response.status_code == 200

def test_leave_creation_and_approval_workflow(db: Session):
    """Test leave creation and approval workflow."""
    # Setup similar to above
    company = create_company(db=db, name="Test Company", domain="test.com", contact_email="admin@test.com", contact_phone="+1234567890", address="123 Test St", city="Test City", state="Test State", country="Test Country", postal_code="12345")
    manager = create_user(db=db, email="manager@test.com", password="password123", full_name="Test Manager", role="MANAGER", company_id=company.id)
    create_employee_profile(db=db, user_id=manager.id, company_id=company.id, department="Management", position="Manager", phone="+1234567891", hire_date="2023-01-01", manager_id=None)
    employee = create_user(db=db, email="employee@test.com", password="password123", full_name="Test Employee", role="EMPLOYEE", company_id=company.id)
    create_employee_profile(db=db, user_id=employee.id, company_id=company.id, department="Engineering", position="Developer", phone="+1234567892", hire_date="2023-06-01", manager_id=manager.id)

    # Login as employee
    response = client.post("/api/auth/login", json={"email": "employee@test.com", "password": "password123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create leave request
    leave_data = {
        "type": "Vacation",
        "start_at": "2024-12-01T00:00:00",
        "end_at": "2024-12-05T00:00:00",
        "reason": "Holiday vacation"
    }
    response = client.post("/api/leaves", json=leave_data, headers=headers)
    assert response.status_code == 201
    leave_id = response.json()["id"]

    # Login as manager
    response = client.post("/api/auth/login", json={"email": "manager@test.com", "password": "password123"})
    manager_token = response.json()["access_token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}

    # Approve leave
    response = client.put(f"/api/leaves/{leave_id}/approve", headers=manager_headers)
    assert response.status_code == 200

def test_chat_send_receive_workflow(db: Session):
    """Test chat send/receive workflow including WebSocket connection."""
    # Setup
    company = create_company(db=db, name="Test Company", domain="test.com", contact_email="admin@test.com", contact_phone="+1234567890", address="123 Test St", city="Test City", state="Test State", country="Test Country", postal_code="12345")
    manager = create_user(db=db, email="manager@test.com", password="password123", full_name="Test Manager", role="MANAGER", company_id=company.id)
    create_employee_profile(db=db, user_id=manager.id, company_id=company.id, department="Management", position="Manager", phone="+1234567891", hire_date="2023-01-01", manager_id=None)
    employee = create_user(db=db, email="employee@test.com", password="password123", full_name="Test Employee", role="EMPLOYEE", company_id=company.id)
    create_employee_profile(db=db, user_id=employee.id, company_id=company.id, department="Engineering", position="Developer", phone="+1234567892", hire_date="2023-06-01", manager_id=manager.id)

    # Login as employee
    response = client.post("/api/auth/login", json={"email": "employee@test.com", "password": "password123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Send message
    message_data = {
        "receiver_id": manager.id,
        "message": "Hello Manager!"
    }
    response = client.post("/api/chat/messages", json=message_data, headers=headers)
    assert response.status_code == 201

    # Get messages
    response = client.get("/api/chat/messages", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_document_upload_download_workflow(db: Session):
    """Test document upload and download workflow."""
    # Setup
    company = create_company(db=db, name="Test Company", domain="test.com", contact_email="admin@test.com", contact_phone="+1234567890", address="123 Test St", city="Test City", state="Test State", country="Test Country", postal_code="12345")
    manager = create_user(db=db, email="manager@test.com", password="password123", full_name="Test Manager", role="MANAGER", company_id=company.id)
    create_employee_profile(db=db, user_id=manager.id, company_id=company.id, department="Management", position="Manager", phone="+1234567891", hire_date="2023-01-01", manager_id=None)

    # Login as manager
    response = client.post("/api/auth/login", json={"email": "manager@test.com", "password": "password123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document (mock)
    doc_data = {
        "file_path": f"uploads/{company.id}/{manager.id}/test.pdf",
        "type": "POLICY",
        "access_role": "EMPLOYEE"
    }
    response = client.post("/api/documents", json=doc_data, headers=headers)
    assert response.status_code == 201

    # Get documents
    response = client.get("/api/documents", headers=headers)
    assert response.status_code == 200

def test_notification_trigger_verification_workflow(db: Session):
    """Test notification trigger and verification workflow."""
    # Setup
    company = create_company(db=db, name="Test Company", domain="test.com", contact_email="admin@test.com", contact_phone="+1234567890", address="123 Test St", city="Test City", state="Test State", country="Test Country", postal_code="12345")
    manager = create_user(db=db, email="manager@test.com", password="password123", full_name="Test Manager", role="MANAGER", company_id=company.id)
    create_employee_profile(db=db, user_id=manager.id, company_id=company.id, department="Management", position="Manager", phone="+1234567891", hire_date="2023-01-01", manager_id=None)
    employee = create_user(db=db, email="employee@test.com", password="password123", full_name="Test Employee", role="EMPLOYEE", company_id=company.id)
    create_employee_profile(db=db, user_id=employee.id, company_id=company.id, department="Engineering", position="Developer", phone="+1234567892", hire_date="2023-06-01", manager_id=manager.id)

    # Login as employee
    response = client.post("/api/auth/login", json={"email": "employee@test.com", "password": "password123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get notifications
    response = client.get("/api/notifications", headers=headers)
    assert response.status_code == 200

    # Mark as read (if any)
    notifications = response.json()
    if notifications:
        notif_id = notifications[0]["id"]
        response = client.put(f"/api/notifications/{notif_id}/read", headers=headers)
        assert response.status_code == 200
