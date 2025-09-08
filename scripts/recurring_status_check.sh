#!/bin/bash
# recurring_status_check.sh
# Recurring status check for Workforce App
# Usage: ./recurring_status_check.sh
# Will repeat every X minutes as defined below

# --- CONFIG ---
INTERVAL_MINUTES=5   # Change to how often you want checks
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# Function to run the status check
run_status_check() {
  clear
  echo "🚀 Workforce App Status Check - $(date)"
  echo "----------------------------------"

  # --- Backend Checks ---
  echo "📌 Backend Features"
  python3 << 'EOF'
import requests

status = []

# Backend health check
try:
    r = requests.get("http://localhost:8000/health", timeout=3)
    if r.status_code == 200:
        status.append("[✔ Completed] Backend health check endpoint working")
    else:
        status.append(f"[❌ Missing/Broken] Backend health returned {r.status_code}")
except:
    status.append("[❌ Missing/Broken] Backend server not reachable at http://localhost:8000/health")

# Auth check
try:
    r = requests.post("http://localhost:8000/login",
                      json={"username":"admin@example.com","password":"password123"}, timeout=3)
    if r.status_code in (200, 401):
        status.append("[✔ Completed] Backend auth endpoint available")
    else:
        status.append(f"[❌ Missing/Broken] Auth endpoint returned {r.status_code}")
except:
    status.append("[❌ Missing/Broken] Backend auth endpoint not reachable")

for s in status: print(s)
EOF

  # --- Frontend Checks ---
  echo ""
  echo "📌 Frontend Features"
  FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" ${FRONTEND_URL}/health || echo "000")
  if [ "$FRONTEND_HEALTH" == "200" ]; then
    echo "[✔ Completed] Frontend health check endpoint working"
  else
    echo "[❌ Missing/Broken] Frontend not healthy (status $FRONTEND_HEALTH)"
  fi

  # --- Testing Coverage ---
  echo ""
  echo "📌 Testing Coverage"
  if [ -f "./frontend/web-app/tests/payroll-management.spec.ts" ]; then
    echo "[✔ Completed] Payroll Playwright tests present"
  else
    echo "[❌ Missing/Broken] Payroll Playwright tests not found"
  fi

  # --- Feature Roadmap ---
  echo ""
  echo "📌 Feature Roadmap"

  echo "### Core Features"
  echo "- [✔ Completed] Employee Profiles & Directory – basic details, job role, department, contact info."
  echo "- [✔ Completed] Shift Scheduling – create, assign, and manage shifts."
  echo "- [✔ Completed] Leave Management – vacation requests, sick leave, approvals."
  echo "- [⏳ Pending] Attendance Tracking – clock-in/clock/out, break times, overtime logging."
  echo "- [⏳ Pending] Task Assignment & Tracking – assign tasks, deadlines, and track progress."
  echo "- [⏳ Pending] Payroll Integration – auto-calculation of hours worked, overtime, bonuses."

  echo ""
  echo "### 📊 Management & Analytics"
  echo "- [⏳ Pending] Workforce Analytics Dashboard – productivity, absenteeism, labor costs."
  echo "- [⏳ Pending] Compliance & Labor Law Tracking – ensure legal shift limits, rest periods, etc."
  echo "- [⏳ Pending] Performance Reviews – feedback, ratings, KPIs tracking."

  echo ""
  echo "### 🔔 Communication & Engagement"
  echo "- [⏳ Pending] In-app Messaging/Notifications – shift changes, reminders, announcements."
  echo "- [⏳ Pending] Document Sharing – policies, training docs, certifications."
  echo "- [⏳ Pending] Employee Self-service Portal – employees can update profiles, request leave, swap shifts."

  echo ""
  echo "### 🛠 Advanced / Add-ons"
  echo "- [⏳ Pending] Geofencing for Attendance – confirm employees clock in at correct locations."
  echo "- [⏳ Pending] AI-powered Scheduling – auto-optimize shifts based on availability, skill set, labor laws."
  echo "- [⏳ Pending] Mobile App Support – iOS/Android for workers on the go."
  echo "- [⏳ Pending] Integration with HR/Payroll systems – e.g., Workday, ADP, SAP."
  echo "- [⏳ Pending] Multi-language & Multi-location support – if the company operates globally."

  echo ""
  echo "✅ Status check complete"
}

# --- Recurring Loop ---
while true; do
  run_status_check
  echo ""
  echo "⏳ Next check in $INTERVAL_MINUTES minutes..."
  sleep $((INTERVAL_MINUTES * 60))
done

# Usage:
# chmod +x recurring_status_check.sh
# ./recurring_status_check.sh
