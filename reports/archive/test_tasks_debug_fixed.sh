#!/bin/bash

# Step 1: Activate virtual environment and cd to backend
echo "Activating backend virtual environment..."
cd /Users/mithunsuresh/Documents/workforce-app/backend
source venv/bin/activate

# Step 2: Verify admin user exists
echo "Checking admin user in database..."
python - <<END
import sys
sys.path.append('.')
from app.db import engine
from sqlalchemy import text

result = engine.execute(text("SELECT id, email, role, company_id FROM users WHERE email='admin@app.com';"))
found = False
for row in result:
    found = True
    print(f"ID: {row[0]}, Email: {row[1]}, Role: {row[2]}, Company: {row[3]}")
if not found:
    print("Admin user not found. Please create admin@app.com in DB.")
END

# Step 3: Generate fresh JWT token
echo "Generating new JWT token..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
-H "Content-Type: application/json" \
-d '{"email":"admin@app.com","password":"admin123"}')

echo "Login response: $RESPONSE"

TOKEN=$(echo $RESPONSE | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "Failed to generate token. Check login credentials."
    exit 1
fi
echo "Token generated successfully"

# Step 4: Test /tasks/ endpoint
echo "Testing /tasks/ endpoint..."
curl -s -X GET "http://localhost:8000/tasks/" -H "Authorization: Bearer $TOKEN" | python -m json.tool
