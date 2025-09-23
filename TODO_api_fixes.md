# API Fixes TODO

## Issues to Fix:
1. **404 Error on `/api/users`**: Frontend Directory calls `/users` but backend has `/api/employees`
2. **500 Error on `/api/profile/me`**: Missing employee profile data for users
3. **Database Issues**: Missing employee profiles for demo users

## Plan Implementation:

### Step 1: Fix Directory API call
- [ ] Update `frontend-web/web-app/src/pages/Directory.jsx` to use `/api/employees` instead of `/users`

### Step 2: Add users endpoint for backward compatibility
- [ ] Create `backend/app/routers/users.py` with `/api/users` endpoint
- [ ] Update `backend/app/main.py` to include users router

### Step 3: Fix profile issues
- [ ] Update `backend/app/routers/profile.py` to handle missing profiles gracefully
- [ ] Update `backend/app/seed_demo_user.py` to ensure employee profiles are created

### Step 4: Test fixes
- [ ] Test Directory page loads employee data
- [ ] Test Profile page loads user profile data
- [ ] Verify both endpoints return proper data

## Current Status:
- [ ] Step 1: Fix Directory API call
- [ ] Step 2: Add users endpoint
- [ ] Step 3: Fix profile issues
- [ ] Step 4: Test fixes
