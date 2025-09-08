#!/bin/bash
# check_app_status.sh
# Recurring status check for Workforce App

echo "🚀 Workforce App Status Check"
echo "----------------------------------"

# === Backend Features ===
echo "📌 Backend Features"
python3 << 'EOF'
import requests

status = []

# 1. Health check
try:
    r = requests.get("http://localhost:8000/health", timeout=3)
    if r.status_code == 200:
        status.append("[✔ Completed] Backend health check endpoint working")
    else:
        status.append(f"[❌ Missing/Broken] Backend health check returned {r.status_code}")
except:
    status.append("[❌ Missing/Broken] Backend server not reachable at http://localhost:8000/health")

# 2. Auth endpoint
try:
    r = requests.post("http://localhost:8000/login", json={"username":"admin@example.com","password":"password123"}, timeout=3)
    if r.status_code in (200, 401):
        status.append("[✔ Completed] Backend auth endpoint available")
    else:
        status.append(f"[❌ Missing/Broken] Auth endpoint returned {r.status_code}")
except:
    status.append("[❌ Missing/Broken] Auth endpoint not reachable")

for s in status: print(s)
EOF

# === Frontend Features ===
echo ""
echo "📌 Frontend Features"
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health || echo "000")
if [ "$FRONTEND_HEALTH" == "200" ]; then
    echo "[✔ Completed] Frontend health check endpoint working"
else
    echo "[❌ Missing/Broken] Frontend not healthy (status $FRONTEND_HEALTH)"
fi

# === Testing Coverage ===
echo ""
echo "📌 Testing Coverage"
if [ -f "./frontend/web-app/tests/payroll-management.spec.ts" ]; then
    echo "[✔ Completed] Payroll Playwright tests present"
else
    echo "[❌ Missing/Broken] Payroll Playwright tests not found"
fi

# === Feature Roadmap ===
echo ""
echo "📌 Feature Roadmap"

echo "### Core Features"
echo "- [✔ Completed] Employee Profiles & Directory – basic details, job role, department, contact info."
echo "- [✔ Completed] Shift Scheduling – create, assign, and manage shifts."
echo "- [✔ Completed] Leave Management – vacation requests, sick leave, approvals."
echo "- [⏳ Pending] Attendance Tracking – clock-in/clock-out, break times, overtime logging."
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
