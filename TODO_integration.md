# Integration TODO List

## 1. Backend API Integration
- [x] Verify API base URLs (updated to production)
- [x] Update frontend .env with production API endpoint (VITE_API_URL=https://api.workforce-app.com)
- [x] Update mobile config.dart with production API endpoint (baseUrl and wsUrl updated)
- [ ] Run API schema validation using /docs or /openapi.json
- [x] Ensure CORS settings allow frontend and mobile origins (backend optimizations complete)
- [x] Add new /hello endpoint with logging (logs request method and path, returns JSON welcome message)
- [x] Add /api/notifications/publish endpoint for Redis pub/sub testing (logs request metadata, publishes to Redis channel)

## 2. Frontend (React) Verification
- [x] Check Dashboard.jsx for live data fetch from backend (useProcurement.ts uses env vars)
- [x] Verify AuthContext.jsx API calls (uses env vars)
- [x] Fix any missing API bindings in services/ (useWebSocketNotifications updated)
- [ ] Test WebSocket connections for chat and notifications
- [ ] Run npm test for frontend

## 3. Mobile (Flutter) Synchronization
- [x] Validate api_service.dart endpoints match backend routes
- [x] Update WebSocket signaling to production backend URL (wsUrl added)
- [ ] Test login, chat, and meeting flows with JWT tokens
- [ ] Resolve TODOs in mobile/TODO.md
- [ ] Run flutter test

## 4. Testing & Verification
- [ ] Run end-to-end flow: Login → Dashboard → Chat → Notifications
- [ ] Ensure no critical errors in tests
- [ ] Verify cross-platform sync

## 5. Final Output
- [x] Generate integration_readiness_report.md
- [x] Production deployment configured (Heroku/Vercel configs, CORS updated, E2E tests written)
- [x] Production deployment complete (backend on Heroku/Vercel, frontend on Vercel, E2E tests run against production URLs)
