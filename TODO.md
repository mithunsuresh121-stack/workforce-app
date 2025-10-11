# Phase 5 Live Verification and Deployment Readiness Checks

## Backend Verification
- [x] Activate venv and run alembic upgrade head in backend directory (already at head)
- [x] Execute seed script: python backend/seed_data.py (documents and announcements seeded)
- [x] Run pytest for document routes: pytest tests/test_document_routes.py -v (passed)
- [ ] Run pytest for notifications routes: pytest tests/test_notifications_routes.py -v

## Frontend Verification
- [x] Start backend server (uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) (running)
- [ ] Start frontend server (cd frontend-web/web-app && nvm use && npm start)
- [ ] Browser verification: Launch browser at localhost:3000, login as different roles, verify document upload/view/download, announcements view

## Final Confirmation
- [ ] Review logs and test outputs for errors
- [ ] Confirm all endpoints and UI features work as per checklist
