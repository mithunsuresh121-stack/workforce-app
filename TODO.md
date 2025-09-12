# TODO: Comprehensive Testing and Fixes for Workforce App

## Backend API Testing
- [ ] Run and verify backend API tests in `backend/test_all_endpoints.py`
- [ ] Add tests for:
  - Task update and delete functionality
  - Calendar, leaves, and shifts endpoints
  - Reports generation endpoints
  - Chat assistant endpoints
  - Employee management beyond basic user operations
- [ ] Investigate and fix any 403 Forbidden and 404 Not Found errors from backend logs

## Frontend UI Testing
- [ ] Run Playwright tests in `frontend-web/web-app/tests/`
- [ ] Verify UI pages:
  - Login
  - Directory (see `directory-screen.spec.ts`)
  - Profile (see `profile-screen.spec.ts` and `ProfileScreen.tsx`)
  - Dashboard
  - Other screens as applicable
- [ ] Fix any UI test failures and console errors
- [ ] Confirm data-testid attributes are present for reliable testing

## Environment and Configuration
- [x] Fix webpack dev server port to 3000 in `webpack.config.cjs`
- [x] Fix Playwright baseURL to http://localhost:3000 in `playwright.config.ts`

## Next Steps
- [ ] Execute backend API tests and analyze results
- [ ] Execute frontend Playwright tests and analyze results
- [ ] Address any bugs, performance issues, or UX problems found
- [ ] Confirm full end-to-end functionality on localhost
