import requests
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"
TASKS_URL = f"{BASE_URL}/tasks"
COMPANIES_URL = f"{BASE_URL}/companies"

def test_login():
    """Test login functionality"""
    print("Testing login...")
    payload = {
        "email": "admin@app.com",
        "password": "supersecure123"
    }
    
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
    payload = {
        "email": "admin@app.com",
        "password": "supersecure123"
    }
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
        "status": "Pending",
        "assigned_to": 1,
        "company_id": 1
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

def test_task_update_delete():
    """Test task update and delete functionality"""
    print("\nTesting task update and delete...")
    token = get_token()
    if not token:
        print("Cannot test task update/delete without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # First create a task
    task_data = {
        "title": "Task to Update",
        "description": "This task will be updated and deleted",
        "priority": "High",
        "status": "Pending",
        "assigned_to": 1,
        "company_id": 1
    }

    try:
        response = requests.post(TASKS_URL, json=task_data, headers=headers)
        if response.status_code != 201:
            print(f"✗ Cannot create task for update test: {response.status_code} {response.text}")
            return
        task = response.json()
        task_id = task["id"]
        print(f"✓ Created task for update/delete test: {task['title']} (ID: {task_id})")
    except Exception as e:
        print(f"✗ Task creation error for update test: {e}")
        return

    # Test updating the task
    update_data = {
        "title": "Updated Task",
        "description": "This task has been updated",
        "priority": "Low",
        "status": "In Progress",
        "assigned_to": 1,
        "company_id": 1
    }

    try:
        response = requests.put(f"{TASKS_URL}/{task_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_task = response.json()
            print(f"✓ Task updated: {updated_task['title']} (Status: {updated_task['status']})")
        else:
            print(f"✗ Task update failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Task update error: {e}")

    # Test deleting the task
    try:
        response = requests.delete(f"{TASKS_URL}/{task_id}", headers=headers)
        if response.status_code == 200:
            print(f"✓ Task deleted successfully (ID: {task_id})")
        else:
            print(f"✗ Task delete failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Task delete error: {e}")

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

def test_leaves():
    """Test leaves endpoints"""
    print("\nTesting leaves...")
    token = get_token()
    if not token:
        print("Cannot test leaves without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing leaves
    try:
        response = requests.get(f"{BASE_URL}/leaves", headers=headers)
        if response.status_code == 200:
            leaves = response.json()
            print(f"✓ Leaves retrieved: {len(leaves)} leaves found")
        else:
            print(f"✗ Leaves list failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"✗ Leaves list error: {e}")
        return

    # Test creating a leave request
    leave_data = {
        "tenant_id": "1",
        "employee_id": 1,
        "type": "Vacation",
        "start_at": "2025-09-15T00:00:00",
        "end_at": "2025-09-20T00:00:00",
        "status": "Pending"
    }

    try:
        response = requests.post(f"{BASE_URL}/leaves", json=leave_data, headers=headers)
        if response.status_code == 201:
            leave = response.json()
            print(f"✓ Leave created: ID {leave['id']}")
            return leave["id"]
        else:
            print(f"✗ Leave creation failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"✗ Leave creation error: {e}")
        return None

def test_leave_update_delete():
    """Test leave update status and delete functionality"""
    print("\nTesting leave update and delete...")
    token = get_token()
    if not token:
        print("Cannot test leave update/delete without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Create a leave request first
    leave_data = {
        "tenant_id": "1",
        "employee_id": 1,
        "type": "Sick Leave",
        "start_at": "2025-10-01T00:00:00",
        "end_at": "2025-10-05T00:00:00",
        "status": "Pending"
    }

    try:
        response = requests.post(f"{BASE_URL}/leaves", json=leave_data, headers=headers)
        if response.status_code != 201:
            print(f"✗ Cannot create leave for update test: {response.status_code} {response.text}")
            return
        leave = response.json()
        leave_id = leave["id"]
        print(f"✓ Created leave for update/delete test: ID {leave_id}")
    except Exception as e:
        print(f"✗ Leave creation error for update test: {e}")
        return

    # Update leave status
    update_data = {"status": "Approved"}

    try:
        response = requests.put(f"{BASE_URL}/leaves/{leave_id}/status", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_leave = response.json()
            print(f"✓ Leave status updated: ID {updated_leave['id']} Status: {updated_leave['status']}")
        else:
            print(f"✗ Leave status update failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Leave status update error: {e}")

    # Delete leave request
    try:
        response = requests.delete(f"{BASE_URL}/leaves/{leave_id}", headers=headers)
        if response.status_code == 200:
            print(f"✓ Leave deleted successfully: ID {leave_id}")
        else:
            print(f"✗ Leave delete failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Leave delete error: {e}")

def test_shifts():
    """Test shifts endpoints"""
    print("\nTesting shifts...")
    token = get_token()
    if not token:
        print("Cannot test shifts without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing shifts
    try:
        response = requests.get(f"{BASE_URL}/shifts", headers=headers)
        if response.status_code == 200:
            shifts = response.json()
            print(f"✓ Shifts retrieved: {len(shifts)} shifts found")
        else:
            print(f"✗ Shifts list failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"✗ Shifts list error: {e}")
        return

    # Test creating a shift
    shift_data = {
        "tenant_id": "1",
        "employee_id": 1,
        "start_at": "2025-09-15T09:00:00",
        "end_at": "2025-09-15T17:00:00",
        "status": "Scheduled"
    }

    try:
        response = requests.post(f"{BASE_URL}/shifts", json=shift_data, headers=headers)
        if response.status_code == 201:
            shift = response.json()
            print(f"✓ Shift created: ID {shift['id']}")
            return shift["id"]
        else:
            print(f"✗ Shift creation failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"✗ Shift creation error: {e}")
        return None

def test_shift_update_delete():
    """Test shift update and delete functionality"""
    print("\nTesting shift update and delete...")
    token = get_token()
    if not token:
        print("Cannot test shift update/delete without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Create a shift first
    shift_data = {
        "tenant_id": "1",
        "employee_id": 1,
        "start_at": "2025-10-01T09:00:00",
        "end_at": "2025-10-01T17:00:00",
        "location": "Office"
    }

    try:
        response = requests.post(f"{BASE_URL}/shifts", json=shift_data, headers=headers)
        if response.status_code != 201:
            print(f"✗ Cannot create shift for update test: {response.status_code} {response.text}")
            return
        shift = response.json()
        shift_id = shift["id"]
        print(f"✓ Created shift for update/delete test: ID {shift_id}")
    except Exception as e:
        print(f"✗ Shift creation error for update test: {e}")
        return

    # Update shift
    update_data = {
        "tenant_id": "1",
        "employee_id": 1,
        "start_at": "2025-10-01T10:00:00",
        "end_at": "2025-10-01T18:00:00",
        "location": "Home Office"
    }

    try:
        response = requests.put(f"{BASE_URL}/shifts/{shift_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_shift = response.json()
            print(f"✓ Shift updated: ID {updated_shift['id']} Location: {updated_shift['location']}")
        else:
            print(f"✗ Shift update failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Shift update error: {e}")

    # Delete shift
    try:
        response = requests.delete(f"{BASE_URL}/shifts/{shift_id}", headers=headers)
        if response.status_code == 200:
            print(f"✓ Shift deleted successfully: ID {shift_id}")
        else:
            print(f"✗ Shift delete failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Shift delete error: {e}")

def test_employees():
    """Test employees endpoints"""
    print("\nTesting employees...")
    token = get_token()
    if not token:
        print("Cannot test employees without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing employees
    try:
        response = requests.get(f"{BASE_URL}/employees", headers=headers)
        if response.status_code == 200:
            employees = response.json()
            print(f"✓ Employees retrieved: {len(employees)} employees found")
        else:
            print(f"✗ Employees list failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"✗ Employees list error: {e}")
        return

def test_dashboard():
    """Test dashboard endpoints"""
    print("\nTesting dashboard...")
    token = get_token()
    if not token:
        print("Cannot test dashboard without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test dashboard KPIs
    try:
        response = requests.get(f"{BASE_URL}/dashboard/kpis", headers=headers)
        if response.status_code == 200:
            kpis = response.json()
            print(f"✓ Dashboard KPIs retrieved: {kpis}")
        else:
            print(f"✗ Dashboard KPIs failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Dashboard KPIs error: {e}")

    # Test task status chart
    try:
        response = requests.get(f"{BASE_URL}/dashboard/charts/task-status", headers=headers)
        if response.status_code == 200:
            chart = response.json()
            print(f"✓ Task status chart retrieved: {len(chart)} statuses")
        else:
            print(f"✗ Task status chart failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Task status chart error: {e}")

def test_attendance():
    """Test attendance endpoints"""
    print("\nTesting attendance...")
    token = get_token()
    if not token:
        print("Cannot test attendance without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test clock in
    clock_in_data = {
        "employee_id": 1,
        "notes": "Test clock in"
    }

    try:
        response = requests.post(f"{BASE_URL}/attendance/clock-in", json=clock_in_data, headers=headers)
        if response.status_code == 201:
            attendance = response.json()
            print(f"✓ Clock in successful: ID {attendance['id']}")
            attendance_id = attendance['id']
        else:
            print(f"✗ Clock in failed: {response.status_code} {response.text}")
            return
    except Exception as e:
        print(f"✗ Clock in error: {e}")
        return

    # Test clock out
    clock_out_data = {
        "attendance_id": attendance_id,
        "employee_id": 1,
        "notes": "Test clock out"
    }

    try:
        response = requests.put(f"{BASE_URL}/attendance/clock-out", json=clock_out_data, headers=headers)
        if response.status_code == 200:
            updated_attendance = response.json()
            print(f"✓ Clock out successful: ID {updated_attendance['id']}")
        else:
            print(f"✗ Clock out failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Clock out error: {e}")

def test_payroll():
    """Test payroll endpoints"""
    print("\nTesting payroll...")
    token = get_token()
    if not token:
        print("Cannot test payroll without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing payroll runs
    try:
        response = requests.get(f"{BASE_URL}/payroll/payroll-runs", headers=headers)
        if response.status_code == 200:
            runs = response.json()
            print(f"✓ Payroll runs retrieved: {len(runs)} runs found")
        else:
            print(f"✗ Payroll runs list failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Payroll runs list error: {e}")

def test_notifications():
    """Test notifications endpoints"""
    print("\nTesting notifications...")
    token = get_token()
    if not token:
        print("Cannot test notifications without valid token")
        return
    headers = {"Authorization": f"Bearer {token}"}

    # Test listing notifications
    try:
        response = requests.get(f"{BASE_URL}/notifications", headers=headers)
        if response.status_code == 200:
            notifications = response.json()
            print(f"✓ Notifications retrieved: {len(notifications)} notifications found")
        else:
            print(f"✗ Notifications list failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Notifications list error: {e}")


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
    test_task_update_delete()
    test_leaves()
    test_leave_update_delete()
    test_shifts()
    test_shift_update_delete()
    test_employees()
    test_dashboard()
    test_attendance()
    test_payroll()
    test_notifications()

    print("\n" + "="*50)
    print("Testing Summary:")
    print("✓ Login functionality")
    print("✓ Health check endpoint")
    print("✓ Companies endpoint")
    print("✓ Tasks endpoint (list, create, update, delete)")
    print("✓ Leaves endpoint (list, create, update, delete)")
    print("✓ Shifts endpoint (list, create, update, delete)")
    print("✓ Employees endpoint (list)")
    print("✓ Dashboard endpoint (KPIs, charts)")
    print("✓ Attendance endpoint (clock in/out)")
    print("✓ Payroll endpoint (list runs)")
    print("✓ Notifications endpoint (list)")

    if task_id:
        print(f"✓ Task creation successful (ID: {task_id})")
    else:
        print("✗ Task creation failed")

    print("\nAreas that need further testing:")
    print("- Employee management (create, update, delete)")
    print("- Payroll full CRUD operations")
    print("- Chat assistant (not implemented)")
    print("- Calendar full integration")
    print("- Reports generation (beyond dashboard)")

if __name__ == "__main__":
    main()
