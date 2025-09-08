# TODO for Preparing Workforce App for GitHub

## Repo Restructuring
- [x] Create `mobile/` and move `frontend/` (Flutter mobile) there
- [x] Create `frontend-web/` and move `frontend/web-app/` (React web) there
- [x] Move loose test scripts (test_*.py) to `tests/`
- [x] Move loose utility scripts (check_*.py, add_*.py, etc.) to `scripts/`
- [x] Create `.github/workflows/` and move/update CI files from `ci-cd/`

## Branching Strategy & Documentation
- [ ] Create `CONTRIBUTING.md` with Git Flow branching and commit conventions
- [ ] Update root `README.md` with project overview
- [ ] Create `docs/SETUP.md` for local setup instructions
- [ ] Create `docs/CI-CD.md` explaining pipelines, branch strategy, secrets
- [ ] Create `docs/DEPLOYMENT.md` for staging/prod deployment guide

## GitHub Actions (CI/CD Pipelines)
- [ ] Update `backend-tests.yml` with PostgreSQL service, migrations, coverage
- [ ] Create `frontend-tests.yml` for React web app linting and tests
- [ ] Create `mobile-tests.yml` for Flutter linting, tests, and build validation
- [ ] Create `.github/dependabot.yml` for dependency updates

## Code Quality & Security
- [ ] Create `.pre-commit-config.yaml` with black, flake8, isort
- [ ] Create `.eslintrc.json` and `.prettierrc` for frontend-web
- [ ] Create `.github/CODEOWNERS` to require PR reviews
- [ ] Create `.env.example` files for backend, frontend-web, and mobile

## Verification
- [ ] Verify final repo structure matches requirements
- [ ] Verify all references and paths updated accordingly
