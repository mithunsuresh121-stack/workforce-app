import requests

BASE_URL = "http://localhost:8000"
EMPLOYEE_ID = 30
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGNvbXBhbnkuY29tIiwiY29tcGFueV9pZCI6MSwicm9sZSI6IkVtcGxveWVlIiwiZXhwIjoxNzU3MzI2ODYzfQ.vWbCJutMAVEgJUHAm0qVDPz89Y1PHqs1zv4q_WLGZ3U"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def check_active_attendance():
    r = requests.get(f"{BASE_URL}/attendance/active/{EMPLOYEE_ID}", headers=HEADERS)
    print(f"Check active attendance status: {r.status_code}")
    print(f"Response: {r.text}")
    return r

def create_active_attendance():
    payload = {"employee_id": EMPLOYEE_ID, "notes": "Auto-created active attendance for tests"}
    r = requests.post(f"{BASE_URL}/attendance/clock-in", json=payload, headers=HEADERS)
    print(f"Create active attendance status: {r.status_code}")
    print(f"Response: {r.text}")
    return r

def main():
    r = check_active_attendance()
    if r.status_code != 200 or not r.json():
        print("No active attendance found, creating one...")
        create_active_attendance()
    else:
        print("Active attendance session already exists.")

if __name__ == "__main__":
    main()
