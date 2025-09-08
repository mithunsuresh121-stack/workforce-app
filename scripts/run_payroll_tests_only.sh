#!/bin/bash
set -e

FRONTEND_DIR="/Users/mithunsuresh/Documents/workforce-app/frontend"
BACKEND_URL="http://localhost:8000/health"
TEST_USER_EMAIL="admin@example.com"
TEST_USER_PASSWORD="password123"

echo "🚀 Running Payroll Management tests (backend already running)..."

# Step 1: Verify backend is healthy
echo "⏳ Verifying backend health at $BACKEND_URL..."
if curl -s "$BACKEND_URL" | grep -q "healthy"; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend is not healthy. Please start the backend server first."
    exit 1
fi

# Step 2: Ensure test user exists
echo "👤 Checking/creating test user..."
python3 <<EOF
import requests
try:
    r = requests.post("http://localhost:8000/auth/login", json={"email": "$TEST_USER_EMAIL", "password": "$TEST_USER_PASSWORD"})
    if r.status_code == 200:
        print("✅ Test user already exists and can log in.")
    else:
        print("⚠️ Test user not found. Creating...")
        requests.post("http://localhost:8000/auth/register", json={"email": "$TEST_USER_EMAIL", "password": "$TEST_USER_PASSWORD"})
        print("✅ Test user created.")
except Exception as e:
    print("❌ Failed to check/create test user:", e)
    exit(1)
EOF

# Step 3: Run Playwright tests
echo "▶️ Running Payroll Management Playwright tests..."
cd "$FRONTEND_DIR"
npx playwright test --grep "Payroll Management" --headed

echo "🎉 Payroll Management test workflow completed!"
