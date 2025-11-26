# WebSocket Test Fixes TODO

## Steps to Complete
- [x] Update error assertions in 'handles fetch error' to expect 'Failed to load notifications'
- [x] Update 'handles mark as read error' to expect 'Failed to mark as read'
- [x] Change 'handles mark as read' test to expect resolves instead of rejects
- [x] Modify beforeEach: Remove server.close(), add server.resetHandlers()
- [x] Add addEventListener, removeEventListener, dispatchEvent to MockWebSocket
- [x] Add wait for handlers to be set in WebSocket message test
- [x] Run `cd frontend-web/web-app && npm test -- --run useWebSocketNotifications.test.tsx` to confirm all 5 tests pass
- [x] Update `TODO_test_fixes.md` to mark WebSocket test fixes complete
