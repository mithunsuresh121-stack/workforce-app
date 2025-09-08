#!/bin/bash

# Edge cases and error handling test script for Employee endpoints
# Tests invalid inputs, expired tokens, unauthorized access, etc.

API_URL="http://localhost:8000"

# Login as SuperAdmin to get valid token
echo "Logging in as SuperAdmin..."
SUPERADMIN_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@example.com","password":"password123"}' | jq -r '.access_token')

if [ "$SUPERADMIN_TOKEN" == "null" ] || [ -z "$SUPERADMIN_TOKEN" ]; then
  echo "Login failed. Exiting."
  exit 1
fi
echo "Login successful."

echo
echo "=== Testing Edge Cases and Error Handling ==="

# Test 1: Invalid JSON payload
echo "1. Testing invalid JSON payload..."
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invalid": "json", "missing": "fields"}' | jq '.'

# Test 2: Missing required fields
echo "2. Testing missing required fields..."
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"department": "Engineering"}' | jq '.'

# Test 3: Invalid user_id (non-existent user)
echo "3. Testing invalid user_id..."
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 99999, "company_id": 1, "department": "Engineering", "position": "Engineer", "hire_date": "2023-01-01T00:00:00"}' | jq '.'

# Test 4: Invalid company_id
echo "4. Testing invalid company_id..."
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 30, "company_id": 999, "department": "Engineering", "position": "Engineer", "hire_date": "2023-01-01T00:00:00"}' | jq '.'

# Test 5: Invalid date format
echo "5. Testing invalid date format..."
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 30, "company_id": 1, "department": "Engineering", "position": "Engineer", "hire_date": "invalid-date"}' | jq '.'

# Test 6: Duplicate employee profile
echo "6. Testing duplicate employee profile..."
# First create a profile
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 30, "company_id": 1, "department": "Engineering", "position": "Engineer", "hire_date": "2023-01-01T00:00:00"}' > /dev/null

# Try to create again
curl -s -X POST "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 30, "company_id": 1, "department": "Engineering", "position": "Engineer", "hire_date": "2023-01-01T00:00:00"}' | jq '.'

# Test 7: Invalid JWT token
echo "7. Testing invalid JWT token..."
curl -s -X GET "$API_URL/employees/" \
  -H "Authorization: Bearer invalid.token.here" | jq '.'

# Test 8: Expired JWT token (using an old token)
echo "8. Testing expired JWT token..."
EXPIRED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcmFkbWluQGV4YW1wbGUuY29tIiwiY29tcGFueV9pZCI6MSwicm9sZSI6IlN1cGVyQWRtaW4iLCJleHAiOjE2MDAwMDAwMDB9.invalid"
curl -s -X GET "$API_URL/employees/" \
  -H "Authorization: Bearer $EXPIRED_TOKEN" | jq '.'

# Test 9: No authorization header
echo "9. Testing no authorization header..."
curl -s -X GET "$API_URL/employees/" | jq '.'

# Test 10: Wrong HTTP method
echo "10. Testing wrong HTTP method..."
curl -s -X PATCH "$API_URL/employees/" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 30, "company_id": 1}' | jq '.'

# Test 11: Invalid user_id in GET request
echo "11. Testing invalid user_id in GET request..."
curl -s -X GET "$API_URL/employees/99999" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq '.'

# Test 12: Invalid user_id in PUT request
echo "12. Testing invalid user_id in PUT request..."
curl -s -X PUT "$API_URL/employees/99999" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"department": "Updated"}' | jq '.'

# Test 13: Invalid user_id in DELETE request
echo "13. Testing invalid user_id in DELETE request..."
curl -s -X DELETE "$API_URL/employees/99999" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" | jq '.'

echo
echo "Edge cases and error handling tests completed."
