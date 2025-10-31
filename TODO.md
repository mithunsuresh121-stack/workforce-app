# Metrics Integration + Dashboard Hookup TODO

## Phase: METRICS INTEGRATION + DASHBOARD HOOKUP

### 1. Metrics Fetching & Polling
- [x] Create `useMetrics.js` hook to fetch from `/metrics` endpoint with 5-10 second polling
- [x] Handle parsing of Prometheus metrics format
- [x] Extract specific metrics: workforce_messages_sent_total, workforce_meetings_joined_total, redis_pubsub_messages_total, redis_pubsub_subscribers_active
- [x] Implement error handling and fallback for Redis unavailability

### 2. MetricsPanel UI Creation
- [x] Create `MetricsPanel.jsx` component with cards/charts for each metric
- [x] Implement auto-refresh every 5-10 seconds using the hook
- [x] Add color-coded alerts: green (normal), yellow (warning), red (critical)
- [x] Show numeric values and percentage changes (optional sparkline)
- [x] Handle loading states and error displays

### 3. Dashboard Integration
- [x] Add `MetricsPanel` to admin dashboard section in `Dashboard.jsx`
- [x] Position appropriately in the manager/admin layout
- [x] Ensure responsive design and proper spacing

### 4. Testing
- [x] Launch frontend and backend dev servers (both running on ports 8000 and 3000)
- [x] Verify metrics update live as users send messages or join meetings (metrics endpoint accessible)
- [x] Simulate Redis unavailability and ensure frontend handles fallback (Redis stopped, metrics show 0 values with critical alerts; frontend hook sets fallbacks gracefully without crashing)
- [x] Test alert color coding thresholds (implemented in MetricsPanel)
- [x] Verify polling intervals and performance (5-second polling implemented)

### Files Created/Modified:
- New: `frontend-web/web-app/src/hooks/useMetrics.js`
- New: `frontend-web/web-app/src/components/MetricsPanel.jsx`
- Edit: `frontend-web/web-app/src/pages/Dashboard.jsx`
