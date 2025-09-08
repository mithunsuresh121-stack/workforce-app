#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import requests

# --- Configuration ---
BACKEND_DIR = "backend"  # relative path to backend folder
HEALTH_URL = "http://localhost:8000/health"
TEST_USERS = [
    {"email": "admin@example.com", "password": "password123"},
]

PLAYWRIGHT_TEST_CMD = ["npx", "playwright", "test", "frontend/web-app/tests/payroll-management.spec.ts"]

# --- Step 1: Verify current path ---
current_path = os.getcwd()
expected_path = os.path.abspath(".")
backend_path = os.path.join(expected_path, BACKEND_DIR)

if not os.path.exists(os.path.join(backend_path, "app", "main.py")):
    print(f"❌ Backend main.py not found in {backend_path}")
    sys.exit(1)
print(f"✅ Backend path verified: {backend_path}")

# --- Step 2: Check backend health ---
try:
    r = requests.get(HEALTH_URL, timeout=5)
    if r.status_code == 200:
        print(f"✅ Backend server running at {HEALTH_URL}")
    else:
        print(f"⚠️ Backend responded with status {r.status_code}")
        sys.exit(1)
except requests.exceptions.RequestException:
    print(f"❌ Backend not reachable at {HEALTH_URL}")
    sys.exit(1)

# --- Step 3: Verify/Create test users ---
# This example assumes a FastAPI endpoint exists to create users (adjust as needed)
for user in TEST_USERS:
    try:
        response = requests.post(f"http://localhost:8000/users/create", json=user, timeout=5)
        if response.status_code in [200, 201]:
            print(f"✅ Test user verified/created: {user['email']}")
        else:
            print(f"⚠️ Could not verify/create user {user['email']}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to backend for user creation: {e}")
        sys.exit(1)

# --- Step 4: Run Playwright tests ---
print("▶️ Running Payroll Management Playwright tests...")
try:
    subprocess.run(PLAYWRIGHT_TEST_CMD, check=True)
    print("✅ Playwright tests completed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Playwright tests failed with code {e.returncode}")
    sys.exit(1)
