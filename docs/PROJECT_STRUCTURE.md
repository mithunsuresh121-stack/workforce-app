# Project Structure & Conventions

## Monorepo Overview
This is a monorepo for the Workforce App, containing backend, frontend-web, mobile, and supporting directories.

- `backend/` - FastAPI Python backend
- `frontend-web/` - React web app
- `mobile/` - Flutter mobile app
- `infra/` - Infrastructure and deployment configs (Docker, monitoring)
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `archives/` - Legacy/historical content (do not modify or run without review)
- `mobile/playstore-assets/` - Play Store assets

## Backend Structure (`backend/app/`)
Follows clean architecture layering:
- `routers/` - API endpoints (HTTP routes, validation)
- `services/` - Business logic (orchestration, validation, workflows)
- `crud/` - Database operations (create, read, update, delete)
- `models/` - SQLAlchemy database models
- `schemas/` - Pydantic schemas for API input/output
- `core/` - Core utilities (config, security, deps)
- `tests/` - Unit and integration tests
- `archives/legacy/` - Old code/tests (archived, not used in production)

**Layering Convention**: Routers call services for business logic, services call CRUD for DB access, CRUD interacts with models/schemas.

**Naming Conventions**:
- Files/modules: snake_case (e.g., attendance_service.py)
- Classes: PascalCase (e.g., AttendanceService)
- Functions: snake_case (e.g., get_attendance_report)
- Environment variables: UPPER_SNAKE_CASE (e.g., DATABASE_URL)
- Roles: kebab-case (e.g., hr-manager)

**Logging**: Use Python's logging module. Structure logs as: timestamp - level - module - message. Use structured logging where possible.

**Error Handling**: Raise HTTPExceptions in routers/services. Use custom exceptions in services for business errors.

## Frontend-Web Structure (`frontend-web/src/`)
React app with TypeScript.

- `components/` - Reusable UI components
- `pages/` - Page-level components (routes)
- `services/` - API calls, utilities
- `types/` - TypeScript type definitions
- `config/` - App configuration
- `assets/` - Static assets (images, fonts)
- `contexts/` - React contexts (state management)
- `hooks/` - Custom React hooks
- `features/` - Feature-specific modules (if needed)

**Conventions**:
- Naming: camelCase for files/functions, PascalCase for components
- Env vars: REACT_APP_ prefix
- Logging: console.log for dev, integrate with service like Sentry for prod

## Mobile Structure (`mobile/lib/`)
Flutter app.

- `screens/` - Screen widgets (pages)
- `widgets/` - Reusable widgets
- `services/` - API calls, business logic
- `models/` - Data models
- `config/` - App configuration
- `assets/` - Static assets
- `providers/` - State management (Riverpod/Provider)

**Conventions**:
- Naming: snake_case for files, PascalCase for classes/widgets
- Env vars: Use flutter_dotenv or similar
- Logging: Use print() for dev, logger package for prod

## General Conventions
- **Dependencies**: Local only (venv for Python, nvm for Node, fvm for Flutter). Update requirements.txt/package.json/pubspec.yaml after changes.
- **Formatting**: Black/isort for Python, Prettier/ESLint for JS, dart format for Flutter.
- **Testing**: pytest for backend, npm test for frontend, flutter test for mobile.
- **CI/CD**: Update paths in docker-compose, scripts if moved.
- **Archives**: Do not run archived code. Review before reviving.

For contributions, see CONTRIBUTING.md.
