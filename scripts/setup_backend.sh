#!/bin/bash

set -e

echo "=== Installing/Starting PostgreSQL ==="
brew install postgresql@14 || echo "Postgres already installed"
brew services start postgresql@14

export PATH="/usr/local/opt/postgresql@14/bin:$PATH"

# Initialize Postgres cluster if not already done
if [ ! -d "/usr/local/var/postgresql@14" ]; then
    echo "Initializing Postgres cluster..."
    initdb --locale=C -E UTF-8 /usr/local/var/postgresql@14
fi

# Start Postgres manually if brew service isn't working
pg_ctl -D /usr/local/var/postgresql@14 start || true

# Wait a few seconds for Postgres to start
sleep 3

echo "=== Creating Database ==="
createdb workforce_app_db || echo "Database already exists"

echo "=== Setting up Python venv ==="
# Ensure you are in the project root
cd "$(dirname "$0")"

# Remove existing venv if you want a fresh start
# rm -rf venv

python3 -m venv venv
source venv/bin/activate

echo "=== Upgrading pip and installing dependencies ==="
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "=== Initializing Database ==="
cd backend
python init_db.py

echo "=== Running FastAPI backend ==="
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
