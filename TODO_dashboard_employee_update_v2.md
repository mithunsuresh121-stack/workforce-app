# Dashboard Employee Update - Implementation Plan

## Backend Updates (backend/app/routers/dashboard.py)
- [x] Add role-checking logic in /dashboard/kpis endpoint
- [x] Implement employee-specific KPI calculation:
  - [x] total_tasks → count of tasks assigned to the employee
  - [x] active_tasks → count of "In Progress" tasks assigned to employee
  - [x] completed_tasks → count of "Completed" tasks assigned to employee
  - [x] pending_approvals → count of employee's pending approvals
  - [x] active_teams → count of teams employee belongs to
- [x] Keep existing response for Manager, CompanyAdmin, and SuperAdmin roles

## Frontend Updates (frontend-web/web-app/src/pages/Dashboard.jsx)
- [ ] Add role-based rendering using auth context
- [ ] Implement employee dashboard with 5 KPI cards
- [ ] Add clickable card functionality with navigation
- [ ] Handle null/empty states gracefully
- [ ] Ensure Material Tailwind styling and responsiveness

## Navigation & Routing
- [ ] Check if /teams route exists, otherwise use /directory as fallback
- [ ] Implement useNavigate for card click handling
- [ ] Test all redirect paths

## Testing
- [ ] Test employee user flow
- [ ] Test other roles remain unchanged
- [ ] Test edge cases (no data, null responses)
- [ ] Verify responsiveness
