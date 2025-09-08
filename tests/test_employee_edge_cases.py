import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = 'http://localhost:8000'

def get_jwt_token(email, password):
    """Get JWT token for a user"""
    login_payload = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        logger.error(f"Failed to login {email}: {response.status_code} - {response.text}")
        return None

def test_edge_case(description, jwt, payload, expected_status):
    """Test an edge case scenario"""
    logger.info(f"Testing: {description}")
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{BASE_URL}/employees", headers=headers, data=json.dumps(payload))

    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response: {response.text}")

    if response.status_code == expected_status:
        logger.info(f"✅ PASS: Expected {expected_status}, got {response.status_code}")
    else:
        logger.error(f"❌ FAIL: Expected {expected_status}, got {response.status_code}")

    return response.status_code == expected_status

def run_edge_case_tests():
    """Run comprehensive edge case tests"""
    logger.info("Starting Edge Case Testing for Employee Creation Endpoint")

    # Get JWT tokens for different roles
    superadmin_jwt = get_jwt_token("test_superadmin@example.com", "password123")
    employee_jwt = get_jwt_token("test_employee@example.com", "password123")

    if not superadmin_jwt or not employee_jwt:
        logger.error("Failed to obtain JWT tokens. Aborting tests.")
        return

    # Test cases
    test_cases = [
        # Valid payload (should succeed)
        {
            "description": "Valid payload with all required fields",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": 200,
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer",
                "phone": "123-456-7890",
                "hire_date": "2025-09-01T00:00:00",
                "manager_id": None
            },
            "expected_status": 201
        },

        # Missing required field: user_id
        {
            "description": "Missing required field: user_id",
            "jwt": superadmin_jwt,
            "payload": {
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer"
            },
            "expected_status": 422
        },

        # Missing required field: company_id
        {
            "description": "Missing required field: company_id",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": 101,
                "department": "Engineering",
                "position": "Developer"
            },
            "expected_status": 422
        },

        # Invalid data type: user_id as string
        {
            "description": "Invalid data type: user_id as string",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": "invalid",
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer"
            },
            "expected_status": 422
        },

        # Invalid hire_date format
        {
            "description": "Invalid hire_date format",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": 102,
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer",
                "hire_date": "invalid-date"
            },
            "expected_status": 422
        },

        # Unauthorized access: Employee role
        {
            "description": "Unauthorized access: Employee role",
            "jwt": employee_jwt,
            "payload": {
                "user_id": 103,
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer"
            },
            "expected_status": 403
        },

        # Duplicate employee profile
        {
            "description": "Duplicate employee profile",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": 200,  # Same as first test
                "company_id": 1,
                "department": "Engineering",
                "position": "Developer"
            },
            "expected_status": 409
        },

        # Empty payload
        {
            "description": "Empty payload",
            "jwt": superadmin_jwt,
            "payload": {},
            "expected_status": 422
        },

        # Invalid company_id for non-SuperAdmin (if we had a CompanyAdmin user)
        # Note: We don't have a CompanyAdmin user with company_id set, so skipping this test

        # Extremely long string values
        {
            "description": "Extremely long department name",
            "jwt": superadmin_jwt,
            "payload": {
                "user_id": 104,
                "company_id": 1,
                "department": "A" * 1000,  # Very long department name
                "position": "Developer"
            },
            "expected_status": 422  # Should fail validation if length limits exist
        }
    ]

    passed = 0
    total = len(test_cases)

    for test_case in test_cases:
        if test_edge_case(**test_case):
            passed += 1
        logger.info("-" * 50)

    logger.info(f"Edge Case Testing Complete: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All edge case tests passed!")
    else:
        logger.warning(f"⚠️  {total - passed} tests failed")

if __name__ == "__main__":
    run_edge_case_tests()
