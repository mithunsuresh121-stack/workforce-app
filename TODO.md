# Cleanup and Refactor TODO List

## Step 1: Deletions (Approved)
- [ ] Delete log/output files: backend_server.log, backend/backend.log, backend/pytest*.log, test_output*.json/log, migration.log, backend/logs/ contents
- [ ] Delete sensitive temp files: cookies*.txt, token*.txt, fresh_token.txt
- [ ] Delete temp DBs: backend/test.db, backend/test_timestamp.db, backend/test_cascade.db
- [ ] Delete build/coverage outputs: mobile/build/, backend/.coverage, test-results/
- [ ] Delete backups/archives/junk: frontend-web/src_backup_20250914170130/, workforce-app-complete/, 极ntend/, frontend-web/src极速赛车* paths
- [ ] Delete duplicate mains/seeds: backend/app/main_final.py, backend/app/main_fixed.py, backend/seed_demo_user_final.py, backend/seed_demo_user_fixed.py
- [ ] Check and delete one-off scripts (add_*.py, create_*.py, check_*.py, reset_*.py, seed_*.py) if not referenced (confirm seed_demo_user.py is used in main.py startup)
- [ ] Move legacy test scripts (test_all_endpoints.py, etc.) to backend/archive_tests/ folder

## Step 2: Refactors (Proposed)
- [ ] Refactor backend/app/main.py: Remove unused imports (duplicate structlog processors, unused get_db), split log_requests into helpers (extract_user_id, log_admin_action), consistent style (quotes, line lengths), remove redundant processors
- [ ] Check backend/app/routers/ and schemas/ for naming consistency, unused imports/variables, commented code
- [ ] Apply consistent code style across backend (PEP8: imports, naming, formatting)
- [ ] Remove unused imports/variables in core files (e.g., main.py, routers/auth.py, schemas/schemas.py)
- [ ] Split long functions if any (e.g., in routers or services)
- [ ] Verify no dynamic imports or runtime refs before deletions

## Step 3: Verification
- [ ] Run backend build/test: cd backend && python -m pytest (or equivalent)
- [ ] Run mobile build: cd mobile && flutter build apk
- [ ] Run web build: cd frontend-web/web-app && npm run build
- [ ] Check for broken refs after deletions
- [ ] Archive important reports/TODOs if needed

## Notes
- Prioritize safety: No business logic changes.
- If risky, ask for confirmation.
- Update this TODO after each step.
