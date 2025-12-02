# Automated Progress Tracker for Leave & Shift Management
import json
import os

tasks = [
    # Phase 1 – Flutter Mobile Implementation
    "Create leave_management_screen.dart with form, list view, approval/rejection UI",
    "Create shift_management_screen.dart with shift scheduling form, list view, management UI",
    "Implement state management in leaves_provider.dart and shifts_provider.dart",
    "Update api_service.dart to include API functions for leaves and shifts",
    "Update app.dart to include routes and navigation",
    # Phase 2 – Flutter Mobile Testing
    "Write widget/integration tests for leave management",
    "Write widget/integration tests for shift management",
    "Test role-based visibility, approval/rejection workflows, and data persistence",
    # Phase 3 – Frontend Web Testing
    "Write Playwright tests for leave management",
    "Write Playwright tests for shift management",
    "Test forms, list views, approval/rejection workflows, and role-based access",
    # Phase 4 – Backend Testing
    "Ensure pytest scripts cover CRUD, role-based access, edge cases, and error handling",
    "Validate timestamp tracking, status values, and multi-tenant isolation",
    # Phase 5 – CI/CD Integration
    "Update GitHub Actions workflows to include backend and frontend tests",
    "Run full CI/CD pipeline and confirm all tests pass",
    # Phase 6 – Reporting & Sign-Off
    "Summarize test results across backend, web, and mobile",
    "Confirm Leave and Shift Management features are fully integrated, production-ready, and role-compliant",
]

PROGRESS_FILE = "progress_status.json"


def load_progress():
    """Load progress from file if it exists"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {task: "Pending" for task in tasks}


def save_progress(progress):
    """Save progress to file"""
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        print(f"Error saving progress: {e}")


# Dictionary to track status
progress = load_progress()


def mark_done(task_name):
    if task_name in progress:
        progress[task_name] = "Completed"
        save_progress(progress)
    else:
        print(f"Task '{task_name}' not found in checklist.")


def mark_skipped(task_name):
    if task_name in progress:
        progress[task_name] = "Skipped"
        save_progress(progress)
    else:
        print(f"Task '{task_name}' not found in checklist.")


def print_progress():
    print("\n--- Leave & Shift Management Progress Tracker ---")
    for i, task in enumerate(tasks, 1):
        status = progress[task]
        print(f"{i}. [{status}] {task}")
    completed = sum(1 for s in progress.values() if s == "Completed")
    total = len(tasks)
    print(
        f"\nProgress: {completed}/{total} tasks completed ({completed/total*100:.1f}%)\n"
    )


# Example usage:
# mark_done("Create leave_management_screen.dart with form, list view, approval/rejection UI")
# print_progress()
