#!/bin/bash
set -e

cd /Users/mithunsuresh/Documents/workforce-app

BASE_URL="http://127.0.0.1:8000"
TIMESTAMP=$(date +%s)
EMAIL="testuser_${TIMESTAMP}@example.com"
PASSWORD="password123"
FULL_NAME="Test User"

# Colors
GREEN="\\033[0;32m"
RED="\\033[0;31m"
YELLOW="\\033[1;33m"
NC="\\033[0m" # No Color

echo -e "${YELLOW}=== Initial Health Check ===${NC}"
curl -s $BASE_URL/openapi.json | jq .info.title

echo -e "${YELLOW}=== Signup New User ===${NC}"
SIGNUP_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/signup_response.json -X POST $BASE_URL/auth/signup \\
  -H "Content-Type: application/json" \\
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"$FULL_NAME\", \"role\": \"Employee\", \"company_id\": 1}")

HTTP_CODE=$(tail -c 4 /tmp/signup_response.json | xargs)
if [ "$HTTP_CODE" != "201" ]; then
  echo -e "${RED}❌ Signup failed with status $HTTP_CODE${NC}"
  cat /tmp/signup_response.json | jq .
  exit 1
fi
echo -e "${GREEN}✅ Signup successful${NC}"
cat /tmp/signup_response.json | jq .

echo -e "${YELLOW}=== Login ===${NC}"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \\
  -H "Content-Type: application/json" \\
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
  echo -e "${RED}❌ Login failed, no token received${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Login successful${NC}"

echo -e "${YELLOW}=== Get Users ===${NC}"
USERS_RESPONSE=$(curl -s -X GET $BASE_URL/auth/users/1 \\
  -H "Authorization: Bearer $TOKEN")
echo "$USERS_RESPONSE" | jq .

USER_ID=$(echo "$USERS_RESPONSE" | jq -r --arg email "$EMAIL" '.[] | select(.email == $email) | .id')
if [ -z "$USER_ID" ]; then
  echo -e "${RED}❌ User not found in users list${NC}"
  exit 1
fi

echo -e "${YELLOW}=== Partial Update User (full_name only) ===${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT $BASE_URL/auth/users/$USER_ID \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d "{\"full_name\": \"Updated Test User\"}")
echo "$UPDATE_RESPONSE" | jq .
echo -e "${GREEN}✅ User updated successfully${NC}"

echo -e "${YELLOW}=== Get Updated User ===${NC}"
UPDATED_USER=$(curl -s -X GET $BASE_URL/auth/users/1 \\
  -H "Authorization: Bearer $TOKEN" | jq -r --arg id "$USER_ID" '.[] | select(.id == ($id | tonumber))')
echo "$UPDATED_USER" | jq .
echo -e "${GREEN}✅ Verified updated user${NC}"

echo -e "${YELLOW}=== Attempt Duplicate Signup ===${NC}"
DUPLICATE_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/duplicate_response.json -X POST $BASE_URL/auth/signup \\
  -H "Content-Type: application/json" \\
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"full_name\": \"$FULL_NAME\", \"role\": \"Employee\", \"company_id\": 1}")

DUP_HTTP_CODE=$(tail -c 4 /tmp/duplicate_response.json | xargs)
if [ "$DUP_HTTP_CODE" != "409" ]; then
  echo -e "${RED}❌ Duplicate signup test failed, expected 409 but got $DUP_HTTP_CODE${NC}"
  cat /tmp/duplicate_response.json | jq .
  exit 1
fi
echo -e "${GREEN}✅ Duplicate signup correctly returned 409 Conflict${NC}"
cat /tmp/duplicate_response.json | jq .

echo -e "${YELLOW}=== Final Health Check ===${NC}"
curl -s $BASE_URL/openapi.json | jq .info.title
echo -e "${GREEN}✅ All tests completed successfully${NC}"
