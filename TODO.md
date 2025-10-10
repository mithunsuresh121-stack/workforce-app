# Phase 4 Verification TODO

## Backend Verification
- [ ] Confirm endpoints /dashboard/attendance, /leaves, /overtime, /payroll return correct aggregated data.
- [ ] Test role-based access: managers see full analytics, employees denied (403).
- [ ] Validate CSV export endpoints /dashboard/export/{type}: files download, correct headers, match DB data.
- [ ] Run automated tests in tests/test_dashboard_routes.py and report failures/fixtures issues.

## Frontend Verification
- [ ] Ensure Dashboard.jsx charts render: Attendance (line), Leave utilization (pie), Overtime (bar), Payroll (card).
- [ ] Confirm period filter dropdown works and updates charts dynamically.
- [ ] Test export buttons: CSV downloads for each dataset, content matches backend.
- [ ] Verify role-based rendering: managers see analytics + exports, employees only KPIs.

## End-to-End Functional Check
- [ ] Log in as manager: verify data visibility matches role.
- [ ] Log in as employee: verify data visibility matches role.
- [ ] Ensure data fetched matches seeded data (payroll, leaves, attendance, overtime).
- [ ] Check charts/tables/CSVs update correctly with filters.

## Reporting
- [ ] Summarize test coverage, CSV verification, chart rendering, role-based access.
- [ ] Highlight frontend/backend discrepancies or bugs.
- [ ] Confirm Phase 4 fully operational and ready for deployment.
