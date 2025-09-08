#!/usr/bin/env python3
import os
import sys
import json
import time
import requests

# Config (environment overrides supported)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
EMPLOYEE_ID = int(os.getenv("EMPLOYEE_ID", "30"))
TOKEN = os.getenv("EMPLOYEE_JWT") or (
    open(os.path.join(os.path.dirname(__file__), "..", "token.txt")).read().strip()
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "token.txt")) else None
)
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports", "archive", "attendance"))
os.makedirs(OUT_DIR, exist_ok=True)

if not TOKEN:
    print("ERROR: No JWT token found. Set EMPLOYEE_JWT env var or place token.txt in repo root.", file=sys.stderr)
    sys.exit(2)

headers = {"Authorization": f"Bearer {TOKEN}"}

def save(name, data):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {path}")

def request_json(method, url, **kwargs):
    kwargs.setdefault("timeout", 10)
    r = requests.request(method, url, **kwargs)
    # try to parse JSON else return text
    try:
        body = r.json()
    except Exception:
        body = r.text
    return r.status_code, body, r

# 1) Verify token by calling /auth/me
status, body, resp = request_json("GET", f"{BASE_URL}/auth/me", headers=headers)
save("auth_me.json", {"status": status, "body": body})
if status != 200:
    print("ERROR: Token verification failed:", status, body, file=sys.stderr)
    sys.exit(3)

print("Authenticated as:", body.get("email"), "role:", body.get("role"))

# Ensure token belongs to Employee (clock-in must be employee role)
role = body.get("role")
if role != "Employee":
    print(f"ERROR: Token role is '{role}'. Clock-in must be performed by an Employee role. Aborting.", file=sys.stderr)
    sys.exit(4)

# 2) Check active attendance for the employee
status, body, resp = request_json("GET", f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=headers)
save("active_before.json", {"status": status, "body": body})
if status == 200 and body:
    print("Active attendance already exists for employee", EMPLOYEE_ID)
    print(body)
else:
    # 3) Create an active attendance via clock-in
    payload = {"employee_id": EMPLOYEE_ID, "notes": "automated-test-clock-in"}
    status, body, resp = request_json("POST", f"{BASE_URL}/attendance/clock-in", headers=headers, json=payload)
    save("clock_in_response.json", {"status": status, "body": body})
    print("Clock-in response:", status)
    if status not in (200, 201):
        # Detailed guidance for debugging
        if status == 422:
            print("VALIDATION ERROR (422). Response:", body, file=sys.stderr)
            print("Suggestion: check required fields and formats for /attendance/clock-in payload.", file=sys.stderr)
        elif status == 403:
            print("ACCESS DENIED (403). Response:", body, file=sys.stderr)
            print("Suggestion: ensure the token belongs to the employee and company isolation is correct.", file=sys.stderr)
        else:
            print("Unexpected status code. Response:", body, file=sys.stderr)
        sys.exit(5)
    print("Clock-in created successfully.")

# 4) Confirm active attendance now
time.sleep(1)
status, body, resp = request_json("GET", f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=headers)
save("active_after.json", {"status": status, "body": body})
if status == 200 and body:
    print("Confirmed active attendance:", body)
else:
    print("Failed to confirm active attendance after clock-in. Response:", status, body, file=sys.stderr)
    sys.exit(6)

print("SUCCESS: Employee", EMPLOYEE_ID, "has an active attendance session.")
sys.exit(0)
