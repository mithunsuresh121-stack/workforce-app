#!/usr/bin/env bash
set -euo pipefail
# Ensure we run from the backend directory
cd "$(dirname "$0")"
# Ensure app package is on sys.path when Alembic runs
export PYTHONPATH="$PWD"
echo "PYTHONPATH=$PYTHONPATH"
# Write full alembic output to migration.log
echo "=== alembic current ===" > migration.log 2>&1 || true
python -m alembic current  >> migration.log 2>&1 || true
echo "=== alembic upgrade head ===" >> migration.log 2>&1
python -m alembic upgrade head  >> migration.log 2>&1 || true
echo "=== DONE ===" >> migration.log 2>&1
