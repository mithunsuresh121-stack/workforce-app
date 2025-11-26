# TODO List for Workforce App

## High Priority
- [ ] Fix Failing WebSocket Test in useWebSocketNotifications.test.tsx
  - [ ] Debug why `useWebSocketNotifications.tsx` doesn't set `connected` to `true`.
  - [ ] Ensure WebSocket mock triggers `onopen` and `onmessage`.
  - [ ] Mock connection state correctly.
  - [ ] Update `useWebSocketNotifications.tsx` if needed (e.g., `onopen` logic).
  - [ ] Run `npm test` to confirm all 20 tests pass.
  - [ ] Update `TODO_integration.md` to mark fix complete.

## Medium Priority
- [ ] Integrate frontend-backend features
- [ ] Verify API endpoints

## Low Priority
- [ ] Other tasks...
