# Application Finalization TODO

## Current Status
- Date: November 07, 2025
- Overall Readiness: 99% (per integration_readiness_report.md)
- Focus: Email integration, frontend finalization, backend optimizations, production deployment, documentation

## Steps from Approved Plan

### 1. Email Integration
- [ ] Enhance backend/app/services/email_service.py: Add dynamic placeholders to templates (e.g., {user_name}, {company_name}); implement SendGrid API fallback using sendgrid-python if SMTP fails.
- [ ] Update backend/app/config.py: Add Pydantic validation for SENDGRID_API_KEY (required in prod); log warning if missing.
- [ ] Create .env: Add SENDGRID_API_KEY (use placeholder for test; prompt user if real needed); set SMTP for Mailtrap test (smtp.mailtrap.io:2525, username/password placeholders).
- [ ] Update backend/app/routers/auth.py: Implement proper reset token storage/verification (add ResetToken model via alembic if needed; currently placeholder raises 400).
- [ ] Create backend/tests/test_email_integration.py: Add unit tests for send_welcome_email, send_password_reset_email, send_notification_email (mock smtplib/SendGrid, assert calls/content).
- [ ] Test email: Start uvicorn, trigger signup/password reset via curl/Postman, verify logs/delivery (use Mailtrap for SMTP test).

### 2. Frontend Finalization
- [ ] Fix frontend-web/web-app/vitest.config.js: Remove transformMode (use Vite defaults), add coverage config (reporter: ['text', 'json', 'html']), ensure testMatch: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'].
- [ ] Update frontend-web/web-app/src/setupTests.js: Confirm vi.mock('axios') at top; add vi.mock('ws') for WebSocket.
- [ ] Update frontend-web/web-app/src/pages/Notifications.jsx: Integrate useWebSocket hook for real-time updates (subscribe to user notifications channel); add unread count badge in components/Navbar.jsx.
- [ ] Create frontend-web/web-app/src/pages/Settings.jsx (or extend pages/Profile.jsx): Add form for notification preferences (toggles for email_enabled, push_enabled, mute_all, notification_types; fetch/update via api.put('/notification-preferences/')).
- [ ] Optimize frontend: Add React.lazy/memo to pages/Dashboard.jsx, pages/Chat.jsx; implement infinite scroll in Notifications.jsx using react-intersection-observer.
- [ ] Test frontend: Run npm test (verify no Vitest errors), manual responsiveness check, WebSocket stability (simulate via browser dev tools).

### 3. Backend/API Completion & Optimization
- [ ] Update backend/app/main.py: Add Redis caching to /notifications/ endpoint (use redis_service.get/set with TTL=300s for user notifications); extend CORS for prod origins (e.g., https://app.workforceapp.com).
- [ ] Update backend/app/crud_notifications.py: Add pagination to get_notifications_for_user (limit/offset params); ensure .order_by(Notification.created_at.desc()).
- [ ] Update backend/app/routers/notifications.py: Add query params (limit: int=20, offset: int=0, type: Optional[str]) to GET /notifications/.
- [ ] Fix WebSocket: Update backend/app/services/ws_broadcast.py: Add heartbeat ping/pong (every 30s) to fix minor test failure.
- [ ] Address non-critical: Run alembic migration for "companies" table issue if schema mismatch (check via check_tables.py); fix Flutter fvm path in mobile/README.md (add export PATH=$PATH:$(fvm flutter path)).
- [ ] Test backend: Run pytest -v (aim 100%), uvicorn --reload, test endpoints with curl, WebSocket via wscat redis://localhost:6379.

### 4. Production Deployment
- [ ] Update docs/DEPLOYMENT.md: Add detailed steps (backend: heroku create → git push heroku main with Procfile=gunicorn backend.app.main:app; frontend: vercel --prod; mobile: flutter build → manual upload).
- [ ] Update backend/Dockerfile: Multi-stage build (prod: no dev deps, expose 8000); update docker-compose.yml for prod env (external DB/Redis).
- [ ] Update frontend-web/web-app/package.json: Ensure "build": "vite build" for prod.
- [ ] Config updates: frontend-web/web-app/src/contexts/AuthContext.jsx → REACT_APP_API_URL=process.env.REACT_APP_API_URL || 'https://api.workforceapp.com/api'; mobile/lib/api_service.dart → const String baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'https://api.workforceapp.com');
- [ ] Deploy: execute docker build -t workforce-backend . && docker run -p 8000:8000 workforce-backend (local sim); guide manual Heroku/Vercel if no cloud creds.
- [ ] Final E2E: Use browser_action to test prod-like flow (launch https://localhost:3000 → login → dashboard → chat → notifications; trigger email, verify delivery).

### 5. Documentation
- [ ] Update TODO_integration.md: Add email/frontend sections, mark all [x] complete; append prod deployment notes.
- [ ] Update integration_readiness_report.md: Set overall to 100%, add sections for email (verified), frontend (Vitest fixed, preferences UI added), optimizations (caching/pagination), deployment (configs updated, E2E passed).

## Tracking
- Update this file after each major step completion.
- Pending: None initially.
- Blockers: SendGrid key for prod emails (use test mode).
