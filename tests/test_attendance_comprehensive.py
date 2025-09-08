import pytest
import requests


@pytest.fixture(scope="module")
def tokens(base_url):
    """Retrieve JWT tokens for admin and employee."""
    admin_r = requests.post(
        f"{base_url}/auth/login",
        json={"email": "admin@app.com", "password": "supersecure123"},
    )
    admin_r.raise_for_status()
    admin_jwt = admin_r.json()["access_token"]

    employee_r = requests.post(
        f"{base_url}/auth/login",
        json={"email": "test@company.com", "password": "password123"},
    )
    employee_r.raise_for_status()
    employee_jwt = employee_r.json()["access_token"]

    return {"admin": admin_jwt, "employee": employee_jwt}


@pytest.fixture
def cleanup_active_attendance(base_url, tokens, auth_headers):
    """Clock out any lingering active attendance before each test."""
    # Get employee ID from JWT token (employee ID is 32)
    employee_id = 32

    r = requests.get(
        f"{base_url}/attendance/active/{employee_id}", headers=auth_headers(tokens["admin"])
    )
    if r.status_code == 200:
        for record in r.json():
            requests.put(
                f"{base_url}/attendance/clock-out",
                json={"employee_id": employee_id, "attendance_id": record["id"]},
                headers=auth_headers(tokens["admin"]),
            )


def test_employee_cannot_clock_in_without_permission(base_url, tokens, auth_headers, cleanup_active_attendance):
    """Employee should be denied access if not permitted."""
    employee_id = 32
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Employee test"},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 403


def test_admin_can_clock_in_and_out(base_url, tokens, auth_headers, cleanup_active_attendance):
    """Admin can clock in, start/end breaks, and clock out."""
    employee_id = 32

    # Clock in
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Admin test"},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 201
    attendance = r.json()
    attendance_id = attendance["id"]

    # Start break
    r = requests.post(
        f"{base_url}/attendance/breaks/start",
        json={"attendance_id": attendance_id, "break_type": "lunch"},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 201
    break_id = r.json()["id"]

    # End break
    r = requests.put(
        f"{base_url}/attendance/breaks/{break_id}/end",
        json={},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 200

    # Clock out
    r = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"


def test_employee_break_edge_cases(base_url, tokens, auth_headers, cleanup_active_attendance):
    """Test breaks and edge cases using admin for clock-in and employee for breaks."""
    employee_id = 30

    # Admin clocks in
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Edge case test"},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 201
    attendance_id = r.json()["id"]

    # Employee starts break
    r = requests.post(
        f"{base_url}/attendance/breaks/start",
        json={"attendance_id": attendance_id, "break_type": "coffee"},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 201
    break_id = r.json()["id"]

    # Edge case: start another break without ending
    r = requests.post(
        f"{base_url}/attendance/breaks/start",
        json={"attendance_id": attendance_id, "break_type": "lunch"},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 400  # should fail due to existing active break

    # Employee ends break
    r = requests.put(
        f"{base_url}/attendance/breaks/{break_id}/end",
        json={},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 200

    # Edge case: end same break twice
    r = requests.put(
        f"{base_url}/attendance/breaks/{break_id}/end",
        json={},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 400  # already ended

    # Clock out
    r = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 200


def test_permission_denied_for_other_users_break(base_url, tokens, auth_headers, cleanup_active_attendance):
    """Employee cannot end someone else's break."""
    employee_id = 32

    # Admin clocks in and starts break
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Permission test"},
        headers=auth_headers(tokens["admin"]),
    )
    attendance_id = r.json()["id"]

    r = requests.post(
        f"{base_url}/attendance/breaks/start",
        json={"attendance_id": attendance_id, "break_type": "lunch"},
        headers=auth_headers(tokens["admin"]),
    )
    break_id = r.json()["id"]

    # Employee attempts to end admin's break
    r = requests.put(
        f"{base_url}/attendance/breaks/{break_id}/end",
        json={},
        headers=auth_headers(tokens["employee"]),
    )
    assert r.status_code == 403

    # Admin ends the break to clean up
    r = requests.put(
        f"{base_url}/attendance/breaks/{break_id}/end",
        json={},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 200

    # Admin clocks out
    r = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(tokens["admin"]),
    )
    assert r.status_code == 200
