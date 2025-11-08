# Integration TODO List

## 1. Backend API Integration
- [ ] Verify API base URLs (currently localhost:8000)
- [ ] Update frontend .env with production API endpoint (if needed)
- [ ] Update mobile config.dart with production API endpoint
- [ ] Run API schema validation using /docs or /openapi.json
- [ ] Ensure CORS settings allow frontend and mobile origins

## 2. Frontend (React) Verification
- [ ] Check Dashboard.jsx for live data fetch from backend
- [ ] Verify AuthContext.jsx API calls
- [ ] Fix any missing API bindings in services/
- [ ] Test WebSocket connections for chat and notifications
- [ ] Run npm test for frontend

## 3. Mobile (Flutter) Synchronization
- [ ] Validate api_service.dart endpoints match backend routes
- [ ] Update WebSocket signaling to production backend URL
- [ ] Test login, chat, and meeting flows with JWT tokens
- [ ] Resolve TODOs in mobile/TODO.md
- [ ] Run flutter test

## 4. Testing & Verification
- [ ] Run end-to-end flow: Login → Dashboard → Chat → Notifications
- [ ] Ensure no critical errors in tests
- [ ] Verify cross-platform sync

## 5. Final Output
- [ ] Generate integration_readiness_report.md
