import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def superadmin_jwt(base_url):
    """Get superadmin JWT token for tests"""
    r = requests.post(f"{base_url}/auth/login", json={"email": "admin@app.com", "password": "supersecure123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def manager_jwt(base_url):
    """Get manager JWT token for tests"""
    r = requests.post(f"{base_url}/auth/login", json={"email": "admin@techcorp.com", "password": "password123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def employee_jwt(base_url):
    """Get employee JWT token for tests"""
    r = requests.post(f"{base_url}/auth/login", json={"email": "test@company.com", "password": "password123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def auth_headers():
    """Helper fixture to create auth headers"""
    def _auth_header(token):
        return {"Authorization": f"Bearer {token}"}
    return _auth_header

def clear_active_attendance(base_url, employee_jwt, auth_headers):
    """Helper function to clear active attendance for a given employee JWT"""
    try:
        # First get the employee ID from the JWT token (this is a simplified approach)
        # For now, we'll assume employee ID is 30 for test@company.com
        employee_id = 30

        # Check if there's an active attendance using the correct endpoint
        r_check = requests.get(f"{base_url}/attendance/active/{employee_id}", headers=auth_headers(employee_jwt))
        if r_check.status_code == 200:
            active_data = r_check.json()
            if active_data:  # Check if list is not empty
                attendance = active_data[0]  # Get first active attendance
                print(f"Found active attendance: ID={attendance['id']}, Status={attendance.get('status', 'unknown')}")

                # Try to clock out
                r = requests.put(f"{base_url}/attendance/clock-out", json={
                    "attendance_id": attendance['id'],
                    "employee_id": employee_id,
                    "notes": "Test cleanup"
                }, headers=auth_headers(employee_jwt))
                if r.status_code == 200:
                    print("✅ Successfully cleared active attendance")
                    return True
                else:
                    print(f"❌ Failed to clear active attendance: {r.status_code} - {r.text}")
                    return False
            else:
                print("ℹ️ No active attendance found")
                return True
        elif r_check.status_code == 404:
            print("ℹ️ No active attendance found")
            return True
        else:
            print(f"❌ Failed to check active attendance: {r_check.status_code} - {r_check.text}")
            return False
    except Exception as e:
        print(f"❌ Exception in clear_active_attendance: {e}")
        return False

@pytest.fixture(scope="function", autouse=True)
def cleanup_attendance(base_url, employee_jwt, auth_headers):
    """Automatically clean up active attendance before and after each test"""
    print("\n=== Pre-test cleanup ===")
    clear_active_attendance(base_url, employee_jwt, auth_headers)

    yield

    print("\n=== Post-test cleanup ===")
    clear_active_attendance(base_url, employee_jwt, auth_headers)
