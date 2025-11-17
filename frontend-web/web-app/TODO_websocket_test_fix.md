# WebSocket Test Fixes TODO

## Steps to Complete
- [ ] Update `useWebSocketNotifications.test.tsx`:
  - Replace custom MockWebSocket with `vi.mock('ws')` for type-safe mocking.
  - Update useAuth mock to include `{ user: { id: '1', token: 'mock-token' }, loading: false }`.
  - Add `beforeEach(() => server.resetHandlers())` to disable MSW for WS tests.
  - Ensure all WS state updates (onopen, onmessage) are wrapped in `await act(async () => { ... })`.
  - Verify the 5 tests cover: mount, connection, markAsRead, fetch error, WS message.

- [ ] Run `cd frontend-web/web-app && npm test -- --coverage` to confirm all 5 tests pass.

- [ ] Update `TODO_test_fixes.md` to mark WebSocket test fixes complete.
