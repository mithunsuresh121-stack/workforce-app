# TODO: Redis Pub/Sub Production Verification, WebSocket Test Fixes, and CI/CD Setup

## 1. Redis Pub/Sub Production Verification
- [ ] Deploy backend to Vercel (`cd backend && vercel --prod`)
- [ ] Test pub/sub functionality via redis-cli or test script
- [ ] Check logs for successful pub/sub operations
- [ ] Run backend tests including pub/sub tests in test_notifications_caching.py

## 2. WebSocket Test Fixes
- [ ] Update useWebSocketNotifications.tsx WebSocket URL to use import.meta.env.VITE_WS_URL || 'wss://api.workforce-app.com/ws/notifications'
- [ ] Update useWebSocketNotifications.test.tsx to include QueryClientProvider, AuthProvider, and proper MockWebSocket setup
- [ ] Fix test failures at lines 66 and 140

## 3. Run Tests
- [ ] Frontend: `cd frontend-web/web-app && npm test -- --coverage`
- [ ] Backend: `cd backend && pytest --cov`, including pub/sub tests

## 4. Update TODO_integration.md
- [ ] Mark Redis pub/sub fix and WebSocket test fixes complete

## 5. CI/CD Setup
- [ ] Create GitHub Actions workflow for tests and deployment
- [ ] Ensure secure Redis connections and HTTPS

## 6. Verification
- [ ] Confirm alignment with Python 3.11.1, FastAPI 0.115.0, aioredis 1.3.1, React 18.2.0, TypeScript 5.9.3
