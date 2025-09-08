import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_signup():
    response = client.post("/auth/signup", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "Employee",
        "company_id": 1
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_login():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
        "company_id": 1
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
        "company_id": 1
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
