# WebSocket Test Fixes TODO

## Steps to Complete
- [ ] Update error assertions in 'handles fetch error' to expect 'Failed to load notifications'
- [ ] Update 'handles mark as read error' to expect 'Failed to mark as read'
- [ ] Change 'handles mark as read' test to expect resolves instead of rejects
- [ ] Modify beforeEach: Remove server.close(), add server.resetHandlers()
- [ ] Run `cd frontend-web/web-app && npm test -- --coverage` to confirm all 5 tests pass
- [ ] Update `TODO_test_fixes.md` to mark WebSocket test fixes complete
