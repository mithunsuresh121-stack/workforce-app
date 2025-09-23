# Employee Dashboard Contribution Charts Implementation

## Plan Overview
Replace "Reports & Requests" section with contribution-based charts for Employee role while maintaining existing functionality for other roles.

## Implementation Steps

### Backend Changes
- [x] Add 3 new chart endpoints for Employee role:
  - [x] `/dashboard/charts/contribution/tasks-completed` - Shows tasks completed by employee over time
  - [x] `/dashboard/charts/contribution/tasks-created` - Shows tasks created/assigned by employee
  - [x] `/dashboard/charts/contribution/productivity` - Shows productivity metrics
- [x] Update dashboard router with role-based access control
- [x] Add proper error handling and empty state management

### Frontend Changes
- [x] Update DashboardCharts component to replace "Reports & Requests" with contribution charts
- [x] Add interactivity for chart clicks with proper navigation
- [x] Maintain existing functionality for Manager/CompanyAdmin/SuperAdmin roles
- [x] Handle empty data states gracefully

### Testing
- [ ] Test Employee role functionality
- [ ] Verify other roles (Manager, CompanyAdmin, SuperAdmin) unchanged
- [ ] Test edge cases (no tasks, no teams, mixed status data)
- [ ] Test chart interactivity and navigation

## Files to Modify
- `backend/app/routers/dashboard.py` - Add new contribution endpoints
- `frontend-web/web-app/src/components/DashboardCharts.jsx` - Replace Reports & Requests section
