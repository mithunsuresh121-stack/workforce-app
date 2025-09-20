# Dashboard Employee Update - Implementation Plan

## Backend Updates (backend/app/routers/dashboard.py)
- [ ] Add role-checking logic in /dashboard/kpis endpoint
- [ ] Implement employee-specific KPI calculation:
  - [ ] total_tasks → count of tasks assigned to the employee
  - [ ] active_tasks → count of "In Progress" tasks assigned to employee
  - [ ] completed_tasks → count of "Completed" tasks assigned to employee
  - [ ] pending_approvals → count of employee's pending approvals
  - [ ] active_teams → count of teams employee belongs to
- [ ] Keep existing response for Manager, CompanyAdmin, and SuperAdmin roles

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
