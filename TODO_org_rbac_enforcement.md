# Organization Security Enforcement Phase - TODO

## 1. Update RBAC for strict org isolation
- [x] Modify `can_access_company` to strictly scope COMPANY_ADMIN
- [x] Add sub-org visibility rules (sub-orgs can't see parent)
- [x] Add cross-org block methods

## 2. Add audit hooks
- [x] Integrate AuditService.log_event in org CRUD (org_created)
- [x] Integrate AuditService.log_event in channel CRUD (channel_created)
- [x] Integrate AuditService.log_event in meeting CRUD (meeting_created)
- [x] Add audit hooks for user assignment (user_assigned_role)
- [x] Add audit hooks for permission denials (in RBAC exceptions)
- [x] Add audit hooks for invites (user_invited in chat/meetings)

## 3. Harden admin roles
- [x] Add user role update endpoint in admin.py
- [x] Add checks for last superadmin protection
- [x] Add cross-org prevention

## 4. Enforce cross-org blocks
- [x] Update chat.py to block DMs/channels across orgs
- [x] Update meetings.py to block invites across orgs

## 5. Write unit tests
- [x] Extend test_rbac.py with tests for org visibility
- [x] Extend test_rbac.py with tests for role enforcement
- [x] Extend test_rbac.py with tests for audit events on denials/creates
- [x] Extend test_rbac.py with tests for cross-org blocks

## 6. Confirm existing tests pass
- [x] Run pytest after changes

## 7. Output summary
- [ ] List new endpoints, permissions, audit events
