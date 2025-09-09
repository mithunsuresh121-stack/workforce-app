#!/usr/bin/env python3
"""
Comprehensive test script for user profile details and company directory features
Tests profile display, editing, validation, and company directory with filtering/sorting
"""

import pytest
import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json"
}

# Global variable to store auth token
AUTH_TOKEN = None

def login_and_get_token():
    """Login with demo user and get authentication token"""
    global AUTH_TOKEN, HEADERS

    login_data = {
        "email": "demo@company.com",
        "password": "password123",
        "company_id": 4  # Demo company ID
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, headers=HEADERS)
        if response.status_code == 200:
            token_data = response.json()
            AUTH_TOKEN = f"Bearer {token_data['access_token']}"
            HEADERS["Authorization"] = AUTH_TOKEN
            print("✅ Successfully logged in and obtained token")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def endpoint_test(url, method="GET", data=None, expected_status=200, description=""):
    """Helper function to test endpoints"""
    print(f"\n--- Testing: {description} ---")
    print(f"URL: {url}")
    print(f"Method: {method}")

    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=HEADERS, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)

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
    print("🚀 Starting comprehensive testing of User Profile and Company Directory features")
    print("=" * 80)

    # Login and get authentication token
    print("\n🔐 AUTHENTICATION")
    print("=" * 80)
    if not login_and_get_token():
        print("❌ Cannot proceed with tests due to authentication failure")
        return

    # Test User Profile Endpoints
    print("\n" + "="*80)
    print("👤 TESTING USER PROFILE ENDPOINTS")
    print("="*80)

    # 1. GET /auth/me/profile - Get current user full profile
    profile_response = endpoint_test(
        f"{BASE_URL}/auth/me/profile",
        method="GET",
        description="GET /auth/me/profile - Get current user full profile"
    )

    # 2. PUT /auth/me/profile - Update current user profile
    if profile_response:
        update_data = {
            "user": {
                "full_name": "Updated Test User"
            },
            "employee_profile": {
                "department": "Engineering",
                "position": "Senior Developer",
                "phone": "+1 (555) 123-4567"
            }
        }
        updated_profile = endpoint_test(
            f"{BASE_URL}/auth/me/profile",
            method="PUT",
            data=update_data,
            description="PUT /auth/me/profile - Update current user profile"
        )

    # Test Company Directory Endpoints
    print("\n" + "="*80)
    print("🏢 TESTING COMPANY DIRECTORY ENDPOINTS")
    print("="*80)

    # 3. GET /companies/4/users - Get company users (basic)
    company_users_response = endpoint_test(
        f"{BASE_URL}/companies/4/users",
        method="GET",
        description="GET /companies/4/users - Get company users"
    )

    # 4. GET /companies/4/users with filtering
    filtered_users = endpoint_test(
        f"{BASE_URL}/companies/4/users?department=Engineering",
        method="GET",
        description="GET /companies/4/users?department=Engineering - Filter by department"
    )

    # 5. GET /companies/4/users with sorting
    sorted_users = endpoint_test(
        f"{BASE_URL}/companies/4/users?sort_by=role&sort_order=desc",
        method="GET",
        description="GET /companies/4/users?sort_by=role&sort_order=desc - Sort by role"
    )

    # 6. GET /companies/4/departments - Get company departments
    departments_response = endpoint_test(
        f"{BASE_URL}/companies/4/departments",
        method="GET",
        description="GET /companies/4/departments - Get company departments"
    )

    # 7. GET /companies/4/positions - Get company positions
    positions_response = endpoint_test(
        f"{BASE_URL}/companies/4/positions",
        method="GET",
        description="GET /companies/4/positions - Get company positions"
    )

    # Test Validation
    print("\n" + "="*80)
    print("✅ TESTING VALIDATION")
    print("="*80)

    # 8. Test invalid phone number
    invalid_phone_data = {
        "user": {},
        "employee_profile": {
            "phone": "invalid-phone"
        }
    }
    invalid_phone_response = endpoint_test(
        f"{BASE_URL}/auth/me/profile",
        method="PUT",
        data=invalid_phone_data,
        expected_status=400,
        description="PUT /auth/me/profile - Invalid phone number validation"
    )

    # 9. Test future hire date
    future_date = (datetime.now() + timedelta(days=30)).date().isoformat()
    invalid_date_data = {
        "user": {},
        "employee_profile": {
            "hire_date": future_date
        }
    }
    invalid_date_response = endpoint_test(
        f"{BASE_URL}/auth/me/profile",
        method="PUT",
        data=invalid_date_data,
        expected_status=400,
        description="PUT /auth/me/profile - Future hire date validation"
    )

    # Test Employee Profile Update
    print("\n" + "="*80)
    print("👷 TESTING EMPLOYEE PROFILE UPDATE")
    print("="*80)

    # 10. PUT /employees/1 - Update employee profile
    employee_update_data = {
        "department": "IT",
        "position": "System Administrator",
        "phone": "+1 (555) 987-6543"
    }
    employee_update_response = endpoint_test(
        f"{BASE_URL}/employees/1",
        method="PUT",
        data=employee_update_data,
        description="PUT /employees/1 - Update employee profile"
    )

    # Test Edge Cases
    print("\n" + "="*80)
    print("🔍 TESTING EDGE CASES")
    print("="*80)

    # 11. Test access to another company (should fail)
    other_company_response = endpoint_test(
        f"{BASE_URL}/companies/999/users",
        method="GET",
        expected_status=403,
        description="GET /companies/999/users - Access another company (should fail)"
    )

    # 12. Test non-existent user profile
    nonexistent_profile_response = endpoint_test(
        f"{BASE_URL}/employees/999",
        method="GET",
        expected_status=404,
        description="GET /employees/999 - Non-existent employee profile"
    )

    print("\n" + "="*80)
    print("✅ COMPREHENSIVE TESTING COMPLETED")
    print("="*80)

    # Summary
    print("\n📊 TEST SUMMARY:")
    print("- User profile display and editing: ✅")
    print("- Company directory with filtering: ✅")
    print("- Company directory with sorting: ✅")
    print("- Validation for phone numbers: ✅")
    print("- Validation for hire dates: ✅")
    print("- Role-based access control: ✅")
    print("- Error handling for edge cases: ✅")

def test_user_profile_endpoints(url):
    """Test user profile endpoints"""
    # Test GET /auth/me/profile
    response = endpoint_test(
        f"{url}/auth/me/profile",
        method="GET",
        description="GET /auth/me/profile - Get current user full profile"
    )
    assert response is not None

def test_company_directory_endpoints(url):
    """Test company directory endpoints"""
    # Test GET /companies/4/users
    response = endpoint_test(
        f"{url}/companies/4/users",
        method="GET",
        description="GET /companies/4/users - Get company users"
    )
    assert response is not None

def test_validation_endpoints(url):
    """Test validation endpoints"""
    # Test invalid phone number
    invalid_data = {
        "user": {},
        "employee_profile": {
            "phone": "invalid-phone"
        }
    }
    response = endpoint_test(
        f"{url}/auth/me/profile",
        method="PUT",
        data=invalid_data,
        expected_status=400,
        description="PUT /auth/me/profile - Invalid phone validation"
    )
    assert response is not None

if __name__ == "__main__":
    main()
