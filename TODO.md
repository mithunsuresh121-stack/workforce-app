# Project Reorganization Plan

## Monorepo-Level Reorganization
- [ ] Create `infra/` directory
- [ ] Move infrastructure files to `infra/`: docker-compose.yml, docker-compose-grafana.yml, grafana/, prometheus.yml, k8s-redis-cluster.yaml, redis.conf
- [ ] Create `scripts/` directory
- [ ] Move utility scripts to `scripts/`: blackbox-*.sh, check_and_download.sh, cleanup_actions.sh, download_apk.sh, push_script.sh, run_*.sh, websocket_simulation.py
- [ ] Create `archives/` directory
- [ ] Move legacy content to `archives/`: all TODO_*.md files, reports/, ATTENDANCE_SYSTEM_STATUS_REPORT.md, backend_readiness_report.md, IMPLEMENTATION_STATUS_REPORT_PHASE_8.md, integration_readiness_report.md, LEAVE_SHIFT_MANAGEMENT_SUMMARY.md, real_time_readiness_report.md, STAGING_DEPLOYMENT_VALIDATION_CHECKLIST.md
- [ ] Move `playstore-assets/` under `mobile/`

## Backend Reorganization
- [ ] Move `backend/tests/` to `backend/app/tests/`
- [ ] Move `backend/archive_tests/` to `backend/app/archives/legacy_tests/`
- [ ] Update test imports and pytest configuration
- [ ] Review and refactor routers/services/crud for clean layering and grouping (attendance, payroll, etc.)

## Frontend-Web Reorganization
- [ ] Inspect `frontend-web/web/` and `frontend-web/web-app/` to determine active app
- [ ] Move active app to `frontend-web/src/` with structure: components/, pages/, services/, types/, config/, assets/
- [ ] Archive unused app to `archives/frontend-legacy/`
- [ ] Update imports and build configs

## Mobile Reorganization
- [ ] Move junk folders like `src极速赛车开奖直播历史记录+开奖结果` to `archives/mobile-junk/`
- [ ] Organize `mobile/lib/src/` into: screens/, widgets/, services/, models/, config/
- [ ] Move `mobile/assets/` to `mobile/lib/assets/` if needed
- [ ] Update pubspec.yaml and imports

## General Updates
- [ ] Update all import statements across the project
- [ ] Update CI/docker-compose references to new paths
- [ ] Create `docs/PROJECT_STRUCTURE.md` with structure and conventions
- [ ] Run backend tests (pytest)
- [ ] Run Flutter analyze and build
- [ ] Run React lint, test, and build
- [ ] Verify no broken imports or builds
