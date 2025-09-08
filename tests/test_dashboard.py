import requests
import json

# Test the dashboard endpoints
BASE_URL = "http://localhost:8000"

def test_dashboard_endpoints():
    # First, let's try to get a token by logging in
    login_data = {
        "email": "admin@techcorp.com",  # Existing test user
        "password": "password123",      # Existing test user password
        "company_id": 1                 # Company ID
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
            
            # Test KPIs endpoint
            kpis_response = requests.get(f"{BASE_URL}/dashboard/kpis", headers=headers)
            print(f"KPIs Status: {kpis_response.status_code}")
            if kpis_response.status_code == 200:
                print("KPIs Data:", json.dumps(kpis_response.json(), indent=2))
            
            # Test recent activities endpoint
            activities_response = requests.get(f"{BASE_URL}/dashboard/recent-activities", headers=headers)
            print(f"Activities Status: {activities_response.status_code}")
            if activities_response.status_code == 200:
                print("Activities Data:", json.dumps(activities_response.json(), indent=2))
            
            # Test task status chart endpoint
            task_status_response = requests.get(f"{BASE_URL}/dashboard/charts/task-status", headers=headers)
            print(f"Task Status Status: {task_status_response.status_code}")
            if task_status_response.status_code == 200:
                print("Task Status Data:", json.dumps(task_status_response.json(), indent=2))
                
        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Make sure the backend is running.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dashboard_endpoints()
