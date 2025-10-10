import sys
import os
import pytest
import requests

# Add backend app directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/app')))

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the API"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def superadmin_jwt(base_url):
    """Get superadmin JWT token for tests"""
    r = requests.post(f"{base_url}/api/auth/login", json={"email": "admin@app.com", "password": "supersecure123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def manager_jwt(base_url):
    """Get manager JWT token for tests"""
    r = requests.post(f"{base_url}/api/auth/login", json={"email": "manager@company.com", "password": "password123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def employee_jwt(base_url):
    """Get employee JWT token for tests"""
    r = requests.post(f"{base_url}/api/auth/login", json={"email": "demo@company.com", "password": "password123"})
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def auth_headers():
    """Helper fixture to create auth headers"""
    def _auth_header(token):
        return {"Authorization": f"Bearer {token}"}
    return _auth_header

def clear_active_attendance(base_url, superadmin_jwt, auth_headers):
    """Helper function to clear all active attendances using superadmin JWT"""
    try:
        # Get all active attendances using the admin endpoint
        r_check = requests.get(f"{base_url}/api/attendance/admin/active-all", headers=auth_headers(superadmin_jwt))
        if r_check.status_code == 200:
            active_attendances = r_check.json()
            if active_attendances:  # Check if list is not empty
                print(f"Found {len(active_attendances)} active attendance(s) to clean up")
                success_count = 0
                for attendance in active_attendances:
                    print(f"Cleaning up attendance: ID={attendance['id']}, Employee={attendance['employee_id']}")

                    # Try to clock out
                    r = requests.put(f"{base_url}/api/attendance/clock-out", json={
                        "attendance_id": attendance['id'],
                        "employee_id": attendance['employee_id'],
                        "notes": "Test cleanup"
                    }, headers=auth_headers(superadmin_jwt))
                    if r.status_code == 200:
                        success_count += 1
                        print(f"✅ Successfully cleared attendance {attendance['id']}")
                    else:
                        print(f"❌ Failed to clear attendance {attendance['id']}: {r.status_code} - {r.text}")
                print(f"ℹ️ Cleanup complete: {success_count}/{len(active_attendances)} attendances cleared")
                return success_count == len(active_attendances)
            else:
                print("ℹ️ No active attendances found")
                return True
        else:
            print(f"❌ Failed to get active attendances: {r_check.status_code} - {r_check.text}")
            return False
    except Exception as e:
        print(f"❌ Exception in clear_active_attendance: {e}")
        return False

@pytest.fixture(scope="function", autouse=True)
def cleanup_attendance(base_url, superadmin_jwt, auth_headers):
    """Automatically clean up active attendance before and after each test"""
    print("\n=== Pre-test cleanup ===")
    clear_active_attendance(base_url, superadmin_jwt, auth_headers)

    yield

    print("\n=== Post-test cleanup ===")
    clear_active_attendance(base_url, superadmin_jwt, auth_headers)

@pytest.fixture(scope="function")
def override_get_db():
    """Override get_db dependency for tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
