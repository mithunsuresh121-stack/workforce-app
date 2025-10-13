# Phase 7: Monitoring + Finalization TODO

## 1. Expand seed_data.py
- [ ] Update backend/seed_data.py to add 8-10 records per model (leaves, shifts, tasks, documents, notifications) with variety in statuses, types, ownership
- [ ] Ensure no foreign key conflicts and proper relationships

## 2. Integrate structlog
- [ ] Install structlog: pip install structlog
- [ ] Update backend/app/__init__.py to use structlog as primary logger with context (timestamp, user_id, endpoint, level)
- [ ] Maintain backward compatibility and console readability

## 3. Add pytest tests
- [ ] Create/update tests/test_workflows.py for backend workflows: auth, leaves, chat, docs, notifications
- [ ] Ensure coverage for prioritized flows

## 4. Add Playwright tests
- [ ] Install Playwright in frontend-web: npm install playwright
- [ ] Create frontend-web/playwright.config.js
- [ ] Create frontend-web/tests/ for login, navigation, CRUD UI flows

## 5. Update Docker configuration
- [ ] Update docker-compose.yml for migrations, testing, backend/frontend startup

## 6. Update README.md
- [ ] Add deployment steps, migrations, testing documentation

## 7. Verification and Reporting
- [ ] Run seeding and verify data
- [ ] Run backend tests (pytest)
- [ ] Run frontend tests (Playwright)
- [ ] Verify structlog output
- [ ] Test deployment setup
- [ ] Report completion
