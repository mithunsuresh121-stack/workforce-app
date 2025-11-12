# Integration Steps TODO

## Frontend Updates
- [x] Refactor src/hooks/useProcurement.ts to use import.meta.env.VITE_API_URL with fallback (prod: https://api.workforce-app.com, dev: http://localhost:8000). Update WebSocket to wss://api.workforce-app.com/ws/procurement/{companyId}.
- [x] Locate AuthContext (or read/update src/pages/Login.tsx, Signup.tsx) for /api/auth/* calls; refactor to same apiBase, add token refresh if missing.
- [x] Create/update frontend-web/web-app/.env with VITE_API_URL=https://api.workforce-app.com.

## Mobile Updates
- [x] List mobile dir to confirm api_service.dart/config.dart.
- [x] Update mobile/lib/services/api_service.dart (or config.dart) for prod API base URL and WebSocket signaling to wss://api.workforce-app.com/ws/notifications.

## Verification
- [x] Run backend locally (cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000) and access /docs for API schema validation.
- [ ] Test WebSocket: Run frontend/backend, use browser to connect and verify notifications.
- [ ] Run frontend tests: cd frontend-web/web-app && nvm use && npm test.
- [ ] Run backend tests: cd backend && source venv/bin/activate && pytest --cov.
- [ ] Run mobile tests: cd mobile && fvm use && flutter test.

## E2E & Finalization
- [ ] E2E flow: Launch frontend in browser, simulate login → dashboard → chat → notifications → procurement; verify data fetch/WebSocket.
- [ ] Update TODO_integration.md to mark all [ ] as [x].
- [ ] Confirm RBAC/token handling in auth calls.

Progress: Starting with frontend refactor.
