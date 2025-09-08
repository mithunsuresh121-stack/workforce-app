import pytest
import requests
import time

def test_health(base_url):
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200

def test_employee_crud_superadmin(base_url, superadmin_jwt, auth_headers):
    # Create - use a unique user_id to avoid conflicts
    import random
    user_id = random.randint(1000, 9999)  # Use a random high number to avoid conflicts
    payload = {"user_id": user_id, "company_id": 1, "department": "QA", "position": "Tester", "hire_date": "2023-05-01"}
    r = requests.post(f"{base_url}/employees/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [200, 201]

    # Try to create again - should get 409 Conflict
    r = requests.post(f"{base_url}/employees/", json=payload, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 409
    assert "already exists" in r.json()["detail"].lower()

    # Read - use user_id to get the profile
    r = requests.get(f"{base_url}/employees/{user_id}", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200

    # Update - use user_id
    r = requests.put(f"{base_url}/employees/{user_id}", json={"position": "Senior Tester"}, headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200
    assert r.json()["position"] == "Senior Tester"

    # Delete (soft delete) - use user_id
    r = requests.delete(f"{base_url}/employees/{user_id}", headers=auth_headers(superadmin_jwt))
    assert r.status_code == 200

def test_role_restrictions(base_url, manager_jwt, employee_jwt, auth_headers):
    # Manager should not delete employees from other company
    r = requests.delete(f"{base_url}/employees/999", headers=auth_headers(manager_jwt))
    assert r.status_code in [403, 404, 401]

    # Employee should not create - use user_id 29 (admin@app.com)
    payload = {"user_id": 29, "company_id": 1, "department": "Eng", "position": "Dev", "hire_date": "2023-01-01"}
    r = requests.post(f"{base_url}/employees/", json=payload, headers=auth_headers(employee_jwt))
    assert r.status_code in [403, 401]

def test_invalid_requests(base_url, superadmin_jwt, auth_headers):
    # Missing field
    r = requests.post(f"{base_url}/employees/", json={"department": "Ops"}, headers=auth_headers(superadmin_jwt))
    assert r.status_code in [422, 401]

    # Invalid JWT
    r = requests.get(f"{base_url}/employees/", headers=auth_headers("invalid"))
    assert r.status_code == 401

    # Expired JWT simulation
    r = requests.get(f"{base_url}/employees/", headers=auth_headers("expired.token.value"))
    assert r.status_code == 401
