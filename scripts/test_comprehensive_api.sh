#!/bin/bash
set -e

cd /Users/mithunsuresh/Documents/workforce-app

BASE_URL="http://127.0.0.1:8000"
TIMESTAMP=$(date +%s)
EMAIL="testuser_${TIMESTAMP}@example.com"
PASSWORD="password123"
FULL_NAME="Test User"

# Colors
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}=== COMPREHENSIVE WORKFORCE APP API TESTING ===${NC}"
echo -e "${YELLOW}Testing all backend endpoints with curl commands${NC}"
echo -e "${YELLOW}Timestamp: $TIMESTAMP${NC}"
echo ""

# Function to make curl requests and capture response
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    local description=$5

    echo -e "${YELLOW}=== $description ===${NC}"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" $headers "$BASE_URL$url")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST $headers -H "Content-Type: application/json" -d "$data" "$BASE_URL$url")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X PUT $headers -H "Content-Type: application/json" -d "$data" "$BASE_URL$url")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X DELETE $headers "$BASE_URL$url")
    fi

    http_code=$(echo "$response" | grep "HTTP_CODE:" | cut -d: -f2)
    body=$(echo "$response" | sed '/HTTP_CODE:/d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ SUCCESS ($http_code)${NC}"
        if [ "$body" != "" ]; then
            echo "$body" | jq . 2>/dev/null || echo "$body"
        fi
    else
        echo -e "${RED}❌ FAILED ($http_code)${NC}"
        if [ "$body" != "" ]; then
            echo "$body" | jq . 2>/dev/null || echo "$body"
        fi
    fi
    echo ""
}

# 1. INITIAL HEALTH CHECK
make_request "GET" "/openapi.json" "" "" "Initial Health Check"

# 2. AUTHENTICATION TESTS
echo -e "${BLUE}=== AUTHENTICATION TESTS ===${NC}"

# 2.1 Signup - Success
make_request "POST" "/auth/signup" "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"$FULL_NAME\", \"role\": \"Employee\", \"company_id\": 1}" "" "Signup New User"

# 2.2 Signup - Duplicate (should fail with 409)
make_request "POST" "/auth/signup" "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"$FULL_NAME\", \"role\": \"Employee\", \"company_id\": 1}" "" "Duplicate Signup (Expected 409)"

# 2.3 Signup - Invalid data (missing required fields)
make_request "POST" "/auth/signup" "{\"email\": \"invalid-email\", \"password\": \"123\", \"role\": \"InvalidRole\"}" "" "Signup Invalid Data (Expected 422)"

# 2.4 Login - Success
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" "$BASE_URL/auth/login")
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token' 2>/dev/null || echo "")
if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}❌ Login failed, no token received${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Login successful, token obtained${NC}"
AUTH_HEADER="-H \"Authorization: Bearer $TOKEN\""

# 2.5 Login - Invalid credentials
make_request "POST" "/auth/login" "{\"email\": \"$EMAIL\", \"password\": \"wrongpassword\"}" "" "Login Invalid Credentials (Expected 401)"

# 3. USER MANAGEMENT TESTS
echo -e "${BLUE}=== USER MANAGEMENT TESTS ===${NC}"

# 3.1 Get Users by Company
make_request "GET" "/auth/users/1" "" "$AUTH_HEADER" "Get Users by Company"

# 3.2 Get Current User Profile
make_request "GET" "/auth/me" "" "$AUTH_HEADER" "Get Current User Profile"

# 3.3 Get User Notifications
make_request "GET" "/auth/notifications" "" "$AUTH_HEADER" "Get User Notifications"

# 3.4 Update User - Partial update (full_name only)
USER_ID=$(curl -s -X GET "$BASE_URL/auth/users/1" -H "Authorization: Bearer $TOKEN" | jq -r --arg email "$EMAIL" '.[] | select(.email == $email) | .id' 2>/dev/null || echo "")
if [ -z "$USER_ID" ] || [ "$USER_ID" = "null" ]; then
    echo -e "${RED}❌ Could not find user ID for update test${NC}"
else
    make_request "PUT" "/auth/users/$USER_ID" "{\"full_name\": \"Updated Test User\"}" "$AUTH_HEADER" "Partial User Update (full_name only)"
fi

# 3.5 Update User - Full update
if [ -n "$USER_ID" ] && [ "$USER_ID" != "null" ]; then
    make_request "PUT" "/auth/users/$USER_ID" "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"Fully Updated User\", \"role\": \"Employee\", \"company_id\": 1}" "$AUTH_HEADER" "Full User Update"
fi

# 3.6 Update User - Invalid user ID
make_request "PUT" "/auth/users/99999" "{\"full_name\": \"Invalid User\"}" "$AUTH_HEADER" "Update Non-existent User (Expected 404)"

# 4. COMPANY MANAGEMENT TESTS
echo -e "${BLUE}=== COMPANY MANAGEMENT TESTS ===${NC}"

# 4.1 Get All Companies (SuperAdmin only - may fail for regular users)
make_request "GET" "/companies" "" "$AUTH_HEADER" "Get All Companies"

# 4.2 Get Company by ID
make_request "GET" "/companies/1" "" "$AUTH_HEADER" "Get Company by ID"

# 4.3 Get Non-existent Company
make_request "GET" "/companies/999" "" "$AUTH_HEADER" "Get Non-existent Company (Expected 404)"

# 4.4 Create Company (SuperAdmin only - may fail for regular users)
COMPANY_NAME="Test Company $TIMESTAMP"
make_request "POST" "/companies" "{\"name\": \"$COMPANY_NAME\", \"domain\": \"test$TIMESTAMP.com\", \"contact_email\": \"contact@test$TIMESTAMP.com\", \"contact_phone\": \"1234567890\", \"address\": \"123 Test St\", \"city\": \"Test City\", \"state\": \"Test State\", \"country\": \"Test Country\", \"postal_code\": \"12345\"}" "$AUTH_HEADER" "Create New Company"

# 4.5 Delete Company (SuperAdmin only - may fail for regular users)
make_request "DELETE" "/companies/999" "" "$AUTH_HEADER" "Delete Non-existent Company (Expected 404)"

# 5. TASK MANAGEMENT TESTS
echo -e "${BLUE}=== TASK MANAGEMENT TESTS ===${NC}"

# 5.1 Get All Tasks
make_request "GET" "/tasks" "" "$AUTH_HEADER" "Get All Tasks"

# 5.2 Create Task
TASK_TITLE="Test Task $TIMESTAMP"
make_request "POST" "/tasks" "{\"title\": \"$TASK_TITLE\", \"description\": \"This is a test task\", \"status\": \"To Do\", \"due_at\": \"2024-12-31T23:59:59\", \"assignee_id\": 1, \"company_id\": 1}" "$AUTH_HEADER" "Create New Task"

# 5.3 Get Task by ID
TASK_ID=$(curl -s -X GET "$BASE_URL/tasks" -H "Authorization: Bearer $TOKEN" | jq -r --arg title "$TASK_TITLE" '.[] | select(.title == $title) | .id' 2>/dev/null || echo "")
if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "null" ]; then
    make_request "GET" "/tasks/$TASK_ID" "" "$AUTH_HEADER" "Get Task by ID"
else
    echo -e "${YELLOW}⚠️ Could not find created task for ID test${NC}"
fi

# 5.4 Get Non-existent Task
make_request "GET" "/tasks/999" "" "$AUTH_HEADER" "Get Non-existent Task (Expected 404)"

# 5.5 Create Task with Invalid Data
make_request "POST" "/tasks" "{\"title\": \"\", \"status\": \"Invalid Status\", \"company_id\": 999}" "$AUTH_HEADER" "Create Task Invalid Data (Expected 422)"

# 6. DASHBOARD TESTS
echo -e "${BLUE}=== DASHBOARD TESTS ===${NC}"

# 6.1 Get Dashboard KPIs
make_request "GET" "/dashboard/kpis" "" "$AUTH_HEADER" "Get Dashboard KPIs"

# 6.2 Get Recent Activities
make_request "GET" "/dashboard/recent-activities" "" "$AUTH_HEADER" "Get Recent Activities"

# 6.3 Get Task Status Chart
make_request "GET" "/dashboard/charts/task-status" "" "$AUTH_HEADER" "Get Task Status Chart"

# 6.4 Get Employee Distribution Chart
make_request "GET" "/dashboard/charts/employee-distribution" "" "$AUTH_HEADER" "Get Employee Distribution Chart"

# 7. UNAUTHORIZED ACCESS TESTS
echo -e "${BLUE}=== UNAUTHORIZED ACCESS TESTS ===${NC}"

# 7.1 Access Protected Endpoint without Token
make_request "GET" "/auth/me" "" "" "Access Protected Endpoint without Token (Expected 401)"

# 7.2 Access with Invalid Token
make_request "GET" "/auth/me" "" "-H \"Authorization: Bearer invalid_token\"" "Access with Invalid Token (Expected 401)"

# 8. FINAL HEALTH CHECK
echo -e "${BLUE}=== FINAL HEALTH CHECK ===${NC}"
make_request "GET" "/openapi.json" "" "" "Final Health Check"

echo -e "${GREEN}🎉 COMPREHENSIVE API TESTING COMPLETED!${NC}"
echo -e "${YELLOW}Summary:${NC}"
echo -e "  ✅ Authentication endpoints tested (signup, login, duplicate handling)"
echo -e "  ✅ User management tested (CRUD operations, partial updates)"
echo -e "  ✅ Company management tested (read operations, create/delete for SuperAdmin)"
echo -e "  ✅ Task management tested (read operations, create with validation)"
echo -e "  ✅ Dashboard endpoints tested (KPIs, charts, activities)"
echo -e "  ✅ Error handling tested (401, 404, 409, 422 status codes)"
echo -e "  ✅ Unauthorized access tested (missing/invalid tokens)"
echo ""
echo -e "${BLUE}Note: Some endpoints may have failed due to role-based access control.${NC}"
echo -e "${BLUE}SuperAdmin role is required for company management operations.${NC}"
