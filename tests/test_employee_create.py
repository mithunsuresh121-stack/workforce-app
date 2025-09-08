import requests
import json

BASE_URL = 'http://localhost:8000'
SUPERADMIN_EMAIL = 'admin@app.com'
SUPERADMIN_PASSWORD = 'supersecure123'

def get_jwt_token():
    login_payload = {
        "email": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    response.raise_for_status()
    return response.json()['access_token']

def test_create_employee():
    jwt_token = get_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # Complete payload including company_id
    payload = {
        "user_id": 10,
        "company_id": 4,  # Company ID for user 10
        "department": "Engineering",
        "position": "Developer",
        "phone": "123-456-7890",
        "hire_date": "2025-09-01T00:00:00",
        "manager_id": None
    }

    response = requests.post(f"{BASE_URL}/employees", headers=headers, data=json.dumps(payload))

    print("Status code:", response.status_code)
    print("Response body:", response.text)

if __name__ == "__main__":
    test_create_employee()
