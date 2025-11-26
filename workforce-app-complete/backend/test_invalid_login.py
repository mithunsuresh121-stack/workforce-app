import requests

# Invalid credentials test
url = "http://localhost:8000/auth/login"
payload = {
    "email": "admin@techcorp.com",
    "password": "wrongpassword",
    "company_id": 1
}

response = requests.post(url, json=payload)

print("Invalid login test:")
if response.status_code == 200:
    print("ERROR: Login should have failed but succeeded:", response.json())
else:
    print("SUCCESS: Login correctly failed with status:", response.status_code)
    print("Response:", response.text)
