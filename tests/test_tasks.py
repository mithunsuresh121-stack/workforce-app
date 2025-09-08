import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

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
        "status": "To Do",
        "company_id": 1
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
        "status": "To Do",
        "company_id": 1
    })
    task_id = create_response.json()["id"]
    
    # Get the task by ID
    response = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == task_id
