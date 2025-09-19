import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_auth_token():
    response = client.post("/api/auth/login", json={
        "email": "demo@company.com",
        "password": "password123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

def get_super_admin_token():
    response = client.post("/api/auth/login", json={
        "email": "admin@app.com",
        "password": "supersecure123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

def test_get_profile_me():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "full_name" in data
    assert "email" in data

def test_request_profile_update():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First get the current user to get user_id
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    user_profile = response.json()
    user_id = user_profile["user_id"]

    payload = {
        "user_id": user_id,
        "request_type": "update",
        "payload": {
            "full_name": "Updated Name",
            # "gender": "Male",  # removed as per request
            "address": "123 New St",
            "city": "New City",
            "emergency_contact": "123-456-7890"
        }
    }
    response = client.post("/api/profile/request-update", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"

def test_request_delete_account():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/profile/request-delete", headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["request_type"] == "delete"

def test_get_profile_requests():
    token = get_super_admin_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/profile/requests", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_approve_profile_request():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First get the current user to get user_id
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    user_profile = response.json()
    user_id = user_profile["user_id"]

    payload = {
        "user_id": user_id,
        "request_type": "update",
        "payload": {
            "full_name": "Approve Me",
            # "gender": "Female"  # removed as per request
        }
    }
    response = client.post("/api/profile/request-update", json=payload, headers=headers)
    assert response.status_code == 201
    request_id = response.json()["id"]

    admin_token = get_super_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(f"/api/profile/requests/{request_id}/approve", json={"review_comment": "Approved"}, headers=admin_headers)
    assert response.status_code == 200

def test_reject_profile_request():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # First get the current user to get user_id
    response = client.get("/api/profile/me", headers=headers)
    assert response.status_code == 200
    user_profile = response.json()
    user_id = user_profile["user_id"]

    payload = {
        "user_id": user_id,
        "request_type": "update",
        "payload": {
            "full_name": "Reject Me"
        }
    }
    response = client.post("/api/profile/request-update", json=payload, headers=headers)
    assert response.status_code == 201
    request_id = response.json()["id"]

    admin_token = get_super_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(f"/api/profile/requests/{request_id}/reject", json={"review_comment": "Rejected"}, headers=admin_headers)
    assert response.status_code == 200
