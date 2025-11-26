# AI Governance Implementation TODO

## New Files
- [ ] backend/app/schemas/ai.py - Pydantic models for AI requests/responses
- [ ] backend/app/services/ai_service.py - AI gatekeeper logic
- [ ] backend/app/routers/ai.py - AI endpoints (/api/ai/query)
- [ ] backend/alembic/versions/add_ai_audit_fields.py - Migration for AuditLog

## Edits
- [ ] backend/app/models/audit_log.py - Add AI audit fields
- [ ] backend/app/services/audit_service.py - Add log_ai_event method
- [ ] backend/app/services/security_service.py - Add AI anomaly detection
- [ ] backend/app/core/rbac.py - Add can_use_ai_capability
- [ ] backend/app/routers/admin.py - Add /admin/ai/policy and /admin/ai/logs
- [ ] backend/app/main.py - Include ai router
- [ ] backend/tests/test_security.py - Add AI-specific tests

## Testing
- [ ] Run pytest backend/tests/test_security.py
- [ ] Verify all tests pass (existing + new)
- [ ] Output test results
