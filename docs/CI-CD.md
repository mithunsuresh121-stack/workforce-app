# CI/CD Pipeline Documentation

## Overview

The Workforce App uses GitHub Actions for continuous integration and deployment. Pipelines are triggered on pushes and pull requests to `develop` and `main` branches.

## Branch Strategy

- `main`: Production branch, requires PR approval and CI passing.
- `develop`: Integration branch for features and fixes.
- `feature/*`: Feature branches merged to `develop`.
- `bugfix/*`: Bug fixes merged to `develop`.
- `release/*`: Release candidates merged to `main`.
- `hotfix/*`: Urgent fixes merged to `main`.

## Pipelines

### Backend Tests (`backend-tests.yml`)

- **Trigger**: PRs to `develop` or `main`.
- **Jobs**:
  - Setup Python 3.11
  - Install dependencies from `backend/requirements.txt`
  - Spin up PostgreSQL test DB
  - Run database migrations
  - Run pytest with coverage
  - Lint with ruff

### Frontend-Web Tests (`frontend-tests.yml`)

- **Trigger**: PRs to `develop` or `main`.
- **Jobs**:
  - Setup Node.js 20+
  - Install dependencies (`npm ci`)
  - Run ESLint
  - Run tests (`npm test`)

### Mobile Tests (`mobile-tests.yml`)

- **Trigger**: PRs to `develop` or `main`.
- **Jobs**:
  - Setup Flutter SDK
  - Install dependencies (`flutter pub get`)
  - Run lint (`flutter analyze`)
  - Run unit tests (`flutter test`)
  - Build APK/IPA validation

## Secrets and Environment Variables

Store sensitive data in GitHub Secrets:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `API_KEY`: External API keys

Use `.env.example` files for local development with placeholder values.

## Deployment

- Manual deployment from `main` branch after release.
- Use Docker Compose for staging/production.
- Monitor CI/CD runs for failures and address promptly.
