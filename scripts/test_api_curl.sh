#!/bin/bash

# This script tests all relevant API endpoints of the FastAPI workforce management app
# It logs in as a SuperAdmin user, stores the JWT token, and uses it for subsequent requests

# Set API base URL
API_URL="http://localhost:8000"

# Login credentials for SuperAdmin user
EMAIL="superadmin@example.com"
PASSWORD="password123"

echo "Logging in as SuperAdmin user..."
# Login and extract JWT token
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "Login failed. Exiting."
  exit 1
fi

echo "Login successful. JWT token obtained."

# Common header with Authorization
AUTH_HEADER="Authorization: Bearer $TOKEN"

echo
echo "Testing GET /employees/ endpoint..."
curl -s -X GET "$API_URL/employees/" -H "$AUTH_HEADER" | jq

echo
echo "Testing POST /employees/ endpoint..."
CREATE_PAYLOAD='{
  "user_id": 30,
  "company_id": 1,
  "department": "Engineering",
  "position": "Software Engineer",
  "phone": "123-456-7890",
  "hire_date": "2023-01-15T00:00:00",
  "manager_id": null
}'
curl -s -X POST "$API_URL/employees/" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d "$CREATE_PAYLOAD" | jq

echo
echo "Testing GET /employees/{user_id} endpoint..."
USER_ID=10
curl -s -X GET "$API_URL/employees/$USER_ID" -H "$AUTH_HEADER" | jq

echo
echo "Testing PUT /employees/{user_id} endpoint..."
UPDATE_PAYLOAD='{
  "department": "Product",
  "position": "Senior Software Engineer",
  "phone": "987-654-3210",
  "hire_date": "2023-01-15T00:00:00",
  "manager_id": null
}'
curl -s -X PUT "$API_URL/employees/$USER_ID" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d "$UPDATE_PAYLOAD" | jq

echo
echo "Testing DELETE /employees/{user_id} endpoint..."
curl -s -X DELETE "$API_URL/employees/$USER_ID" -H "$AUTH_HEADER" | jq

echo
echo "All API endpoint tests completed."
