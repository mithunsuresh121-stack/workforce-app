#!/bin/bash
set -e

echo "🚀 Starting full Payroll Management testing workflow..."

# --- Step 1: Ensure we are in project root ---
PROJECT_ROOT="$(pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend/web-app"

if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ Project structure not found (backend/frontend missing)"
  exit 1
fi

echo "✅ Project structure verified"

# --- Step 2: Kill anything already on port 8000 or 3001 ---
echo "⚠️ Killing processes on ports 8000 and 3001 if any..."
lsof -ti:8000 | xargs kill -9 || true
lsof -ti:3001 | xargs kill -9 || true

# --- Step 3: Start backend server ---
echo "⏳ Starting backend server..."
cd "$BACKEND_DIR"
source venv/bin/activate
nohup uvicorn app.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# --- Step 4: Wait for backend health ---
echo "⏳ Waiting for backend health at http://localhost:8000/health..."
for i in {1..20}; do
  if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ Backend is healthy"
    break
  fi
  sleep 3
done

if ! curl -s http://localhost:8000/health | grep -q "ok"; then
  echo "❌ Backend failed to start"
  kill -9 $BACKEND_PID || true
  exit 1
fi

# --- Step 5: Seed test data ---
echo "📦 Seeding test user and employee data..."
cd "$BACKEND_DIR"
python3 seed_test_data.py

# --- Step 6: Patch Playwright config ---
echo "🛠️ Patching Playwright config (disable Safari mobile tests)..."
cd "$FRONTEND_DIR"
# Config is already updated, no need to patch

# --- Step 7: Install Playwright + dependencies ---
echo "📦 Installing Playwright dependencies..."
npm install

# --- Step 8: Run Payroll tests ---
echo "✅ Running Payroll Management Playwright tests..."
npx playwright test tests/payroll-management.spec.ts --headed

TEST_RESULT=$?

# --- Step 9: Cleanup ---
echo "🧹 Cleaning up..."
kill -9 $BACKEND_PID || true

if [ $TEST_RESULT -eq 0 ]; then
  echo "🎉 All Payroll Management tests passed successfully!"
else
  echo "❌ Some tests failed. Check Playwright report."
fi
