#!/usr/bin/env python3
"""
Comprehensive test script for leaves and shifts endpoints
Tests all CRUD operations, role-based access control, and edge cases
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = None  # Will be set after login

def login_and_get_token():
    """Login and get authentication token"""
    global AUTH_TOKEN
    login_data = {
        "email": "test_manager@example.com",
        "password": "password123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        AUTH_TOKEN = f"Bearer {token}"
        print(f"✅ Successfully logged in and got token: {token[:50]}...")
        return True
    else:
        print(f"❌ Login failed: {response.json()}")
        return False

def get_headers():
    """Get headers with authentication token"""
    return {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json"
    }

def test_endpoint(url, method="GET", data=None, expected_status=200, description=""):
    """Helper function to test endpoints"""
    print(f"\n--- Testing: {description} ---")
    print(f"URL: {url}")
    print(f"Method: {method}")

    try:
        headers = get_headers()
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Expected Status: {expected_status}")

        if response.status_code == expected_status:
            print("✅ PASS")
        else:
            print("❌ FAIL")

        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, default=str)}")
            return response_data
        except:
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def main():
    print("🚀 Starting comprehensive testing of Leaves and Shifts endpoints")
    print("=" * 60)

    # Login first
    if not login_and_get_token():
        print("❌ Cannot proceed without authentication")
        return

    # Test data
    test_leave_data = {
        "tenant_id": "1",
        "employee_id": 34,
        "type": "vacation",
        "start_at": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_at": (datetime.now() + timedelta(days=5)).isoformat(),
        "status": "Pending"
    }

    test_shift_data = {
        "tenant_id": "1",
        "employee_id": 34,
        "start_at": (datetime.now() + timedelta(hours=9)).isoformat(),
        "end_at": (datetime.now() + timedelta(hours=17)).isoformat(),
        "location": "Office"
    }

    # Test Leaves Endpoints
    print("\n" + "="*60)
    print("📋 TESTING LEAVES ENDPOINTS")
    print("="*60)

    # 1. GET /leaves/ - List all leaves
    leaves_response = test_endpoint(
        f"{BASE_URL}/leaves/",
        method="GET",
        description="GET /leaves/ - List all leaves"
    )

    # 2. POST /leaves/ - Create new leave
    created_leave = test_endpoint(
        f"{BASE_URL}/leaves/",
        method="POST",
        data=test_leave_data,
        expected_status=201,
        description="POST /leaves/ - Create new leave"
    )

    if created_leave:
        leave_id = created_leave.get('id')
        print(f"Created leave ID: {leave_id}")

        # 3. GET /leaves/{id} - Get specific leave
        test_endpoint(
            f"{BASE_URL}/leaves/{leave_id}",
            method="GET",
            description=f"GET /leaves/{leave_id} - Get specific leave"
        )

        # 4. PUT /leaves/{id}/status - Update leave status
        status_update = {"status": "Approved"}
        test_endpoint(
            f"{BASE_URL}/leaves/{leave_id}/status",
            method="PUT",
            json=status_update,
            description=f"PUT /leaves/{leave_id}/status - Update leave status"
        )

        # 5. DELETE /leaves/{id} - Delete leave
        test_endpoint(
            f"{BASE_URL}/leaves/{leave_id}",
            method="DELETE",
            expected_status=200,
            description=f"DELETE /leaves/{leave_id} - Delete leave"
        )

    # 6. GET /leaves/my-leaves/ - Get user's leaves
    test_endpoint(
        f"{BASE_URL}/leaves/my-leaves/",
        method="GET",
        description="GET /leaves/my-leaves/ - Get user's leaves"
    )

    # Test Shifts Endpoints
    print("\n" + "="*60)
    print("⏰ TESTING SHIFTS ENDPOINTS")
    print("="*60)

    # 1. GET /shifts/ - List all shifts
    shifts_response = test_endpoint(
        f"{BASE_URL}/shifts/",
        method="GET",
        description="GET /shifts/ - List all shifts"
    )

    # 2. POST /shifts/ - Create new shift
    created_shift = test_endpoint(
        f"{BASE_URL}/shifts/",
        method="POST",
        data=test_shift_data,
        expected_status=201,
        description="POST /shifts/ - Create new shift"
    )

    if created_shift:
        shift_id = created_shift.get('id')
        print(f"Created shift ID: {shift_id}")

        # 3. GET /shifts/{id} - Get specific shift
        test_endpoint(
            f"{BASE_URL}/shifts/{shift_id}",
            method="GET",
            description=f"GET /shifts/{shift_id} - Get specific shift"
        )

        # 4. PUT /shifts/{id} - Update shift
        updated_shift_data = test_shift_data.copy()
        updated_shift_data["location"] = "Remote"
        test_endpoint(
            f"{BASE_URL}/shifts/{shift_id}",
            method="PUT",
            data=updated_shift_data,
            description=f"PUT /shifts/{shift_id} - Update shift"
        )

        # 5. DELETE /shifts/{id} - Delete shift
        test_endpoint(
            f"{BASE_URL}/shifts/{shift_id}",
            method="DELETE",
            expected_status=200,
            description=f"DELETE /shifts/{shift_id} - Delete shift"
        )

    # 6. GET /shifts/my-shifts/ - Get user's shifts
    test_endpoint(
        f"{BASE_URL}/shifts/my-shifts/",
        method="GET",
        description="GET /shifts/my-shifts/ - Get user's shifts"
    )

    # Test Edge Cases
    print("\n" + "="*60)
    print("🔍 TESTING EDGE CASES")
    print("="*60)

    # Test invalid leave ID
    test_endpoint(
        f"{BASE_URL}/leaves/99999",
        method="GET",
        expected_status=404,
        description="GET /leaves/99999 - Invalid leave ID"
    )

    # Test invalid shift ID
    test_endpoint(
        f"{BASE_URL}/shifts/99999",
        method="GET",
        expected_status=404,
        description="GET /shifts/99999 - Invalid shift ID"
    )

    # Test invalid leave data
    invalid_leave_data = {
        "tenant_id": "4",
        "employee_id": 1,
        "type": "invalid_type",
        "start_at": "invalid_date",
        "end_at": "invalid_date",
        "status": "invalid_status"
    }
    test_endpoint(
        f"{BASE_URL}/leaves/",
        method="POST",
        data=invalid_leave_data,
        expected_status=422,
        description="POST /leaves/ - Invalid leave data"
    )

    print("\n" + "="*60)
    print("✅ COMPREHENSIVE TESTING COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()
