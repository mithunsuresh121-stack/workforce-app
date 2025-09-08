import pytest
import requests
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration
BASE_URL = "http://localhost:8000"
EMPLOYEE_ID = 1

# Database setup for local PostgreSQL
DB_USER = os.environ.get('POSTGRES_USER', 'workforce')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
DB_NAME = os.environ.get('POSTGRES_DB', 'workforce')
DB_HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')

@pytest.fixture(scope="session")
def db_engine():
    """Database engine fixture for cleanup operations"""
    engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    yield engine

@pytest.fixture(scope="session")
def admin_jwt():
    """Admin JWT token fixture"""
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@app.com",
        "password": "supersecure123"
    })
    r.raise_for_status()
    return r.json()["access_token"]

@pytest.fixture(scope="session")
def employee_jwt():
    """Employee JWT token fixture"""
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@company.com",
        "password": "password123"
    })
    r.raise_for_status()
    return r.json()["access_token"]

def auth_header(token):
    """Helper to create authorization header"""
    return {"Authorization": f"Bearer {token}"}

def safe_request(method, url, token, json_data=None):
    """Make request and return status and response"""
    headers = auth_header(token)
    if method.upper() == 'POST':
        r = requests.post(url, json=json_data, headers=headers)
    elif method.upper() == 'PUT':
        r = requests.put(url, json=json_data, headers=headers)
    elif method.upper() == 'GET':
        r = requests.get(url, headers=headers)
    else:
        raise ValueError(f"Unsupported method: {method}")

    return r.status_code, r

@pytest.fixture(autouse=True)
def cleanup_attendance(admin_jwt):
    """Auto-cleanup fixture for attendance records"""
    # Cleanup before test
    r = requests.get(f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=auth_header(admin_jwt))
    if r.status_code == 200:
        for rec in r.json():
            requests.put(f"{BASE_URL}/attendance/clock-out",
                        json={"employee_id": EMPLOYEE_ID, "attendance_id": rec["id"]},
                        headers=auth_header(admin_jwt))

    yield

    # Cleanup after test
    r = requests.get(f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=auth_header(admin_jwt))
    if r.status_code == 200:
        for rec in r.json():
            requests.put(f"{BASE_URL}/attendance/clock-out",
                        json={"employee_id": EMPLOYEE_ID, "attendance_id": rec["id"]},
                        headers=auth_header(admin_jwt))

# ===== EMPLOYEE TESTS (may be skipped due to permissions) =====

def test_employee_clock_in(employee_jwt):
    """Test employee clock-in functionality"""
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", employee_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Employee test clock-in"})

    # Employee cannot clock-in for another employee (EMPLOYEE_ID=1, but JWT is for 30)
    assert status == 403, f"Employee clock-in should be denied: {status} - {r.text}"
    print(f"✅ Employee clock-in correctly denied: {status}")

def test_employee_clock_out(employee_jwt):
    """Test employee clock-out functionality"""
    # First clock in for self
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", employee_jwt,
                           {"employee_id": 30, "notes": "Employee test clock-out"})

    assert status == 201, f"Clock-in failed: {status} - {r.text}"
    attendance_id = r.json()["id"]

    # Then clock out for self
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/clock-out", employee_jwt,
                           {"employee_id": 30, "attendance_id": attendance_id})

    assert status == 200, f"Clock-out failed: {status} - {r.text}"
    print(f"✅ Employee clock-out successful for attendance: {attendance_id}")

def test_employee_break_start_and_end(employee_jwt):
    """Test employee break start and end functionality"""
    # Clock in first for self
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", employee_jwt,
                           {"employee_id": 30, "notes": "Employee break test"})

    assert status == 201, f"Clock-in failed: {status} - {r.text}"
    attendance_id = r.json()["id"]

    # Start break
    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", employee_jwt,
                           {"attendance_id": attendance_id, "break_type": "lunch"})

    assert status == 201, f"Break start failed: {status} - {r.text}"
    break_id = r.json()["id"]

    # End break
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/breaks/{break_id}/end", employee_jwt, {})

    assert status == 200, f"Break end failed: {status} - {r.text}"
    print(f"✅ Employee break start/end successful: break {break_id}")

def test_employee_active_attendance_retrieval(employee_jwt):
    """Test employee active attendance retrieval"""
    # Retrieve active attendance for self (assuming already clocked in)
    status, r = safe_request('GET', f"{BASE_URL}/attendance/active/30", employee_jwt)

    assert status == 200, f"Active attendance retrieval failed: {status} - {r.text}"
    records = r.json()
    assert isinstance(records, list)
    assert len(records) > 0
    print(f"✅ Employee active attendance retrieved: {len(records)} records")

# ===== ADMIN TESTS (always run) =====

def test_admin_clock_in_override(admin_jwt):
    """Test admin clock-in override for employee"""
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Admin override clock-in"})

    assert status == 201, f"Admin clock-in failed: {status} - {r.text}"
    attendance_data = r.json()
    assert "id" in attendance_data
    print(f"✅ Admin clock-in override successful: {attendance_data['id']}")

def test_admin_clock_out_override(admin_jwt):
    """Test admin clock-out override for employee"""
    # Clock in first
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Admin override clock-out"})

    attendance_id = r.json()["id"]

    # Clock out
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/clock-out", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "attendance_id": attendance_id})

    assert status == 200, f"Admin clock-out failed: {status} - {r.text}"
    print(f"✅ Admin clock-out override successful for attendance: {attendance_id}")

def test_admin_break_management(admin_jwt):
    """Test admin break management for employee"""
    # Clock in
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Admin break test"})

    attendance_id = r.json()["id"]

    # Start break
    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", admin_jwt,
                           {"attendance_id": attendance_id, "break_type": "lunch"})

    break_id = r.json()["id"]

    # End break
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/breaks/{break_id}/end", admin_jwt, {})

    assert status == 200, f"Admin break end failed: {status} - {r.text}"
    print(f"✅ Admin break management successful: break {break_id}")

def test_admin_active_attendance_retrieval(admin_jwt):
    """Test admin active attendance retrieval"""
    # Clock in first
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Admin active attendance test"})

    attendance_id = r.json()["id"]

    # Retrieve active attendance
    status, r = safe_request('GET', f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", admin_jwt)

    assert status == 200, f"Admin active attendance retrieval failed: {status} - {r.text}"
    records = r.json()
    assert isinstance(records, list)
    assert len(records) > 0
    print(f"✅ Admin active attendance retrieved: {len(records)} records")

# ===== EDGE CASE TESTS =====

def test_multiple_breaks_without_ending(admin_jwt):
    """Test starting multiple breaks without ending previous ones"""
    # Clock in
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Multiple breaks test"})

    attendance_id = r.json()["id"]

    # Start first break
    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", admin_jwt,
                           {"attendance_id": attendance_id, "break_type": "lunch"})

    break1_id = r.json()["id"]

    # Start second break without ending first (should this be allowed?)
    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", admin_jwt,
                           {"attendance_id": attendance_id, "break_type": "coffee"})

    if status == 201:
        break2_id = r.json()["id"]
        print(f"✅ Multiple breaks allowed: break1={break1_id}, break2={break2_id}")
    else:
        print(f"ℹ️ Multiple breaks not allowed: {status} - {r.text}")

def test_double_break_end(admin_jwt):
    """Test ending the same break twice"""
    # Clock in and start break
    status, r = safe_request('POST', f"{BASE_URL}/attendance/clock-in", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "notes": "Double break end test"})

    attendance_id = r.json()["id"]

    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", admin_jwt,
                           {"attendance_id": attendance_id, "break_type": "lunch"})

    break_id = r.json()["id"]

    # End break first time
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/breaks/{break_id}/end", admin_jwt, {})

    assert status == 200, f"First break end failed: {status} - {r.text}"

    # End break second time
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/breaks/{break_id}/end", admin_jwt, {})

    if status == 200:
        print(f"✅ Double break end allowed for break: {break_id}")
    else:
        print(f"ℹ️ Double break end prevented: {status} - {r.text}")

def test_clock_out_without_clock_in(admin_jwt):
    """Test clocking out without an active attendance"""
    # Try to clock out without clocking in first
    status, r = safe_request('PUT', f"{BASE_URL}/attendance/clock-out", admin_jwt,
                           {"employee_id": EMPLOYEE_ID, "attendance_id": 99999})

    if status == 404:
        print("✅ Clock-out without active attendance properly rejected")
    else:
        print(f"ℹ️ Clock-out without active attendance: {status} - {r.text}")

def test_invalid_attendance_id_operations(admin_jwt):
    """Test operations with invalid attendance IDs"""
    # Try break operations with invalid attendance ID
    status, r = safe_request('POST', f"{BASE_URL}/attendance/breaks/start", admin_jwt,
                           {"attendance_id": 99999, "break_type": "lunch"})

    if status == 404:
        print("✅ Invalid attendance ID for break start properly rejected")
    else:
        print(f"ℹ️ Invalid attendance ID handling: {status} - {r.text}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
