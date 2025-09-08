#!/bin/bash

# This script tests the new Leave and Shift API endpoints
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
echo "=== TESTING LEAVE ENDPOINTS ==="

echo
echo "Testing GET /leaves/ endpoint..."
curl -s -X GET "$API_URL/leaves/" -H "$AUTH_HEADER" | jq

echo
echo "Testing POST /leaves/ endpoint (create leave request)..."
CREATE_LEAVE_PAYLOAD='{
  "tenant_id": "1",
  "employee_id": 1,
  "type": "Vacation",
  "start_at": "2024-02-01T09:00:00",
  "end_at": "2024-02-05T17:00:00",
  "status": "Pending"
}'
curl -s -X POST "$API_URL/leaves/" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d "$CREATE_LEAVE_PAYLOAD" | jq

echo
echo "Testing GET /leaves/my-leaves/ endpoint..."
curl -s -X GET "$API_URL/leaves/my-leaves/" -H "$AUTH_HEADER" | jq

echo
echo "Testing PUT /leaves/{leave_id}/status endpoint (approve leave)..."
# First get a leave ID from the list
LEAVE_ID=$(curl -s -X GET "$API_URL/leaves/" -H "$AUTH_HEADER" | jq -r '.[0].id' 2>/dev/null || echo "1")
if [ "$LEAVE_ID" != "null" ] && [ -n "$LEAVE_ID" ]; then
  curl -s -X PUT "$API_URL/leaves/$LEAVE_ID/status" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d '"Approved"' | jq
else
  echo "No leave found to update status"
fi

echo
echo "=== TESTING SHIFT ENDPOINTS ==="

echo
echo "Testing GET /shifts/ endpoint..."
curl -s -X GET "$API_URL/shifts/" -H "$AUTH_HEADER" | jq

echo
echo "Testing POST /shifts/ endpoint (create shift)..."
CREATE_SHIFT_PAYLOAD='{
  "tenant_id": "1",
  "employee_id": 1,
  "start_at": "2024-01-15T09:00:00",
  "end_at": "2024-01-15T17:00:00",
  "location": "Office"
}'
curl -s -X POST "$API_URL/shifts/" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d "$CREATE_SHIFT_PAYLOAD" | jq

echo
echo "Testing GET /shifts/my-shifts/ endpoint..."
curl -s -X GET "$API_URL/shifts/my-shifts/" -H "$AUTH_HEADER" | jq

echo
echo "Testing PUT /shifts/{shift_id} endpoint (update shift)..."
# First get a shift ID from the list
SHIFT_ID=$(curl -s -X GET "$API_URL/shifts/" -H "$AUTH_HEADER" | jq -r '.[0].id' 2>/dev/null || echo "1")
if [ "$SHIFT_ID" != "null" ] && [ -n "$SHIFT_ID" ]; then
  UPDATE_SHIFT_PAYLOAD='{
    "tenant_id": "1",
    "employee_id": 1,
    "start_at": "2024-01-15T08:00:00",
    "end_at": "2024-01-15T16:00:00",
    "location": "Remote"
  }'
  curl -s -X PUT "$API_URL/shifts/$SHIFT_ID" -H "Content-Type: application/json" -H "$AUTH_HEADER" -d "$UPDATE_SHIFT_PAYLOAD" | jq
else
  echo "No shift found to update"
fi

echo
echo "All Leave and Shift API endpoint tests completed."
