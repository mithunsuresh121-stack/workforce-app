# Enterprise Org Structure + RBAC Implementation TODO

## Phase 1: Database + Models (Completed)
- [x] Create CompanyDepartment model (backend/app/models/company_department.py)
- [x] Create CompanyTeam model (backend/app/models/company_team.py)
- [x] Update User model: Add UserRole Enum, department_id/team_id FKs, relationships (backend/app/models/user.py)
- [x] Update Company model: Add departments relationship (backend/app/models/company.py)
- [x] Update Channel model: Add department_id/team_id FKs, relationships (backend/app/models/channels.py)
- [x] Update Meeting model: Add department_id/team_id FKs, relationships (backend/app/models/meetings.py)
- [ ] Generate Alembic migration for new tables/FKs/Enum (alembic revision --autogenerate -m "add_org_structure_and_rbac")
- [ ] Run migration (alembic upgrade head)
- [ ] Handle legacy role mapping in migration (e.g., update "Manager" to DEPARTMENT_ADMIN, "SuperAdmin" to SUPERADMIN, "CompanyAdmin" to COMPANY_ADMIN)
- [ ] Extend company bootstrap in company_service.py: Create General Department/Team, assign to admin (COMPANY_ADMIN role)

## Phase 2: RBAC Rules & Middleware
- [ ] Create backend/app/core/rbac.py: UserRole (if needed), get_rbac_dependency, require_role, require_company_access, require_dept_access, require_team_access, can_create_channel, can_join_channel, etc.
- [ ] Update backend/app/deps.py: Enrich get_current_claims/user with role, department_id, team_id from JWT/user
- [ ] Apply RBAC to backend/app/routers/companies.py: Add Depends for create/get/delete (SUPERADMIN/COMPANY_ADMIN)
- [ ] Apply RBAC to backend/app/routers/chat.py: For channels/* (require_company_access, can_create/join)
- [ ] Apply RBAC to backend/app/routers/meetings.py: For meetings/* (require_company_access, can_create/join)
- [ ] Apply RBAC to backend/app/routers/employees.py (or users): Admin-only for assign-org

## Phase 3: API Endpoints
- [ ] Create backend/app/schemas/org.py: DepartmentCreate, TeamCreate, AssignOrg, OrgTreeOut schemas
- [ ] Create backend/app/crud/org.py: CRUD for departments, teams, user assignments
- [ ] Create backend/app/routers/org.py: POST /department, POST /team, PATCH /users/{id}/assign-org, GET /tree
- [ ] Include org router in backend/app/main.py

## Phase 4: Chat + Meetings Logic Update
- [ ] Update chat CRUD/services: Validate channel creation/join by role/dept/team (e.g., TEAM_LEAD only team channels)
- [ ] Update meetings CRUD/services: Similar validation for create/join
- [ ] New migration for any additional constraints/indexes on dept/team FKs

## Phase 5: Frontend Integration (React)
- [ ] Explore frontend-web/src/ for AuthContext, update JWT decode to store role/company_id/dept_id/team_id
- [ ] Create frontend-web/src/components/Admin/OrganizationStructure.js: CRUD UI for depts/teams (forms, tree)
- [ ] Update frontend-web/src/components/UserProfile.js: Dropdowns for assign dept/team/role (admin-only)
- [ ] Create/Update frontend-web/src/components/UserBadge.js: Role badge
- [ ] Update frontend-web/src/components/Chat/ChatList.js: Filter by team/dept
- [ ] Update frontend-web/src/pages/Meetings.js: Restrict join by RBAC (check user vs meeting scope)
- [ ] Update API calls to use enriched user state (e.g., include dept_id in queries)

## Phase 6: Tests
- [ ] Create backend/tests/test_rbac.py: Unit tests for each role/scenario
- [ ] Create backend/tests/test_org_creation.py: Dept/team create/assign/tree
- [ ] Create backend/tests/test_permissions.py: Channel/meeting access rejections
- [ ] Update backend/tests/conftest.py: Fixtures for test users with roles/dept/team
- [ ] Add frontend tests: OrgStructure render, badges, UI restrictions (e.g., in src/__tests__/)
- [ ] Run all tests: pytest backend/tests/, npm test frontend

## Followup Verification
- [ ] Run app, create company: Verify bootstrap creates dept/team/admin assignment
- [ ] Test APIs: Create org, assign, get tree with different roles
- [ ] Test chat/meetings: Restricted access enforcement
- [ ] Frontend: npm start, verify UI, role badges, filters, restrictions
- [ ] Browser verification: Launch app, screenshot admin panel/org tree
- [ ] All tests green, no breaks to existing features
