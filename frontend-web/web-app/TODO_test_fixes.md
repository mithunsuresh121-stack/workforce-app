# TODO: Fix Failing Frontend Tests

## Overview
Fix failing tests in criticalPath.test.tsx (9/10 failing), NotificationSettings.test.tsx (1 failing), and useWebSocketNotifications.test.tsx (5/5 failing) by addressing auth mocking, async state updates, WebSocket connection logic, and mock sequencing.

## Steps
- [ ] Fix useWebSocketNotifications hook to properly connect WS after user loads
- [ ] Update useWebSocketNotifications.test.tsx with proper auth mocks and act() wrapping
- [ ] Add data-testid to NotificationSettings component for stable test queries
- [ ] Fix NotificationSettings.test.tsx mock sequencing for save success/error tests
- [ ] Update criticalPath.test.tsx with proper auth mocks, specific queries, and mock responses
- [ ] Run tests to verify all pass with good coverage
- [ ] Update main TODO.md to reflect completion
