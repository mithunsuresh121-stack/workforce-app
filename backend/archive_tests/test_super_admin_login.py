import requests


def test_super_admin_login():
    url = "http://localhost:8000/auth/login"
    payload = {"email": "admin@app.com", "password": "supersecure123"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data, "No access token in response"
    print("Super Admin login test passed.")


if __name__ == "__main__":
    test_super_admin_login()
