# Local Setup Guide for Workforce App

## Backend Setup

1. Create a virtual environment and activate it:

```bash
python3 -m venv ./venv
source ./venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Set environment variables:

Copy `.env.example` to `.env` and update as needed.

4. Run database migrations:

```bash
alembic upgrade head
```

5. Start the backend server:

```bash
uvicorn backend.app.main:app --reload
```

## Frontend-Web Setup (React)

1. Navigate to frontend-web directory:

```bash
cd frontend-web/web-app
```

2. Install dependencies:

```bash
npm install
```

3. Create `.env` file from `.env.example` and update API URLs.

4. Start the development server:

```bash
npm start
```

## Mobile Setup (Flutter)

1. Navigate to mobile directory:

```bash
cd mobile
```

2. Install dependencies:

```bash
flutter pub get
```

3. Run the app on an emulator or device:

```bash
flutter run
```

## Docker Setup (Optional)

Run all services with Docker Compose:

```bash
cp .env.example .env
docker compose up --build
```

## Notes

- Ensure you have Python 3.11+, Node.js 20+, Flutter SDK installed.
- Update `.env` files with correct secrets and API URLs.
