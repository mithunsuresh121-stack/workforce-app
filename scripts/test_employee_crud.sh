#!/bin/bash

# ===============================
# Employee Profiles CRUD Test Script
# ===============================

# 1. Login as SuperAdmin and get JWT token
echo "Logging in as SuperAdmin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
-H "Content-Type: application/json" \
-d '{"email":"admin@app.com","password":"supersecure123"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "Login failed. Exiting."
    exit 1
fi

echo "JWT token obtained successfully."
echo ""

# 2. GET all employees
echo "Fetching all employees..."
curl -s -X GET "http://localhost:8000/employees/" \
-H "Authorization: Bearer $TOKEN" | jq
echo ""

# 3. CREATE a new employee
echo "Creating a new employee..."
CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/employees/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "user_id": 31,
  "company_id": 1,
  "department": "Engineering",
  "position": "Engineer",
  "phone": "123-456-7890",
  "hire_date": "2025-09-01T00:00:00"
}')
echo "Create Response:"
echo $CREATE_RESPONSE | jq
NEW_EMPLOYEE_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo ""

# 4. GET the new employee by ID
echo "Fetching employee with ID $NEW_EMPLOYEE_ID..."
curl -s -X GET "http://localhost:8000/employees/$NEW_EMPLOYEE_ID" \
-H "Authorization: Bearer $TOKEN" | jq
echo ""

# 5. UPDATE the employee
echo "Updating employee with ID $NEW_EMPLOYEE_ID..."
curl -s -X PUT "http://localhost:8000/employees/$NEW_EMPLOYEE_ID" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "department": "Product",
  "position": "Product Manager",
  "phone": "987-654-3210"
}' | jq
echo ""

# 6. DELETE the employee
echo "Deleting employee with ID $NEW_EMPLOYEE_ID..."
curl -s -X DELETE "http://localhost:8000/employees/$NEW_EMPLOYEE_ID" \
-H "Authorization: Bearer $TOKEN" | jq
echo ""

echo "All Employee CRUD tests completed successfully."
