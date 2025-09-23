import requests
import json

# Test the new contribution endpoints
BASE_URL = "http://localhost:8001/api"

def test_contribution_endpoints():
    # First, let's try to get a token by logging in
    login_data = {
        "email": "demo@company.com",  # Existing test user
        "password": "password123",      # Existing test user password
        "company_id": 4                 # Company ID
    }

    try:
        # Try to login
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            print("Login successful!")
            print(f"Token: {token[:50]}...")

            # Test our new contribution endpoints
            print("\n=== Testing New Contribution Endpoints ===")

            # Test tasks completed endpoint
            tasks_completed_response = requests.get(f"{BASE_URL}/dashboard/charts/contribution/tasks-completed", headers=headers)
            print(f"Tasks Completed Status: {tasks_completed_response.status_code}")
            if tasks_completed_response.status_code == 200:
                print("Tasks Completed Data:", json.dumps(tasks_completed_response.json(), indent=2))
            elif tasks_completed_response.status_code == 403:
                print("Tasks Completed Access Denied (expected for non-employees):", tasks_completed_response.json())

            # Test tasks created endpoint
            tasks_created_response = requests.get(f"{BASE_URL}/dashboard/charts/contribution/tasks-created", headers=headers)
            print(f"Tasks Created Status: {tasks_created_response.status_code}")
            if tasks_created_response.status_code == 200:
                print("Tasks Created Data:", json.dumps(tasks_created_response.json(), indent=2))
            elif tasks_created_response.status_code == 403:
                print("Tasks Created Access Denied (expected for non-employees):", tasks_created_response.json())

            # Test productivity endpoint
            productivity_response = requests.get(f"{BASE_URL}/dashboard/charts/contribution/productivity", headers=headers)
            print(f"Productivity Status: {productivity_response.status_code}")
            if productivity_response.status_code == 200:
                print("Productivity Data:", json.dumps(productivity_response.json(), indent=2))
            elif productivity_response.status_code == 403:
                print("Productivity Access Denied (expected for non-employees):", productivity_response.json())

        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Make sure the backend is running on port 8001.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_contribution_endpoints()
