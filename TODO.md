# Org Analytics + Observability Implementation TODO

## Backend Implementation
- [ ] Create backend/app/services/analytics_service.py with AnalyticsService class and methods for user/channel/meeting/audit stats
- [ ] Create backend/app/routers/admin.py with /api/admin/stats/* endpoints and RBAC dependencies
- [ ] Edit backend/app/main.py to include admin router and enhance middleware for admin action logging and request duration
- [ ] Edit backend/app/services/audit_service.py to add log_admin_action method
- [ ] Create backend/tests/test_analytics.py with pytest suite for service methods and endpoints

## Frontend Implementation
- [ ] Create frontend-web/src/pages/admin/analytics.tsx for the analytics route page
- [ ] Create frontend-web/src/components/OrgAnalyticsDashboard.tsx with charts and widgets
- [ ] Edit frontend routing file (App.tsx or routes/index.tsx) to add /admin/analytics route
- [ ] Create frontend unit tests for OrgAnalyticsDashboard component

## Testing and Verification
- [ ] Run backend pytest suite to ensure all tests pass including new analytics tests
- [ ] Run frontend tests to verify component rendering and RBAC gates
- [ ] Test API endpoints with curl/Postman for RBAC scoping and data accuracy
- [ ] Test frontend dashboard for responsive layout, dark-mode compatibility, and API integration
- [ ] Verify observability logging for admin actions and request durations
- [ ] Run full test suite and generate summary report
