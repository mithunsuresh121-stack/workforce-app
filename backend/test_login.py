import requests

# Demo credentials
url = "http://localhost:8000/api/v1/auth/login"
payload = {
    "email": "admin@techcorp.com",
    "password": "password123"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Login successful:", response.json())
else:
    print("Login failed:", response.status_code, response.text)
