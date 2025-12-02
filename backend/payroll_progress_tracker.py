# Payroll & Compensation Progress Tracker

tasks = {
    1: "Create backend models & schemas for payroll",
    2: "Implement backend CRUD endpoints",
    3: "Write backend pytest tests for payroll",
    4: "Create web PayrollManagementScreen with API integration",
    5: "Write Playwright tests for web payroll screens",
    6: "Create mobile PayrollManagementScreen with providers",
    7: "Write Flutter widget/integration tests for payroll",
    8: "Summarize test results and confirm production readiness",
}

progress = {key: False for key in tasks}


def mark_done(task_name: str):
    found = False
    for key, value in tasks.items():
        if value == task_name:
            progress[key] = True
            found = True
            print(f"Task completed: {task_name}")
            break
    if not found:
        print(f"Task not found: {task_name}")


def print_progress():
    total = len(tasks)
    completed = sum(progress.values())
    percentage = (completed / total) * 100
    print("\n--- Payroll & Compensation Progress ---")
    for key, value in tasks.items():
        status = "✅" if progress[key] else "❌"
        print(f"{status} {value}")
    print(f"Progress: {completed}/{total} tasks completed ({percentage:.1f}%)\n")
