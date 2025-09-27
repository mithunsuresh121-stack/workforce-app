#!/usr/bin/env python3
"""
Test API permission enforcement
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def login(email, password):
    """Login and return token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_endpoint(token, method, url, data=None, expected_status=200):
    """Test an endpoint with authentication"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if method == "GET":
        response = requests.get(f"{BASE_URL}{url}", headers=headers)
    elif method == "POST":
        response = requests.post(f"{BASE_URL}{url}", headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(f"{BASE_URL}{url}", headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(f"{BASE_URL}{url}", headers=headers)

    status_ok = response.status_code == expected_status
    print(f"  {method} {url}: {response.status_code} {'✓' if status_ok else '✗'} (expected {expected_status})")
    if not status_ok and response.status_code != expected_status:
        try:
            error = response.json()
            print(f"    Error: {error.get('detail', 'Unknown error')}")
        except:
            print(f"    Response: {response.text[:100]}")
    return status_ok

def test_permissions():
    print("=== Testing API Permission Enforcement ===\n")

    # Login with different users
    super_admin_token = login("superadmin@workforce.com", "password123")
    demo_user_token = login("emp1@techcorp.com", "password123")

    if not super_admin_token:
        print("✗ Failed to login as Super Admin")
        return False
    if not demo_user_token:
        print("✗ Failed to login as Demo User")
        return False

    print("✓ Logged in successfully\n")

    # Test cases: (description, token, method, url, data, expected_status)
    tests = [
        # Super Admin should be able to create users
        ("Super Admin creates EMPLOYEE", super_admin_token, "POST", "/users", {
            "email": "test_employee@test.com",
            "password": "password123",
            "full_name": "Test Employee",
            "role": "EMPLOYEE",
            "company_id": 1
        }, 201),

        # Super Admin should be able to create MANAGER
        ("Super Admin creates MANAGER", super_admin_token, "POST", "/users", {
            "email": "test_manager@test.com",
            "password": "password123",
            "full_name": "Test Manager",
            "role": "MANAGER",
            "company_id": 1
        }, 201),

        # Demo User (EMPLOYEE) should NOT be able to create users
        ("Employee cannot create users", demo_user_token, "POST", "/users", {
            "email": "unauthorized@test.com",
            "password": "password123",
            "full_name": "Unauthorized User",
            "role": "EMPLOYEE",
            "company_id": 1
        }, 403),

        # Super Admin should be able to update users
        ("Super Admin updates user", super_admin_token, "PUT", "/users/1", {
            "full_name": "Updated Name"
        }, 200),

        # Demo User should NOT be able to update other users
        ("Employee cannot update others", demo_user_token, "PUT", "/users/1", {
            "full_name": "Hacked Name"
        }, 403),

        # Demo User should be able to update themselves (assuming user ID 5 is emp1)
        ("Employee can update self", demo_user_token, "PUT", "/users/5", {
            "full_name": "Updated Demo User"
        }, 200),
    ]

    all_passed = True
    for desc, token, method, url, data, expected in tests:
        print(f"Testing: {desc}")
        if not test_endpoint(token, method, url, data, expected):
            all_passed = False
        print()

    if all_passed:
        print("✓ All API permission tests passed!")
        return True
    else:
        print("✗ Some API permission tests failed!")
        return False

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("✗ Server not running or not accessible")
            sys.exit(1)
    except:
        print("✗ Cannot connect to server. Make sure it's running on http://localhost:8000")
        sys.exit(1)

    success = test_permissions()
    sys.exit(0 if success else 1)
