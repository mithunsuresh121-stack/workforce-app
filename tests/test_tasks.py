import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
import io

client = TestClient(app)

def test_get_tasks():
    # First, login to get a token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    token = login_response.json()["access_token"]

    # Use the token to get tasks
    response = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_task():
    # First, login to get a token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    token = login_response.json()["access_token"]

    # Create a new task
    response = client.post("/tasks/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Test Task",
        "description": "This is a test task",
        "status": "Pending",
        "assignee_id": 1,
        "priority": "Medium",
        "due_at": "2024-12-31"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"

def test_get_task_by_id():
    # First, login to get a token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    token = login_response.json()["access_token"]

    # Create a task to get its ID
    create_response = client.post("/tasks/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Test Task for ID",
        "description": "This is a test task for ID retrieval",
        "status": "Pending",
        "assignee_id": 1,
        "priority": "Medium",
        "due_at": "2024-12-31"
    })
    task_id = create_response.json()["id"]

    # Get the task by ID
    response = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_update_task():
    # First, login to get a token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    token = login_response.json()["access_token"]

    # Create a task to update
    create_response = client.post("/tasks/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Test Task for Update",
        "description": "This is a test task for update",
        "status": "Pending",
        "assignee_id": 1,
        "priority": "Medium",
        "due_at": "2024-12-31"
    })
    task_id = create_response.json()["id"]

    # Update the task
    response = client.put(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Updated Test Task",
        "description": "This is an updated test task",
        "status": "In Progress",
        "assignee_id": 1,
        "priority": "High",
        "due_at": "2024-12-31"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Task"
    assert response.json()["status"] == "In Progress"

def test_task_attachments():
    # First, login to get a token
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    token = login_response.json()["access_token"]

    # Create a task
    create_response = client.post("/tasks/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Test Task for Attachments",
        "description": "This is a test task for attachments",
        "status": "Pending",
        "assignee_id": 1,
        "priority": "Medium",
        "due_at": "2024-12-31"
    })
    task_id = create_response.json()["id"]

    # Upload an attachment
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        f"/tasks/{task_id}/attachments",
        headers={"Authorization": f"Bearer {token}"},
        files=files
    )
    assert response.status_code == 201
    attachment = response.json()
    assert attachment["file_path"].endswith("test.txt")

    # Get attachments
    response = client.get(f"/tasks/{task_id}/attachments", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    attachments = response.json()
    assert len(attachments) == 1
    assert attachments[0]["id"] == attachment["id"]

    # Delete attachment
    response = client.delete(f"/tasks/{task_id}/attachments/{attachment['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

def test_role_based_permissions():
    # Test with different user roles
    # This would require setting up different users with different roles
    # For now, just test that endpoints require authentication
    response = client.get("/tasks/")
    assert response.status_code == 401  # Unauthorized

    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "This is a test task",
        "status": "Pending",
        "assignee_id": 1,
        "priority": "Medium",
        "due_at": "2024-12-31"
    })
    assert response.status_code == 401  # Unauthorized
