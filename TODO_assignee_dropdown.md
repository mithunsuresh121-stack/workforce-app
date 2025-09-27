# Assignee Dropdown for Task Creation

## Backend Updates
- [x] Endpoint /api/users/employees exists (GET, returns employees with id, name, email, filtered by role=="Employee")
- [x] Schema EmployeeUserOut exists (id: int, name: str, email: str)
- [ ] Minor: Update users.py for SuperAdmin handling (return all employees if SuperAdmin)
- [ ] Test endpoint with manager login

## Frontend Updates (Tasks.jsx)
- [ ] Add state for employees and currentUser
- [ ] Add useEffect to fetch current user (/auth/me)
- [ ] Add useEffect to fetch employees if role allows
- [ ] Replace assignee input with conditional select dropdown
- [ ] Update formData to use assignee_id (null)
- [ ] Update handleSaveTask for assignee_id, validation, permissions
- [ ] Add validation to disable submit if assignee_id empty for managers
- [ ] Test dropdown renders, submits correctly, hidden for employees

## Testing
- [ ] Backend: Verify /users/employees returns employees only
- [ ] Frontend: Dropdown with API data, submit assigns selected employee
- [ ] Permissions: Hidden for employees, required for managers
