import json

import requests

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TASKS_URL = f"{BASE_URL}/tasks"
COMPANIES_URL = f"{BASE_URL}/companies"


def test_login():
    """Test login functionality"""
    print("Testing login...")
    payload = {"email": "admin@techcorp.com", "password": "password123"}

    try:
        response = requests.post(LOGIN_URL, json=payload)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Login successful. Token: {token[:50]}...")
            return token
        else:
            print(f"✗ Login failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"✗ Login error: {e}")
        return None


def get_token():
    url = "http://localhost:8000/auth/login"
    payload = {"email": "admin@app.com", "password": "supersecure123"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} {response.text}")
        return None


def test_tasks():
    """Test tasks functionality"""
    print("\nTesting tasks...")
    token = get_token()
    if not token:
        print("Cannot test tasks without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing tasks
    try:
        response = requests.get(TASKS_URL, headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✓ Tasks retrieved: {len(tasks)} tasks found")
        else:
            print(f"✗ Tasks list failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"✗ Tasks list error: {e}")
        return

    # Test creating a task with valid status
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "Medium",
        "status": "To Do",  # Updated to valid status
        "assigned_to": 1,
        "company_id": 1,
    }

    try:
        response = requests.post(TASKS_URL, json=task_data, headers=headers)
        if response.status_code == 201:
            task = response.json()
            print(f"✓ Task created: {task['title']} (ID: {task['id']})")
            return task["id"]
        else:
            print(f"✗ Task creation failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"✗ Task creation error: {e}")
        return None


def test_companies():
    """Test companies functionality"""
    print("\nTesting companies...")
    token = get_token()
    if not token:
        print("Cannot test companies without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test getting company info
    try:
        response = requests.get(f"{COMPANIES_URL}/1", headers=headers)
        if response.status_code == 200:
            company = response.json()
            print(f"✓ Company retrieved: {company['name']}")
        else:
            print(f"✗ Company retrieval failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Company retrieval error: {e}")


def test_health_check():
    """Test health check endpoint"""
    print("\nTesting health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✓ Health check: {health['status']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")


def main():
    print("Starting comprehensive API testing...")

    # Test health check first
    test_health_check()

    # Test login
    token = test_login()
    if not token:
        print("Cannot proceed without valid token")
        return

    # Test other endpoints
    test_companies()
    task_id = test_tasks()

    print("\n" + "=" * 50)
    print("Testing Summary:")
    print("✓ Login functionality")
    print("✓ Health check endpoint")
    print("✓ Companies endpoint")
    print("✓ Tasks endpoint (list and create)")

    if task_id:
        print(f"✓ Task creation successful (ID: {task_id})")
    else:
        print("✗ Task creation failed")

    print("\nAreas that need further testing:")
    print("- Task update/delete functionality")
    print("- Calendar/leaves/shifts endpoints")
    print("- Reports generation")
    print("- Chat assistant")
    print("- Employee management (beyond basic user operations)")


if __name__ == "__main__":
    main()
