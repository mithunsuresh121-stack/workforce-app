#!/bin/bash
set -e

echo "🚀 Starting Payroll Management test workflow..."

# Function for progress logging
step() {
  local status=$1
  local msg=$2
  if [ "$status" = "done" ]; then
    echo "[✔ Completed] $msg"
  else
    echo "[⏳ Pending] $msg"
  fi
}

# Start backend
step pending "Starting backend..."
( cd ../backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 & )
BACKEND_PID=$!
sleep 5
step done "Backend process launched (PID $BACKEND_PID)"

# Wait for backend health
echo "Waiting for backend health..."
for i in {1..20}; do
  if curl -s http://localhost:8000/health | grep -q "ok"; then
    step done "Backend is healthy"
    break
  fi
  sleep 3
done

# Start frontend
step pending "Starting frontend..."
( cd ../frontend/web-app && npm run start & )
FRONTEND_PID=$!
sleep 10
step done "Frontend process launched (PID $FRONTEND_PID)"

# Wait for frontend health
echo "Waiting for frontend health..."
for i in {1..20}; do
  if curl -s http://localhost:3000/health | grep -q "ok"; then
    step done "Frontend is healthy"
    break
  fi
  sleep 3
done

# Run Playwright tests (Brave only)
step pending "Running Payroll Management tests in Brave..."
cd frontend/web-app
npx playwright test --project=Brave --reporter=html
step done "Tests finished running"

# Show HTML report
npx playwright show-report
step done "Report opened"

# Cleanup
kill $BACKEND_PID $FRONTEND_PID || true
echo "🛑 Backend and frontend stopped. Workflow complete."
