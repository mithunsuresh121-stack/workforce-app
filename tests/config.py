import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
EMPLOYEE_ID = int(os.getenv("EMPLOYEE_ID", "1"))
EMPLOYEE_JWT = os.getenv("EMPLOYEE_JWT", "")

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
