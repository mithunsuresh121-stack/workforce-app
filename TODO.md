# Phase 1: Core Auth, Roles, User/Company/Profile CRUD - COMPLETED

## Overview
Implement foundational features: Refine models for consistency, strengthen RBAC with company isolation, complete CRUD APIs, integrate Linear UI in key frontend pages, enhance seeding with error simulation. Test with provided credentials and ensure docker-compose runs smoothly.

## Steps

- [x] Refine backend models: Update Leave.py (tenant_id -> company_id Integer FK, add employee_id FK, enums for type/status, relationships to User/Company). Similar for Shift.py. Verify/refine Document.py (add company_id, user_id optional, access_role enum, relationships).

- [x] Create Alembic migration script for model refinements (alter columns, add FKs/indexes, ensure no data loss).

- [x] Run Alembic migration: alembic upgrade head.

- [x] Enhance permissions.py: Add functions for role checks (e.g., requires_role(role: str), company_isolation(current_user_company_id)).

- [x] Update deps.py: Ensure get_current_user decodes JWT, fetches User with role/company_id, injects into endpoints.

- [x] Update auth.py: Clean up (remove mock notifications, fix any inconsistencies like role fallback, ensure proper JWT claims with role/company_id).

- [x] Implement/Enhance CRUD routers:
  - companies.py: SuperAdmin-only CRUD (create/read/update/delete companies).
  - users.py: CompanyAdmin CRUD within company; SuperAdmin all; Employee self-update (limited fields).
  - employees.py/profile.py: CRUD EmployeeProfile; Manager update subordinates; Employee self-update; enforce company isolation.

- [x] Update schemas.py: Add/enhance Pydantic models (e.g., UserCreate with role enum, CompanyCreate, EmployeeProfileUpdate with validations like unique employee_id).

- [x] Update crud.py: Add/enhance functions (e.g., create_user with company check, get_users_by_company, update_profile with RBAC filters).

- [x] Frontend: Check package.json for @linear/ui or similar; if missing, add and install via npm.

- [x] Integrate Linear UI components:
  - Login.jsx/Signup.jsx: Use Linear Button, Input, Card for forms.
  - Profile.jsx: Enhance with Linear Avatar, TextField, Select.
  - EditProfileForm_linear.jsx: Ensure consistent Linear styling.
  - App.jsx/Layout.jsx: Add role-based sidebar navigation (e.g., Employee: Profile/Leave; Manager: +Employees/Dashboard).

- [x] Update AuthContext.jsx/ProtectedRoute.jsx: Handle JWT, role-based access, redirect unauth.

- [x] Enhance seed_data.py: Add clean_db() function (delete cascades safely), seed functions for companies/users/profiles per role, --errors mode (simulate duplicates, invalid FKs, log errors), safe re-run checks (if exists, skip/update).

- [x] Run seed_data.py normal mode: python backend/seed_data.py (create sample data matching test credentials).

- [x] Run seed_data.py --errors mode: Simulate and log errors without crashing.

- [x] Test login flows: Use curl or browser to verify credentials (SuperAdmin: superadmin@workforce.com/password123 no company; CompanyAdmin: admin1@techcorp.com/password123 company_id=10; etc.). Check 401 for inactive/invalid.

- [x] Run pytest: pytest tests/ -v (focus on test_auth.py, test_employees.py, add RBAC tests if needed).

- [x] Verify docker-compose: docker-compose up (backend:8000, frontend:3000, Postgres); check logs, access http://localhost:3000/login.

- [x] Test API CRUD: Curl examples per role (e.g., SuperAdmin GET /companies; CompanyAdmin POST /users with company_id=10; Employee PUT /profile self-update).

- [x] Mark Phase 1 complete: Update TODO.md, prepare for Phase 2 (Attendance + Leave workflows).

## Phase 2: Attendance + Leave Workflows

## Overview
Implement attendance tracking, leave management, shift scheduling, and document management with proper RBAC and company isolation.

## Steps

- [ ] Refine models: Update Task.py (add company_id FK, assignee/manager relationships), ensure all models have proper relationships.

- [ ] Create Alembic migration for Phase 2 models.

- [ ] Run Alembic migration.

- [ ] Enhance permissions.py: Add task, leave, shift, document permissions.

- [ ] Update routers: tasks.py, leaves.py, shifts.py, documents.py with CRUD and RBAC.

- [ ] Update schemas.py: Add/enhance schemas for tasks, leaves, shifts, documents.

- [ ] Update crud.py: Add functions for tasks, leaves, shifts, documents.

- [ ] Frontend: Add pages for Tasks, Leaves, Shifts, Documents with Linear UI.

- [ ] Update seed_data.py: Add sample tasks, leaves, shifts, documents.

- [ ] Test all endpoints and frontend flows.

- [ ] Mark Phase 2 complete.

## Notes
- Use venv for backend, nvm for frontend.
- No global installs; update requirements.txt/package.json if new deps.
- If errors (syntax, port conflicts), auto-fix/retry per .blackboxrules.
- Track progress: Update checkboxes here after each step.
