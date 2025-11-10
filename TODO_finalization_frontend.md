# Frontend Finalization Tasks

## Migration to Vite + TypeScript
- [x] Install Vite and TypeScript dependencies
- [x] Create vite.config.ts
- [x] Create tsconfig.json
- [x] Update package.json scripts for Vite
- [x] Rename App.jsx to App.tsx
- [x] Rename other .jsx files to .tsx (criticalPath.test.jsx, etc.)

## Add Missing Dependencies
- [x] Add @tanstack/react-query for data fetching
- [x] Add react-infinite-scroll-component for infinite scroll
- [x] Add TypeScript types (@types/node, @types/react, etc.)
- [x] Update package.json with new dependencies

## Fix Vitest Configuration
- [x] Rename vitest.config.js to vitest.config.ts
- [x] Update vitest config for TypeScript support
- [x] Ensure proper test environment setup

## Implement WebSocket Notifications Hook
- [x] Create src/hooks/useWebSocketNotifications.tsx
- [x] Base it on existing useWebSocket.js
- [x] Add notification-specific logic
- [x] Handle real-time notification updates

## Create Notification Settings UI
- [x] Create src/pages/NotificationSettings.tsx
- [x] Add UI for toggling email/WS preferences
- [x] Implement save functionality via API
- [x] Add route to App.tsx

## Update App.tsx for Lazy Loading
- [x] Add React.lazy imports for route components
- [x] Wrap routes with Suspense
- [x] Ensure proper loading states

## Update Notifications Page
- [x] Integrate infinite scroll component
- [x] Add WebSocket integration for real-time updates
- [x] Remove polling mechanism
- [x] Update to TypeScript (.tsx)

## Write Tests
- [x] Create NotificationSettings.test.tsx
- [x] Create useWebSocketNotifications.test.tsx
- [x] Update criticalPath.test.tsx for TypeScript
- [x] Ensure all tests pass with Vitest

## TypeScript Types and Error Handling
- [x] Add proper TypeScript types throughout
- [x] Implement error handling for WS connections
- [x] Ensure responsive Tailwind CSS classes

## Integration Testing
- [ ] Test WebSocket integration with backend (ws://localhost:8000/ws/notifications)
- [ ] Verify API endpoints work correctly
- [ ] Test lazy loading and infinite scroll functionality
- [ ] Run full test suite
