# TODO List for Workforce App - Frontend Fixes (GitHub Issues)

## High Priority - Fix GitHub Issues
### 1. Fix Build Fails Due to Missing Dependencies
- [ ] Run `cd frontend-web/web-app && nvm install && nvm use && npm install` to regenerate package-lock.json for Vite 6/Vitest 3 compatibility.
- [ ] Verify: Run `npm run build` locally; ensure no missing module errors.
- [ ] Update workflow if needed (e.g., add fallback npm install before ci).

### 2. Fix Frontend Tests Fail After Vite 5 Update
- [ ] Edit `src/__tests__/useWebSocketNotifications.test.tsx`: Enhance MockWebSocket to auto-dispatch 'open' after onopen assignment; add act() + timeout in waitFor for connected state.
- [ ] Run `npm test -- --coverage --watch=false`; confirm all tests pass (including WebSocket connection and message handling).
- [ ] Mark WebSocket test fix complete in this TODO.md and update `TODO_integration.md` if exists.

### 3. Verification and Deployment
- [ ] Local full run: `npm ci && npm test -- --coverage --watch=false && npm run build`.
- [ ] Create branch: `git checkout -b blackboxai/fix-frontend-issues`.
- [ ] Commit: `git add . && git commit -m "Fix build deps and WebSocket test failures post-Vite upgrade"`.
- [ ] Push and PR: `git push origin blackboxai/fix-frontend-issues` (use `gh pr create` if GitHub CLI installed).
- [ ] Trigger CI on PR; verify no failures in GitHub Actions logs.
- [ ] Update reports (e.g., reports/test_results_webapp.txt) with pass summary.

## Medium Priority
- [ ] Integrate frontend-backend features
- [ ] Verify API endpoints

## Low Priority
- [ ] Other tasks...

## GitHub Workflow Fixes (High Priority - In Progress)
- [x] Update vite.config.ts: Add Vitest test config for lcov coverage output.
- [x] Update .github/workflows/frontend-tests.yml: Fix test flags to --watch=false, adjust coverage path, streamline e2e.
- [ ] Local verification complete (see steps above).
- [ ] Commit and push changes.
- [ ] If issues persist: Review logs for further code fixes (e.g., add ws polyfill if needed).
