import requests
import pytest
import time
from datetime import datetime, timezone

def cleanup_active_attendance(base_url, employee_id, employee_jwt, auth_headers):
    """
    Cleans up any active attendance records for the given employee.
    """
    r = requests.get(f"{base_url}/attendance/active/{employee_id}", headers=auth_headers(employee_jwt))
    if r.status_code == 200:
        records = r.json()
        for record in records:
            print(f"Cleaning up active record: {record}")
            r_out = requests.put(
                f"{base_url}/attendance/clock-out",
                json={"employee_id": employee_id, "attendance_id": record["id"]},
                headers=auth_headers(employee_jwt)
            )
            print(f"Clock-out result: {r_out.status_code}")
    elif r.status_code == 404:
        print("No active attendance records to clean up")
    else:
        print(f"Failed to check active attendance: {r.status_code} - {r.text}")

def cleanup_active_breaks(base_url, employee_id, employee_jwt, auth_headers):
    """
    Optional: Cleans up active breaks if the system allows multiple breaks.
    """
    r = requests.get(f"{base_url}/attendance/active/{employee_id}", headers=auth_headers(employee_jwt))
    if r.status_code == 200:
        records = r.json()
        for record in records:
            for br in record.get("breaks", []):
                if not br.get("end_time"):
                    r_out = requests.put(
                        f"{base_url}/attendance/break-end",
                        json={"employee_id": employee_id, "attendance_id": record["id"], "break_id": br["id"]},
                        headers=auth_headers(employee_jwt)
                    )
                    print(f"Break cleanup result: {r_out.status_code}")
    else:
        print(f"Failed to check active attendance for breaks: {r.status_code} - {r.text}")

@pytest.fixture(scope="function", autouse=True)
def pre_post_cleanup(base_url, employee_jwt, auth_headers):
    """
    Runs before and after each test to ensure no leftover attendance or breaks.
    """
    # Get employee ID from JWT (assuming it's 30 for test@company.com)
    employee_id = 30
    cleanup_active_attendance(base_url, employee_id, employee_jwt, auth_headers)
    cleanup_active_breaks(base_url, employee_id, employee_jwt, auth_headers)
    yield
    cleanup_active_attendance(base_url, employee_id, employee_jwt, auth_headers)
    cleanup_active_breaks(base_url, employee_id, employee_jwt, auth_headers)

def test_clock_in_and_out(base_url, employee_jwt, auth_headers):
    print("\n=== Testing clock-in and clock-out ===")

    employee_id = 30  # Employee ID for test@company.com

    # Clock-in
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Starting shift"},
        headers=auth_headers(employee_jwt),
    )
    assert r.status_code == 201, f"Clock-in failed: {r.status_code} - {r.text}"
    attendance_id = r.json()["id"]
    print(f"✅ Clock-in successful, attendance_id={attendance_id}")

    # Clock-out
    r_out = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(employee_jwt),
    )
    assert r_out.status_code == 200, f"Clock-out failed: {r_out.status_code} - {r_out.text}"
    print(f"✅ Clock-out successful for attendance_id={attendance_id}")

def test_break_start_and_end(base_url, employee_jwt, auth_headers):
    print("\n=== Testing break start and end ===")

    employee_id = 30  # Employee ID for test@company.com

    # Ensure fresh attendance
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Shift for break test"},
        headers=auth_headers(employee_jwt),
    )
    assert r.status_code == 201, f"Clock-in for break test failed: {r.status_code} - {r.text}"
    attendance_id = r.json()["id"]

    # Start break
    r_break_start = requests.post(
        f"{base_url}/attendance/break-start",
        json={"employee_id": employee_id, "attendance_id": attendance_id, "notes": "Starting break"},
        headers=auth_headers(employee_jwt),
    )
    assert r_break_start.status_code == 201, f"Break start failed: {r_break_start.status_code} - {r_break_start.text}"
    break_id = r_break_start.json()["id"]
    print(f"✅ Break started, break_id={break_id}")

    time.sleep(1)  # Simulate break duration

    # End break
    r_break_end = requests.post(
        f"{base_url}/attendance/break-end",
        json={"employee_id": employee_id, "attendance_id": attendance_id, "break_id": break_id},
        headers=auth_headers(employee_jwt),
    )
    assert r_break_end.status_code == 200, f"Break end failed: {r_break_end.status_code} - {r_break_end.text}"
    print(f"✅ Break ended successfully, break_id={break_id}")

    # Clock-out after break
    r_out = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(employee_jwt),
    )
    assert r_out.status_code == 200, f"Clock-out after break failed: {r_out.status_code} - {r_out.text}"
    print(f"✅ Clock-out successful for attendance_id={attendance_id}")

def test_active_attendance_retrieval(base_url, employee_jwt, auth_headers):
    print("\n=== Testing active attendance retrieval ===")

    employee_id = 30  # Employee ID for test@company.com

    # Clock-in
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Active attendance test"},
        headers=auth_headers(employee_jwt),
    )
    assert r.status_code == 201, f"Clock-in failed: {r.status_code} - {r.text}"

    # Retrieve active attendance
    r_active = requests.get(f"{base_url}/attendance/active/{employee_id}", headers=auth_headers(employee_jwt))
    assert r_active.status_code == 200, f"Active attendance retrieval failed: {r_active.status_code} - {r_active.text}"
    records = r_active.json()
    assert len(records) > 0, "No active attendance found"
    print(f"✅ Active attendance retrieved: {records}")

def test_breaks_retrieval_for_attendance(base_url, employee_jwt, auth_headers):
    print("\n=== Testing retrieval of breaks for attendance ===")

    employee_id = 30  # Employee ID for test@company.com

    # Clock-in
    r = requests.post(
        f"{base_url}/attendance/clock-in",
        json={"employee_id": employee_id, "notes": "Break retrieval test"},
        headers=auth_headers(employee_jwt),
    )
    assert r.status_code == 201, f"Clock-in failed: {r.status_code} - {r.text}"
    attendance_id = r.json()["id"]

    # Start break
    r_break = requests.post(
        f"{base_url}/attendance/break-start",
        json={"employee_id": employee_id, "attendance_id": attendance_id, "notes": "Testing break retrieval"},
        headers=auth_headers(employee_jwt),
    )
    assert r_break.status_code == 201, f"Break start failed: {r_break.status_code} - {r_break.text}"

    # Retrieve breaks for attendance
    r_breaks = requests.get(f"{base_url}/attendance/breaks/{attendance_id}", headers=auth_headers(employee_jwt))
    assert r_breaks.status_code == 200, f"Break retrieval failed: {r_breaks.status_code} - {r_breaks.text}"
    breaks = r_breaks.json()
    assert len(breaks) > 0, "No breaks found"
    print(f"✅ Breaks retrieved: {breaks}")

    # Clock-out
    r_out = requests.put(
        f"{base_url}/attendance/clock-out",
        json={"employee_id": employee_id, "attendance_id": attendance_id},
        headers=auth_headers(employee_jwt),
    )
    assert r_out.status_code == 200, f"Clock-out failed: {r_out.status_code} - {r_out.text}"
    print(f"✅ Clock-out successful for attendance_id={attendance_id}")
