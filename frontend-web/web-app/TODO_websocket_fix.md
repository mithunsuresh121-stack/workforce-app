# TODO: Fix Failing WebSocket Test in useWebSocketNotifications

## Steps to Complete
- [ ] Fix wsUrl template literal in useWebSocketNotifications.tsx (use backticks for token interpolation)
- [ ] Update 'handles WebSocket connection' test to wait for WebSocket instantiation before triggering onopen
- [ ] Update 'handles WebSocket message' test to wait for WebSocket instantiation and ensure proper event sequence
- [ ] Run `npm test -- --coverage` to verify all 20 tests pass
- [ ] Update frontend-web/web-app/TODO.md to mark WebSocket test fix as complete
- [ ] Update TODO_integration.md to mark WebSocket testing as complete
