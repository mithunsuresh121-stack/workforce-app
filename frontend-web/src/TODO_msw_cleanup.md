# MSW Cleanup in Tests - Task Breakdown

## Task Overview
Clean up manual fetch mocks in `useWebSocketNotifications.test.tsx`, ensure MSW handles all HTTP requests consistently, verify MSW setup, run tests, and update TODO files.

## Steps to Complete
- [ ] Update `src/__tests__/useWebSocketNotifications.test.tsx`:
  - Remove all manual `fetch` mocks (e.g., `(global.fetch as any).mockResolvedValueOnce()`).
  - Ensure HTTP requests (e.g., `/api/notifications/`) use MSW handlers from `handlers.ts`.
  - Override specific MSW handlers with `server.use()` if needed for individual tests (e.g., return empty array for WebSocket connection test).
  - Retain WebSocket mocks (global in `setupTests.js` or test-specific).
- [ ] Verify MSW setup in `setupTests.js`:
  - Confirm `setupServer(...handlers)` is active and intercepts all HTTP requests.
  - Ensure no conflicts between MSW and WebSocket mocks.
- [ ] Run tests: `cd frontend-web/web-app && npm test -- --coverage`.
- [ ] Update `TODO_test_fixes.md` to mark manual mock cleanup complete.
- [ ] Follow best practices: Consistent MSW usage, type-safe mocks, no backend calls.
- [ ] Confirm alignment with React 18.2.0, TypeScript 5.9.3, Vite, Vitest 1.6.0, @mswjs/msw 2.4.11.
