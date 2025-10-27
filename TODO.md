# Structlog Consistency Verification and Setup TODO

## Overview
Perform comprehensive verification and continuous validation setup for Structlog consistency across the backend. Ensure all modules use Structlog with JSON structured logging, consistent fields (event, timestamp, user_id, company_id, level), and eliminate print() and logging calls.

## Steps

### 1. Add Structlog Imports and Loggers to Missing Files
- [ ] Add `import structlog` and `logger = structlog.get_logger(__name__)` to:
  - `backend/app/routers/companies.py`
  - `backend/app/routers/dashboard.py`
  - `backend/app/routers/documents.py`
  - `backend/app/routers/employees.py`
  - `backend/app/routers/leaves.py`
  - `backend/app/routers/notification_preferences.py`
  - `backend/app/routers/notifications.py`
  - `backend/app/routers/payroll.py`
  - `backend/app/routers/profile.py` (merge final/fixed if needed)
  - `backend/app/routers/shifts.py`
  - `backend/app/routers/tasks.py`
  - `backend/app/routers/ws_notifications.py`
  - `backend/app/routers/chat.py`
  - `backend/app/crud_announcements.py`
  - `backend/app/crud_chat.py`
  - `backend/app/crud_documents.py`

### 2. Replace Print Statements with Structlog Calls
- [ ] Replace all `print()` in:
  - `backend/app/routers/employees.py` (debug messages)
  - `backend/app/routers/leaves.py` (warnings)
  - `backend/app/routers/shifts.py` (warnings)
  - `backend/app/routers/attendance.py` (partial, clock-out prints)
  - `backend/app/seed_demo_user.py`
  - `backend/app/seed_demo_user_fixed.py`
  - `backend/app/seed_demo_user_final.py`
- [ ] Use `logger.info()`, `logger.warning()`, or `logger.error()` with consistent fields: `event`, `user_id`, `company_id`, etc.

### 3. Enhance Main.py Configuration for Mandatory Fields
- [ ] Update `backend/app/main.py` processors to enforce mandatory fields (event, timestamp, user_id, company_id, level) in all logs.
- [ ] Ensure middleware binds context (user_id, company_id) to logs.

### 4. Create Structlog Consistency Test
- [ ] Create `backend/tests/test_structlog_consistency.py` with tests to capture log outputs, assert JSON structure, and mandatory fields.
- [ ] Use caplog fixture to validate logs across modules.

### 5. Integrate Tests into Test Suite
- [ ] Create `backend/pytest.ini` with addopts for parallel execution and coverage.
- [ ] Update `backend/tests/conftest.py` if needed for fixtures.

### 6. Update Dependencies
- [ ] Ensure `pytest` and `pytest-cov` are in `backend/requirements.txt`; install if missing.

### 7. Run Tests and Verify
- [ ] Activate venv: `source backend/venv/bin/activate`
- [ ] Run `pytest -v tests/test_structlog_consistency.py --cov` to verify consistency.
- [ ] If failures, generate `backend/structlog_inconsistencies.log` with details.

### 8. Update Readiness Report
- [ ] If tests pass: Update report with ✅ Logging consistency: Structlog fully integrated...
- [ ] If failures: Update with 🔄 Logging consistency: Structlog integrated, but some modules emit inconsistent logs (see auto-generated structlog_inconsistencies.log).

## Notes
- Prioritize routers, CRUD, and services.
- Ensure JSON structured logging globally.
- Use context from current_user where possible for user_id/company_id.
- Mark seed files as non-prod if prints remain.
