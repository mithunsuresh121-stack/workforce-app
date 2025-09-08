#!/usr/bin/env bash
# =============================================
# Script: fix_and_validate_tasks.sh
# Purpose: Fix task creation validation workflow by running within the backend
#          context, creating validation tasks for real users, and generating
#          JSON + Markdown reports with robust error handling.
# =============================================

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/backend/venv/bin/activate"
REPORTS_DIR="$SCRIPT_DIR/reports"

# Activate Python virtual environment
if [[ ! -f "$VENV" ]]; then
  echo "[ERROR] Virtualenv not found at: $VENV" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "$VENV"

# Optional safeguard (warning only)
if [[ "${CONFIRM_FIX:-NO}" != "YES" ]]; then
  echo "[WARN] Running without CONFIRM_FIX=YES. Proceeding in current environment..."
fi

mkdir -p "$REPORTS_DIR"
export REPORTS_DIR

echo "=== Fix & Validate Task Creation Workflow ==="

# Run Python from backend directory so that `app.*` imports resolve
pushd "$SCRIPT_DIR/backend" >/dev/null

python - <<'PYTHON_SCRIPT'
import os, sys, json, traceback, logging
from datetime import datetime
from typing import Any, Dict, List

# Ensure backend package imports work
sys.path.append('.')
# Reduce SQLAlchemy engine log noise
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

from app.db import SessionLocal
from app import crud
from app.models.user import User
from app.models.task import TaskStatus, TaskPriority  # ensure enums available

REPORTS_DIR = os.environ.get("REPORTS_DIR", os.path.abspath(os.path.join("..", "reports")))
os.makedirs(REPORTS_DIR, exist_ok=True)


def with_session(fn):
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return fn(db, *args, **kwargs)
        finally:
            db.close()
    return wrapper


@with_session
def find_test_users(db) -> List[User]:
    """Find up to three users prioritizing roles: SuperAdmin, Manager, Employee."""
    rows: List[User] = db.query(User).filter(User.is_active == True, User.company_id != None).all()
    if not rows:
        return []
    by_role: Dict[str, List[User]] = {}
    for u in rows:
        by_role.setdefault(u.role or "", []).append(u)
    picks: List[User] = []
    for role in ("SuperAdmin", "Manager", "Employee"):
        if by_role.get(role):
            picks.append(by_role[role][0])
    # Fallback to first users if roles not found
    if not picks:
        picks = rows[:3]
    return picks


@with_session
def create_task_for_user(db, assigning_user: User) -> Dict[str, Any]:
    """Create a validation task using CRUD with correct parameter types."""
    try:
        task = crud.create_task(
            db=db,
            assigning_user=assigning_user,
            title=f"Validation Task for {assigning_user.role} @ {datetime.utcnow().isoformat()}",
            description="Validation task created by fix_and_validate_tasks.sh",
            status="Pending",     # let CRUD normalize to enum
            priority="Medium",    # let CRUD normalize to enum
            due_at=None,
            assignee_id=assigning_user.id,
            company_id=assigning_user.company_id or None,
        )
        return {
            "success": True,
            "task_id": task.id,
            "assignee_id": assigning_user.id,
            "company_id": task.company_id,
        }
    except Exception as e:  # capture all exceptions, rollback inside CRUD caller
        try:
            db.rollback()
        except Exception:
            pass
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error": str(e),
            "trace": traceback.format_exc(limit=5),
        }


def main() -> int:
    results: List[Dict[str, Any]] = []

    try:
        users = find_test_users()
    except Exception as e:
        results.append({"success": False, "error_type": type(e).__name__, "error": str(e)})
        users = []

    if not users:
        results.append({"success": False, "error": "No active users with company_id found in database"})
    else:
        for u in users:
            res = create_task_for_user(u)
            results.append({
                "user": {"id": u.id, "email": u.email, "role": u.role, "company_id": u.company_id},
                "result": res,
            })

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(REPORTS_DIR, f"task_validation_{ts}.json")
    md_path = os.path.join(REPORTS_DIR, f"task_validation_{ts}.md")

    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    with open(md_path, "w") as f:
        f.write(f"# Task Creation Validation Report - {ts}\n\n")
        for r in results:
            user = r.get("user", {})
            res = r.get("result", {})
            status = "✅ Success" if res.get("success") else "❌ Failed"
            if user:
                f.write(f"- User: {user.get('email','?')} (role: {user.get('role','?')}, company: {user.get('company_id','?')})\n")
            else:
                f.write(f"- User: Unknown\n")
            f.write(f"  - Result: {status}\n")
            if not res.get("success"):
                f.write(f"  - Error: {res.get('error_type','Exception')}: {res.get('error','')}\n")
        f.write("\nReport generated successfully.\n")

    # Console summary
    successes = sum(1 for r in results if r.get("result", {}).get("success"))
    failures = [r for r in results if not r.get("result", {}).get("success")]
    print(f"Summary: {successes} succeeded, {len(failures)} failed")
    if failures:
        print("Failures:")
        for r in failures:
            u = r.get("user", {})
            re = r.get("result", {})
            print(f"  - {u.get('email', 'Unknown')} ({u.get('role','?')}): {re.get('error_type','Exception')} - {re.get('error','')}")

    print(f"✅ JSON report: {json_path}")
    print(f"✅ Markdown report: {md_path}")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
PYTHON_SCRIPT

popd >/dev/null

echo "=== Workflow Complete ==="