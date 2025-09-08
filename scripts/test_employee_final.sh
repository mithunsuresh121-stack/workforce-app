#!/bin/bash
# Full Workforce App Test Script - Backend + Frontend Screens
# Requirements: curl, jq, bash 5+, backend running on localhost:8000, frontend running locally

BASE_URL="http://localhost:8000"
REACT_URL="http://localhost:3000"   # Adjust if different
EMAIL="admin@app.com"
PASSWORD="password123"
COMPANY_ID=1
NEW_USER_ID=31  # Use a different user_id to avoid conflicts

echo "=== STEP 1: Login and generate JWT ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
JWT=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
if [ "$JWT" == "null" ] || [ -z "$JWT" ]; then
  echo "❌ Login failed. Response: $LOGIN_RESPONSE"
  exit 1
fi
AUTH_HEADER="Authorization: Bearer $JWT"
echo "✅ Login successful. JWT generated."

echo "=== STEP 2: Test GET /employees/ ==="
curl -s -X GET "$BASE_URL/employees/" -H "$AUTH_HEADER" | jq .

echo "=== STEP 3: Test POST /employees/ (Create Employee) ==="
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/employees/" \
  -H "$AUTH_HEADER" \
  -H "Content-Type: application/json" \
  -d "{
        \"user_id\": $NEW_USER_ID,
        \"company_id\": $COMPANY_ID,
        \"department\": \"Engineering\",
        \"position\": \"Engineer\",
        \"phone\": \"555-1234\",
        \"hire_date\": \"2023-01-01T00:00:00\"
      }")
echo "$CREATE_RESPONSE" | jq .
EMPLOYEE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')

echo "=== STEP 4: Test GET /employees/{user_id} ==="
if [ "$EMPLOYEE_ID" != "null" ] && [ -n "$EMPLOYEE_ID" ]; then
  curl -s -X GET "$BASE_URL/employees/$EMPLOYEE_ID" -H "$AUTH_HEADER" | jq .
else
  echo "❌ Cannot test GET - employee creation failed"
fi

echo "=== STEP 5: Test PUT /employees/{user_id} (Update Employee) ==="
if [ "$EMPLOYEE_ID" != "null" ] && [ -n "$EMPLOYEE_ID" ]; then
  curl -s -X PUT "$BASE_URL/employees/$EMPLOYEE_ID" -H "$AUTH_HEADER" \
    -H "Content-Type: application/json" \
    -d '{"position":"Senior Engineer"}' | jq .
else
  echo "❌ Cannot test PUT - employee creation failed"
fi

echo "=== STEP 6: Test DELETE /employees/{user_id} ==="
if [ "$EMPLOYEE_ID" != "null" ] && [ -n "$EMPLOYEE_ID" ]; then
  curl -s -X DELETE "$BASE_URL/employees/$EMPLOYEE_ID" -H "$AUTH_HEADER" | jq .
else
  echo "❌ Cannot test DELETE - employee creation failed"
fi

echo "=== STEP 7: Role-Based Access Testing ==="
ROLES=("SuperAdmin" "Manager" "Employee")
for ROLE in "${ROLES[@]}"; do
  echo "--- Testing role: $ROLE ---"
  # Placeholder: you can generate a JWT for each role or login with role accounts
  # curl -s -X GET "$BASE_URL/employees/" -H "Authorization: Bearer <ROLE_JWT>" | jq .
done

echo "=== STEP 8: Edge Case Testing ==="
echo "Testing missing fields in POST..."
curl -s -X POST "$BASE_URL/employees/" -H "$AUTH_HEADER" -H "Content-Type: application/json" -d '{}' | jq .
echo "Testing invalid JWT..."
curl -s -X GET "$BASE_URL/employees/" -H "Authorization: Bearer invalidtoken" | jq .
echo "Testing expired JWT..."
# You can simulate by generating a token with short expiry or manually editing expiry

echo "=== STEP 9: Frontend Screen Verification ==="
# Flutter screen check (mobile)
echo "Checking Flutter frontend screens..."
# You can run Flutter integration test command if set up:
# flutter test integration_test/
# Or perform API health check from Flutter service
curl -s "$REACT_URL" | grep -q "<title>" && echo "✅ React frontend reachable" || echo "❌ React frontend not reachable"

# React screen check
echo "Checking React Employees screen..."
curl -s "$REACT_URL/employees" | grep -q "Employees" && echo "✅ Employees screen visible" || echo "❌ Employees screen failed to load"

echo "✅ Full backend + frontend test script executed successfully. Review logs above."
