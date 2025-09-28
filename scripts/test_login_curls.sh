#!/bin/bash

# Script to test login for seeded users via curl
# Prints table: Email | Password | Role | Company | Status | Token (truncated)

echo "Email | Password | Role | Company | Status | Token (truncated)"
echo "----- | -------- | ---- | ------- | ------ | ----------------"

# SuperAdmin
echo -n "superadmin@workforce.com | password123 | SuperAdmin | None | "
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@workforce.com","password":"password123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ]; then
  TOKEN=$(echo "$BODY" | jq -r '.access_token' | cut -c1-20)"..."
  ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:8000/api/auth/me \
    -H "Authorization: Bearer $(echo "$BODY" | jq -r '.access_token')" \
    -H "Content-Type: application/json")
  ME_HTTP_CODE=$(echo "$ME_RESPONSE" | tail -n1)
  ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')
  if [ "$ME_HTTP_CODE" = "200" ]; then
    ROLE=$(echo "$ME_BODY" | jq -r '.role')
    COMPANY=$(echo "$ME_BODY" | jq -r '.company // empty')
    echo "Success | $ROLE | $COMPANY | $TOKEN"
  else
    echo "Fail (/me: $ME_HTTP_CODE) | SuperAdmin | None | -"
  fi
else
  echo "Fail ($HTTP_CODE) | SuperAdmin | None | -"
fi

# CompanyAdmin TechCorp
echo -n "admin1@techcorp.com | password123 | CompanyAdmin | TechCorp | "
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin1@techcorp.com","password":"password123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ]; then
  TOKEN=$(echo "$BODY" | jq -r '.access_token' | cut -c1-20)"..."
  ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:8000/api/auth/me \
    -H "Authorization: Bearer $(echo "$BODY" | jq -r '.access_token')" \
    -H "Content-Type: application/json")
  ME_HTTP_CODE=$(echo "$ME_RESPONSE" | tail -n1)
  ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')
  if [ "$ME_HTTP_CODE" = "200" ]; then
    ROLE=$(echo "$ME_BODY" | jq -r '.role')
    COMPANY=$(echo "$ME_BODY" | jq -r '.company.name // empty')
    echo "Success | $ROLE | $COMPANY | $TOKEN"
  else
    echo "Fail (/me: $ME_HTTP_CODE) | CompanyAdmin | TechCorp | -"
  fi
else
  echo "Fail ($HTTP_CODE) | CompanyAdmin | TechCorp | -"
fi

# CompanyAdmin InnoCorp
echo -n "admin2@innocorp.com | password123 | CompanyAdmin | InnoCorp | "
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin2@innocorp.com","password":"password123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ]; then
  TOKEN=$(echo "$BODY" | jq -r '.access_token' | cut -c1-20)"..."
  ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:8000/api/auth/me \
    -H "Authorization: Bearer $(echo "$BODY" | jq -r '.access_token')" \
    -H "Content-Type: application/json")
  ME_HTTP_CODE=$(echo "$ME_RESPONSE" | tail -n1)
  ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')
  if [ "$ME_HTTP_CODE" = "200" ]; then
    ROLE=$(echo "$ME_BODY" | jq -r '.role')
    COMPANY=$(echo "$ME_BODY" | jq -r '.company.name // empty')
    echo "Success | $ROLE | $COMPANY | $TOKEN"
  else
    echo "Fail (/me: $ME_HTTP_CODE) | CompanyAdmin | InnoCorp | -"
  fi
else
  echo "Fail ($HTTP_CODE) | CompanyAdmin | InnoCorp | -"
fi

# Employee TechCorp
echo -n "emp1@techcorp.com | password123 | Employee | TechCorp | "
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"emp1@techcorp.com","password":"password123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ]; then
  TOKEN=$(echo "$BODY" | jq -r '.access_token' | cut -c1-20)"..."
  ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET http://localhost:8000/api/auth/me \
    -H "Authorization: Bearer $(echo "$BODY" | jq -r '.access_token')" \
    -H "Content-Type: application/json")
  ME_HTTP_CODE=$(echo "$ME_RESPONSE" | tail -n1)
  ME_BODY=$(echo "$ME_RESPONSE" | sed '$d')
  if [ "$ME_HTTP_CODE" = "200" ]; then
    ROLE=$(echo "$ME_BODY" | jq -r '.role')
    COMPANY=$(echo "$ME_BODY" | jq -r '.company.name // empty')
    echo "Success | $ROLE | $COMPANY | $TOKEN"
  else
    echo "Fail (/me: $ME_HTTP_CODE) | Employee | TechCorp | -"
  fi
else
  echo "Fail ($HTTP_CODE) | Employee | TechCorp | -"
fi

# Inactive Employee TechCorp
echo -n "emp5@techcorp.com | password123 | Employee | TechCorp | "
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"emp5@techcorp.com","password":"password123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "401" ]; then
  echo "Fail (Inactive) | Employee | TechCorp | -"
else
  echo "Unexpected ($HTTP_CODE) | Employee | TechCorp | -"
fi
