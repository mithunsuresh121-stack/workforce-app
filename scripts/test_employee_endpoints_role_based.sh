#!/bin/bash

# Automated role-based access testing script for Employee endpoints in FastAPI Workforce App
# Usage: ./test_employee_endpoints_role_based.sh
# Modify the EMAIL and PASSWORD variables below to test different users

API_URL="http://localhost:8000"

# User credentials - modify these to match your test users
SUPERADMIN_EMAIL="superadmin@example.com"
SUPERADMIN_PASSWORD="password123"

MANAGER_EMAIL="manager@example.com"
MANAGER_PASSWORD="password123"

EMPLOYEE_EMAIL="employee@example.com"
EMPLOYEE_PASSWORD="password123"

# Function to login and get JWT token
login() {
  local email=$1
  local password=$2
  echo "Logging in as $email..."
  token=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$email\",\"password\":\"$password\"}" | jq -r '.access_token')
  if [ "$token" == "null" ] || [ -z "$token" ]; then
    echo "Login failed for $email"
    exit 1
  fi
  echo "Login successful for $email"
  echo
  echo "$token"
}

# Login all users and store tokens
SUPERADMIN_TOKEN=$(login "$SUPERADMIN_EMAIL" "$SUPERADMIN_PASSWORD")
MANAGER_TOKEN=$(login "$MANAGER_EMAIL" "$MANAGER_PASSWORD")
EMPLOYEE_TOKEN=$(login "$EMPLOYEE_EMAIL" "$EMPLOYEE_PASSWORD")

# Example JSON payloads for POST and PUT requests
CREATE_PAYLOAD='{
  "user_id": 30,
  "company_id": 1,
  "department": "Engineering",
  "position": "Software Engineer",
  "phone": "123-456-7890",
  "hire_date": "2023-01-15T00:00:00",
  "manager_id": null
}'

UPDATE_PAYLOAD='{
  "department": "Product",
  "position": "Senior Engineer",
  "phone": "987-654-3210",
  "hire_date": "2023-01-15T00:00:00",
  "manager_id": null,
  "is_active": true
}'

# Helper function to perform API requests
api_request() {
  local method=$1
  local endpoint=$2
  local token=$3
  local data=$4

  if [ "$method" == "GET" ] || [ "$method" == "DELETE" ]; then
    curl -s -X $method "$API_URL$endpoint" \
      -H "Authorization: Bearer $token" \
      -H "Content-Type: application/json"
  else
    curl -s -X $method "$API_URL$endpoint" \
      -H "Authorization: Bearer $token" \
      -H "Content-Type: application/json" \
      -d "$data"
  fi
  echo
}

# Test function for a role
test_role() {
  local role_name=$1
  local token=$2
  local user_id=30  # Change as needed for testing specific user profiles

  echo "=== Testing as $role_name ==="

  echo "1. GET /employees/ - List employee profiles"
  echo "Expected: Allowed for SuperAdmin and Manager, Denied or limited for Employee"
  api_request GET "/employees/" "$token"

  echo "2. POST /employees/ - Create employee profile"
  echo "Expected: Allowed for SuperAdmin, Restricted for Manager and Employee"
  api_request POST "/employees/" "$token" "$CREATE_PAYLOAD"

  echo "3. GET /employees/{user_id} - Get employee profile"
  echo "Expected: Allowed for SuperAdmin and Manager for any user, Employee only for own profile"
  api_request GET "/employees/$user_id" "$token"

  echo "4. PUT /employees/{user_id} - Update employee profile"
  echo "Expected: Allowed for SuperAdmin and Manager for any user, Employee only for own profile"
  api_request PUT "/employees/$user_id" "$token" "$UPDATE_PAYLOAD"

  echo "5. DELETE /employees/{user_id} - Delete employee profile"
  echo "Expected: Allowed for SuperAdmin, Restricted for Manager and Employee"
  api_request DELETE "/employees/$user_id" "$token"

  echo
}

# Run tests for each role
test_role "SuperAdmin" "$SUPERADMIN_TOKEN"
test_role "Manager" "$MANAGER_TOKEN"
test_role "Employee" "$EMPLOYEE_TOKEN"

echo "Role-based access tests completed."

# Instructions:
# - Modify the EMAIL and PASSWORD variables at the top to test different users.
# - Responses with HTTP 403 indicate access denied as expected for restricted actions.
# - Review the JSON responses printed for success or error messages.
# - Ensure jq is installed for JSON parsing: brew install jq (macOS) or sudo apt-get install jq (Linux).
