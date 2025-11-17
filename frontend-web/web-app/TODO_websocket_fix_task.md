# TODO: Fix Failing WebSocket Tests in useWebSocketNotifications

## Steps to Complete
- [ ] Modify MockWebSocket constructor in `frontend-web/web-app/src/__tests__/useWebSocketNotifications.test.tsx` to automatically trigger onopen after instantiation using setTimeout for async behavior
- [ ] Update 'handles WebSocket connection' test: Remove manual onopen trigger; instead, wait for the connected state to become true
- [ ] Update 'handles WebSocket message' test: Wait for connected state, then simulate the message event without manual onopen trigger
- [ ] Run `npm test -- --coverage` in the frontend-web/web-app directory to verify all 20 tests pass
- [ ] Update `frontend-web/web-app/TODO.md` to mark the WebSocket test fix as complete
- [ ] Update `TODO_integration.md` to mark WebSocket testing as complete
