#!/bin/bash
# 1️⃣ Activate backend virtual environment
source /Users/mithunsuresh/Documents/workforce-app/backend/venv/bin/activate

# Install dependencies if not installed
pip install -r requirements.txt

# 2️⃣ Start FastAPI backend in background
echo "Starting FastAPI backend..."
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# 3️⃣ Wait for backend to be ready
echo "Waiting for backend to start..."
until curl -s http://127.0.0.1:8000/docs >/dev/null 2>&1; do
  sleep 1
done
echo "Backend is up!"

# 4️⃣ Seed test users if not present
echo "Seeding test users..."
python backend/seed_data.py

# 5️⃣ Verify /api/auth/me with SuperAdmin login
echo "Verifying /api/auth/me..."
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@workforce.com","password":"password123"}' | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token. Check backend login setup."
  kill $BACKEND_PID
  exit 1
fi

curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/auth/me | jq

# 6️⃣ Launch frontend
echo "Launching React frontend..."
cd frontend-web/web-app && source ~/.nvm/nvm.sh && nvm install && nvm use && npm start
