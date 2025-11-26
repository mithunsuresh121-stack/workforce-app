# Security Telemetry & Incident Response Layer Implementation

## Tasks
- [ ] Extend User model with lockout fields (is_locked, locked_until)
- [ ] Create SecurityService with SecurityEvent enum and anomaly detection
- [ ] Extend AuditService with security event logging methods
- [ ] Add admin endpoints: GET /admin/audit/logs, POST /admin/audit/search, GET /admin/security/alerts, POST /admin/users/{id}/unlock
- [ ] Create tests for lockout behavior, unlock, impersonation events, permission_denied escalation, cross-org alerts

## Followup Steps
- [ ] Create Alembic migration for user lockout fields
- [ ] Update login/auth endpoints to integrate lockout checks and security logging
- [ ] Run tests to ensure no regressions
