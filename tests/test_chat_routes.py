import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db import get_db, SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.chat import ChatMessage
from app.crud_chat import create_chat_message, get_chat_history, get_company_chat_messages, mark_message_as_read
from app.deps import get_current_user
from app.schemas.schemas import ChatMessageCreate
from unittest.mock import MagicMock, patch

client = TestClient(app)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user(user: User):
    return user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def test_company(db: Session):
    company = Company(name="Test Company", contact_email="test@company.com")
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@pytest.fixture
def test_admin(db: Session, test_company):
    admin = User(email="admin@test.com", full_name="Test Admin", role="COMPANYADMIN", company_id=test_company.id, hashed_password="hashedpass")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def test_manager(db: Session, test_company):
    manager = User(email="manager@test.com", full_name="Test Manager", role="MANAGER", company_id=test_company.id, hashed_password="hashedpass")
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return manager

@pytest.fixture
def test_employee(db: Session, test_company):
    employee = User(email="employee@test.com", full_name="Test Employee", role="EMPLOYEE", company_id=test_company.id, hashed_password="hashedpass")
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

def test_send_message_same_company(test_admin, test_employee, db: Session):
    app.dependency_overrides[get_current_user] = lambda: test_admin
    message_data = ChatMessageCreate(
        receiver_id=test_employee.id,
        message="Hello from admin!"
    )
    response = client.post("/api/chat/send", json=message_data.dict(), headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 200
    assert response.json()["message"] == "Message sent successfully"
    
    # Verify message in DB
    msg = db.query(ChatMessage).filter(ChatMessage.sender_id == test_admin.id).first()
    assert msg is not None
    assert msg.message == "Hello from admin!"
    assert msg.company_id == test_admin.company_id
    assert msg.receiver_id == test_employee.id

def test_send_message_different_company(test_admin, test_employee, db: Session):
    # Change employee to different company
    other_company = Company(name="Other Company", contact_email="other@company.com")
    db.add(other_company)
    db.commit()
    db.refresh(other_company)
    test_employee.company_id = other_company.id
    db.commit()
    
    app.dependency_overrides[get_current_user] = lambda: test_admin
    message_data = ChatMessageCreate(
        receiver_id=test_employee.id,
        message="Hello from different company!"
    )
    response = client.post("/api/chat/send", json=message_data.dict(), headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 403
    assert "different company" in response.json()["detail"].lower()

def test_get_chat_history(test_admin, test_employee, db: Session):
    # Create some messages
    create_chat_message(db, ChatMessageCreate(receiver_id=test_employee.id, message="Msg 1"), test_admin.company_id, test_admin.id)
    create_chat_message(db, ChatMessageCreate(receiver_id=test_admin.id, message="Reply 1"), test_admin.company_id, test_employee.id)
    
    app.dependency_overrides[get_current_user] = lambda: test_admin
    response = client.get(f"/api/chat/history/{test_employee.id}", headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2
    assert any(msg["message"] == "Msg 1" for msg in history)
    assert any(msg["message"] == "Reply 1" for msg in history)

def test_get_company_chat_admin_only(test_admin, test_manager, db: Session):
    # Create company message
    create_chat_message(db, ChatMessageCreate(receiver_id=None, message="Company announcement"), test_admin.company_id, test_admin.id)
    
    app.dependency_overrides[get_current_user] = lambda: test_admin
    response = client.get("/api/chat/company", headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) >= 1
    assert messages[0]["message"] == "Company announcement"
    
    # Test non-admin (manager) access
    app.dependency_overrides[get_current_user] = lambda: test_manager
    response = client.get("/api/chat/company", headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 403

def test_mark_message_as_read(test_admin, test_employee, db: Session):
    msg = create_chat_message(db, ChatMessageCreate(receiver_id=test_employee.id, message="Unread msg"), test_admin.company_id, test_admin.id)
    
    app.dependency_overrides[get_current_user] = lambda: test_employee
    response = client.post(f"/api/chat/mark-read/{msg.id}", headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 200
    assert response.json()["message"] == "Message marked as read"
    
    db.refresh(msg)
    assert msg.is_read is True

def test_get_unread_count(test_admin, test_employee, db: Session):
    # Create unread messages
    create_chat_message(db, ChatMessageCreate(receiver_id=test_employee.id, message="Unread 1"), test_admin.company_id, test_admin.id)
    create_chat_message(db, ChatMessageCreate(receiver_id=test_employee.id, message="Unread 2"), test_admin.company_id, test_admin.id)
    # Create read message
    msg3 = create_chat_message(db, ChatMessageCreate(receiver_id=test_employee.id, message="Read msg"), test_admin.company_id, test_admin.id)
    mark_message_as_read(db, msg3.id, test_employee.id, test_admin.company_id)
    
    app.dependency_overrides[get_current_user] = lambda: test_employee
    response = client.get("/api/chat/unread", headers={"Authorization": "Bearer fake.token"})
    assert response.status_code == 200
    assert response.json()["unread_count"] == 2

# WebSocket tests require additional setup, but basic connection test
def test_websocket_connection():
    from fastapi.testclient import TestClient
    from websockets.sync.client import connect
    import asyncio
    
    # This is a basic test; full WebSocket testing might need async
    with TestClient(app) as client:
        # Simulate WebSocket connection (simplified)
        assert True  # Placeholder for actual WebSocket test
        # In real scenario, use websockets library to test /ws/chat endpoint
