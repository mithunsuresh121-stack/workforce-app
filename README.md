# Workforce App (Flutter + FastAPI + React)

## Project Overview

Workforce App is a comprehensive workforce management system built with a Flutter mobile app, FastAPI backend, and React web frontend.

## Features

- Employee attendance tracking
- Leave and shift management
- Payroll processing
- Role-based access control
- Notifications and alerts

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+
- Node.js 20+
- Flutter SDK

### Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- Backend API docs: http://localhost:8000/docs
- Flutter Frontend (web/dev): http://localhost:5173
- React Web App: http://localhost:8080

### Local Development

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend-Web

```bash
cd frontend-web/web-app
npm install
npm start
```

#### Mobile (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

## Repository Structure

- `backend/`: FastAPI backend code
- `frontend-web/`: React web app
- `mobile/`: Flutter mobile app
- `docs/`: Documentation
- `scripts/`: Utility scripts
- `tests/`: Test suites
- `.github/workflows/`: GitHub Actions CI/CD pipelines

## Environment Variables

Use `.env` files for local development. See `.env.example` for placeholders.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License
