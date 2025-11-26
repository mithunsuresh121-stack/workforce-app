# TODO: Fix WebSocket Test in useWebSocketNotifications

## Steps to Complete
- [ ] Update 'handles WebSocket message' test in frontend-web/web-app/src/__tests__/useWebSocketNotifications.test.tsx: Remove test.skip and ensure proper event sequence (wait for WebSocket, handlers, dispatch open, then message)
- [ ] Run `npm test -- --coverage` in frontend-web/web-app to verify all 20 tests pass
- [ ] Update frontend-web/web-app/TODO.md to mark WebSocket test fix as complete
- [ ] Update TODO_integration.md to mark WebSocket testing as complete
