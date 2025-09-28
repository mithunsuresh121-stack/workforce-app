#!/usr/bin/env python3
import requests
import json
from tabulate import tabulate

# Test users
test_users = [
    {"email": "superadmin@workforce.com", "password": "password123", "expected_role": "SuperAdmin", "expected_company": "None"},
    {"email": "admin1@techcorp.com", "password": "password123", "expected_role": "CompanyAdmin", "expected_company": "TechCorp"},
    {"email": "admin2@innocorp.com", "password": "password123", "expected_role": "CompanyAdmin", "expected_company": "InnoCorp"},
    {"email": "emp1@techcorp.com", "password": "password123", "expected_role": "Employee", "expected_company": "TechCorp"},
    {"email": "emp5@techcorp.com", "password": "password123", "expected_role": "Employee", "expected_company": "TechCorp", "inactive": True}
]

base_url = "http://localhost:8000/api/auth"
results = []

for user in test_users:
    # Login
    login_payload = {"email": user["email"], "password": user["password"]}
    login_response = requests.post(f"{base_url}/login", json=login_payload)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data["access_token"]
        status = "Success"
        truncated_token = token[:20] + "..." if token else "N/A"
        
        # Get me
        me_headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{base_url}/me", headers=me_headers)
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            role = user_data.get("role", "Unknown")
            company = user_data.get("company", {}).get("name", "None") if user_data.get("company") else "None"
        else:
            role = "Error fetching profile"
            company = "N/A"
            status = "Login OK, Profile Fail"
    else:
        if user.get("inactive"):
            status = "Expected Fail (Inactive)"
            role = user["expected_role"]
            company = user["expected_company"]
            truncated_token = "N/A"
        else:
            status = "Fail"
            role = "N/A"
            company = "N/A"
            truncated_token = "N/A"
    
    results.append([
        user["email"],
        user["password"],
        role,
        company,
        status,
        truncated_token
    ])

# Print table
headers = ["Email", "Password", "Role", "Company", "Status", "Token (truncated)"]
print(tabulate(results, headers=headers, tablefmt="grid"))
