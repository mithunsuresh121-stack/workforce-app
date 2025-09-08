#!/bin/bash
set -e

BASE_URL="http://localhost:8000"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYW5hZ2VyQHRlc3QuY29tIiwiY29tcGFueV9pZCI6MSwicm9sZSI6Ik1hbmFnZXIiLCJleHAiOjE3NTcyMjk0NjN9.p0BjIyOZUH-yfHrqlrDBMteRZEzPWxGmJwu9lND3QLk"   # replace with your valid token
ASSIGNEE_ID=30
COMPANY_ID=1

echo "🚀 Starting Notification Flow Test"
echo "==================================="

# Track results
PASSED=0
FAILED=0

# Helper function
check_success() {
  if [ $1 -eq 0 ]; then
    echo "   ✅ $2"
    PASSED=$((PASSED+1))
  else
    echo "   ❌ $2"
    FAILED=$((FAILED+1))
  fi
}

# 1. Reset notification preferences
echo "🗑️  Resetting preferences to defaults..."
curl -s -X DELETE "$BASE_URL/notification-preferences/" \
  -H "Authorization: Bearer $TOKEN" | jq >/dev/null
check_success $? "Reset preferences"

# 2. Create a test task (triggers notification)
echo ""
echo "📝 Creating a test task..."
CREATE_RESP=$(curl -s -o /tmp/task_resp.json -w "%{http_code}" -X POST "$BASE_URL/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"title\": \"Test Task - $(date '+%Y-%m-%d %H:%M:%S')\",
    \"description\": \"This is a test task notification\",
    \"status\": \"Pending\",
    \"priority\": \"High\",
    \"assignee_id\": $ASSIGNEE_ID,
    \"company_id\": $COMPANY_ID
  }")
if [ "$CREATE_RESP" -eq 200 ] || [ "$CREATE_RESP" -eq 201 ]; then
  check_success 0 "Task creation"
else
  check_success 1 "Task creation (status $CREATE_RESP)"
fi

# 3. Fetch notifications
echo ""
echo "🔔 Fetching notifications..."
NOTIFS=$(curl -s -X GET "$BASE_URL/notifications/" \
  -H "Authorization: Bearer $TOKEN")
echo "$NOTIFS" | jq
if [ "$(echo "$NOTIFS" | jq length)" -gt 0 ]; then
  check_success 0 "Fetched notifications"
else
  check_success 1 "Fetched notifications (none found)"
fi

# Extract first unread notification ID (if any)
NOTIF_ID=$(echo "$NOTIFS" | jq '.[0].id // empty')

# 4. Mark notification as read
if [ -n "$NOTIF_ID" ]; then
  echo ""
  echo "✅ Marking notification $NOTIF_ID as read..."
  MARK_RESP=$(curl -s -o /tmp/mark_resp.json -w "%{http_code}" -X POST "$BASE_URL/notifications/mark-read/$NOTIF_ID" \
    -H "Authorization: Bearer $TOKEN")
  if [ "$MARK_RESP" -eq 200 ]; then
    check_success 0 "Mark notification as read"
  else
    check_success 1 "Mark notification as read (status $MARK_RESP)"
  fi
else
  echo "⚠️  No notifications found to mark as read."
  FAILED=$((FAILED+1))
fi

echo ""
echo "🎯 Notification Flow Test Completed"
echo "==================================="
echo "✅ PASSED: $PASSED"
echo "❌ FAILED: $FAILED"

if [ $FAILED -eq 0 ]; then
  echo "🎉 All tests passed successfully!"
else
  echo "⚠️ Some tests failed. Check logs above."
fi
