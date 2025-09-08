from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from ..deps import get_db, get_current_user
from ..crud import list_users_by_company, list_tasks, list_leaves_by_tenant, list_shifts_by_tenant
from ..models.user import User
from ..models.task import TaskStatus
from ..schemas.schemas import LeaveStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _require_company_id(user: User) -> int:
    """
    Ensure the current user is associated with a company.
    SuperAdmin or users without company cannot fetch company-scoped dashboards.
    """
    if user.company_id is None:
        raise HTTPException(status_code=400, detail="User is not associated with a company")
    return user.company_id


@router.get("/kpis")
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard KPIs for the current user's company
    """
    try:
        company_id = _require_company_id(current_user)

        # Get total employees
        employees = list_users_by_company(db, company_id)
        total_employees = len(employees)

        # Get active tasks (tasks that are not completed)
        tasks = list_tasks(db, company_id)
        active_tasks = sum(
            1
            for task in tasks
            if (getattr(task, "status", "") or "").strip() != TaskStatus.COMPLETED.value
        )

        # Get pending leave requests
        # list_leaves_by_tenant uses tenant_id as str; company_id is int
        leaves = list_leaves_by_tenant(db, str(company_id))
        pending_leaves = sum(
            1
            for leave in leaves
            if (getattr(leave, "status", "") or "").strip() == LeaveStatus.PENDING.value
        )

        # Get shifts for today
        today = date.today()
        shifts = list_shifts_by_tenant(db, str(company_id))
        shifts_today = 0
        for shift in shifts:
            start = getattr(shift, "start_at", None)
            end = getattr(shift, "end_at", None)
            if (start and start.date() == today) or (end and end.date() == today):
                shifts_today += 1

        return {
            "total_employees": total_employees,
            "active_tasks": active_tasks,
            "pending_leaves": pending_leaves,
            "shifts_today": shifts_today,
        }

    except HTTPException:
        # Re-raise known client errors untouched
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")


@router.get("/recent-activities")
def get_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """
    Get recent activities for the dashboard feed
    """
    try:
        company_id = _require_company_id(current_user)
        activities = []

        # Get recent tasks (last N)
        tasks = list_tasks(db, company_id)
        recent_tasks = sorted(
            tasks,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )[:limit]

        for task in recent_tasks:
            title = getattr(task, "title", None) or f"Task #{getattr(task, 'id', 'N/A')}"
            activities.append({
                "type": "task",
                "id": getattr(task, "id", None),
                "title": title,
                "description": f"Task '{title}' was created",
                "status": getattr(task, "status", None),
                "timestamp": getattr(task, "created_at", datetime.min),
                "user": f"User {getattr(task, 'assignee_id', None)}" if getattr(task, "assignee_id", None) else "System",
            })

        # Get recent leaves (last N)
        leaves = list_leaves_by_tenant(db, str(company_id))
        recent_leaves = sorted(
            leaves,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )[:limit]

        for leave in recent_leaves:
            leave_type = getattr(leave, "type", "Leave")
            start_at = getattr(leave, "start_at", None)
            end_at = getattr(leave, "end_at", None)
            activities.append({
                "type": "leave",
                "id": getattr(leave, "id", None),
                "title": f"Leave Request - {leave_type}",
                "description": f"Leave request for {leave_type} from {start_at} to {end_at}",
                "status": getattr(leave, "status", None),
                "timestamp": getattr(leave, "created_at", datetime.min),
                "user": f"Employee {getattr(leave, 'employee_id', 'N/A')}",
            })

        # Sort all activities by timestamp and return limited results
        sorted_activities = sorted(activities, key=lambda x: x["timestamp"], reverse=True)[:limit]
        return sorted_activities

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent activities: {str(e)}")


@router.get("/charts/task-status")
def get_task_status_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get task status distribution for charts
    """
    try:
        company_id = _require_company_id(current_user)
        tasks = list_tasks(db, company_id)

        # Initialize counts from enum values to avoid typos
        status_count = {s.value: 0 for s in TaskStatus}

        for task in tasks:
            s = (getattr(task, "status", "") or "").strip()
            if s in status_count:
                status_count[s] += 1
            # Unknown statuses are ignored; alternatively map them to "Pending" or a catch-all

        return [
            {"name": "Pending", "value": status_count["Pending"]},
            {"name": "In Progress", "value": status_count["In Progress"]},
            {"name": "Completed", "value": status_count["Completed"]},
            {"name": "Overdue", "value": status_count["Overdue"]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching task status data: {str(e)}")


@router.get("/charts/employee-distribution")
def get_employee_distribution_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get employee role distribution for charts
    """
    try:
        company_id = _require_company_id(current_user)
        employees = list_users_by_company(db, company_id)

        role_count = {
            "SuperAdmin": 0,
            "CompanyAdmin": 0,
            "Manager": 0,
            "Employee": 0,
        }

        for employee in employees:
            role = (getattr(employee, "role", "") or "Employee").strip()
            if role not in role_count:
                role = "Employee"
            role_count[role] += 1

        return [
            {"name": "Super Admin", "value": role_count["SuperAdmin"]},
            {"name": "Company Admin", "value": role_count["CompanyAdmin"]},
            {"name": "Manager", "value": role_count["Manager"]},
            {"name": "Employee", "value": role_count["Employee"]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching employee distribution data: {str(e)}")
