import requests
import json

BASE_URL = "http://localhost:8080"

# Test users with their credentials
test_users = [
    {
        "role": "SuperAdmin",
        "email": "admin@app.com",
        "password": "supersecure123",
        "company_id": None
    },
    {
        "role": "SuperAdmin",
        "email": "test_superadmin@example.com",
        "password": "password123",
        "company_id": None
    },
    {
        "role": "CompanyAdmin",
        "email": "test_companyadmin@example.com",
        "password": "password123",
        "company_id": 1
    },
    {
        "role": "Manager",
        "email": "test_manager@example.com",
        "password": "password123",
        "company_id": 1
    },
    {
        "role": "Employee",
        "email": "test_employee@example.com",
        "password": "password123",
        "company_id": 1
    }
]

def test_login(email, password, company_id):
    """Test login for a user and return the response"""
    login_data = {
        "email": email,
        "password": password,
        "company_id": company_id
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": "ERROR",
            "response": str(e),
            "success": False
        }

def main():
    print("Testing login for all user roles...\n")

    results = []

    for user in test_users:
        print(f"Testing {user['role']}: {user['email']}")
        result = test_login(user['email'], user['password'], user['company_id'])

        result_data = {
            "role": user['role'],
            "email": user['email'],
            "password": user['password'],
            "company_id": user['company_id'],
            "login_success": result['success'],
            "status_code": result['status_code'],
            "response": result['response']
        }

        results.append(result_data)

        if result['success']:
            print(f"✅ Login successful")
            # Extract token if available
            if isinstance(result['response'], dict) and 'access_token' in result['response']:
                result_data['token'] = result['response']['access_token'][:50] + "..."  # Truncate for display
        else:
            print(f"❌ Login failed: {result['status_code']} - {result['response']}")

        print("-" * 50)

    # Print summary table
    print("\n" + "="*80)
    print("USER ACCOUNTS SUMMARY")
    print("="*80)
    print("<10")
    print("-"*80)

    for result in results:
        status = "✅ Working" if result['login_success'] else "❌ Failed"
        company = f"Company {result['company_id']}" if result['company_id'] else "No Company"
        print("<10")

    print("\n" + "="*80)
    print("WORKING CREDENTIALS FOR TESTING:")
    print("="*80)

    for result in results:
        if result['login_success']:
            print(f"Role: {result['role']}")
            print(f"Email: {result['email']}")
            print(f"Password: {result['password']}")
            print(f"Company: {'Company ' + str(result['company_id']) if result['company_id'] else 'No Company'}")
            print("-" * 40)

if __name__ == "__main__":
    main()
