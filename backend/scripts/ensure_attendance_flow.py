#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
import glob

# Config
BASE_URL = "http://localhost:8000"
EMPLOYEE_EMAIL = "demo@company.com"
PASSWORD = "password123"
EMPLOYEE_ID = 30  # Updated to ID 30 as requested
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "token.txt")

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    print(f"Token saved to {TOKEN_FILE}")

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def request_json(method, url, **kwargs):
    kwargs.setdefault("timeout", 10)
    r = requests.request(method, url, **kwargs)
    try:
        body = r.json()
    except Exception:
        body = r.text
    return r.status_code, body, r

def main():
    print("=== Step 1: Employee JWT Token Refresh ===")
    # Login to get fresh token
    login_payload = {"email": EMPLOYEE_EMAIL, "password": PASSWORD}
    status, body, resp = request_json("POST", f"{BASE_URL}/auth/login", json=login_payload)
    if status != 200:
        print(f"ERROR: Login failed with status {status}: {body}")
        sys.exit(1)
    token = body.get("access_token")
    if not token:
        print("ERROR: No access_token in login response")
        sys.exit(1)
    print("Login successful, token obtained.")
    save_token(token)

    headers = {"Authorization": f"Bearer {token}"}

    # Verify token
    status, body, resp = request_json("GET", f"{BASE_URL}/auth/me", headers=headers)
    if status != 200:
        print(f"ERROR: Token verification failed: {status} {body}")
        sys.exit(1)
    print(f"Authenticated as: {body.get('email')} role: {body.get('role')}")
    if body.get('role') != 'Employee':
        print(f"ERROR: Token role is {body.get('role')}, expected Employee")
        sys.exit(1)

    print("\n=== Step 2: Verify Active Attendance Session ===")
    status, body, resp = request_json("GET", f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=headers)
    if status == 200 and body:
        print("Active attendance session exists.")
        active_exists = True
    elif status == 404 or not body:
        print("No active attendance session found.")
        active_exists = False
    else:
        print(f"ERROR: Failed to check active attendance: {status} {body}")
        sys.exit(1)

    if not active_exists:
        print("\n=== Step 3: Create Active Attendance Session ===")
        clockin_payload = {"employee_id": EMPLOYEE_ID, "notes": "Automatic test clock-in"}
        status, body, resp = request_json("POST", f"{BASE_URL}/attendance/clock-in", headers=headers, json=clockin_payload)
        if status not in (200, 201):
            print(f"ERROR: Clock-in failed: {status} {body}")
            sys.exit(1)
        print("Clock-in successful.")

        # Confirm active session
        time.sleep(1)
        status, body, resp = request_json("GET", f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=headers)
        if status == 200 and body:
            print("Confirmed active attendance session created.")
        else:
            print(f"ERROR: Failed to confirm active session: {status} {body}")
            sys.exit(1)

    print("\n=== Step 4: Execute Attendance Tests ===")
    # Change to repo root
    repo_root = os.path.join(os.path.dirname(__file__), "..", "..")
    os.chdir(repo_root)

    # Dynamically find all attendance test files matching pattern
    test_files = glob.glob("tests/test_attendance_*.py")
    if not test_files:
        print("ERROR: No attendance test files found matching tests/test_attendance_*.py")
        sys.exit(1)

    cmd = ["python", "-m", "pytest"] + test_files + ["-v", "--tb=short"]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Return code: {result.returncode}")

    print("\n=== Step 5: Validate Flow ===")
    # Check if any tests were skipped
    skipped = "SKIPPED" in result.stdout
    if skipped:
        print("WARNING: Some tests were skipped.")
    else:
        print("✅ No tests were skipped.")

    # Check for 401 errors
    if "401" in result.stdout or "401" in result.stderr:
        print("ERROR: 401 errors detected in test output.")
    else:
        print("✅ No 401 errors detected.")

    if result.returncode == 0:
        print("✅ All tests passed.")
    else:
        print("❌ Some tests failed.")

    print("\n=== Final Summary ===")
    print(f"Employee {EMPLOYEE_ID} has active attendance session: ✅")
    print(f"Fresh token saved to {TOKEN_FILE}: ✅")
    print(f"Tests executed without skipping: {'❌' if skipped else '✅'}")
    print(f"Test results: {'Passed' if result.returncode == 0 else 'Failed'}")

if __name__ == "__main__":
    main()
