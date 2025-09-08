import requests
import json

BASE_URL = 'http://localhost:8000'

# Test users with different roles and their credentials
USERS = {
    "superadmin": {"email": "test_superadmin@example.com", "password": "password123"},
    "companyadmin": {"email": "test_companyadmin@example.com", "password": "password123"},
    "manager": {"email": "test_manager@example.com", "password": "password123"},
    "employee": {"email": "test_employee@example.com", "password": "password123"},
}

# Payload template for employee profile creation
EMPLOYEE_PAYLOAD = {
    "user_id": None,
    "company_id": None,
    "department": "Engineering",
    "position": "Developer",
    "phone": "123-456-7890",
    "hire_date": "2025-09-01T00:00:00",
    "manager_id": None
}

def get_jwt_token(email, password):
    login_payload = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    response.raise_for_status()
    return response.json()['access_token']

def test_create_employee_profile(role, user_id, company_id):
    token = get_jwt_token(USERS[role]["email"], USERS[role]["password"])
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = EMPLOYEE_PAYLOAD.copy()
    payload["user_id"] = user_id
    payload["company_id"] = company_id

    response = requests.post(f"{BASE_URL}/employees", headers=headers, data=json.dumps(payload))
    print(f"Role: {role}, Status Code: {response.status_code}, Response: {response.text}")

def main():
    # SuperAdmin can create for any company
    test_create_employee_profile("superadmin", 36, 1)

    # CompanyAdmin can create for their company (assuming company_id 1)
    test_create_employee_profile("companyadmin", 37, 1)

    # Manager can create for their company (assuming company_id 1)
    test_create_employee_profile("manager", 38, 1)

    # Employee should be forbidden to create profiles
    test_create_employee_profile("employee", 39, 1)

if __name__ == "__main__":
    main()
