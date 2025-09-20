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

        # Check user role for role-based dashboard
        user_role = getattr(current_user, "role", "Employee").strip()

        # Employee-specific KPIs
        if user_role == "Employee":
            # Get tasks assigned to this specific employee
            tasks = list_tasks(db, company_id)
            employee_tasks = [
                task for task in tasks
                if getattr(task, "assignee_id", None) == current_user.id
            ]

            # Calculate employee-specific metrics
            total_tasks = len(employee_tasks)
            active_tasks = sum(
                1 for task in employee_tasks
                if (getattr(task, "status", "") or "").strip() == TaskStatus.IN_PROGRESS.value
            )
            completed_tasks = sum(
                1 for task in employee_tasks
                if (getattr(task, "status", "") or "").strip() == TaskStatus.COMPLETED.value
            )

            # Get pending approvals for this employee (if approval system exists)
            # For now, we'll use pending leaves as a proxy for pending approvals
            leaves = list_leaves_by_tenant(db, str(company_id))
            employee_leaves = [
                leave for leave in leaves
                if getattr(leave, "employee_id", None) == current_user.id
            ]
            pending_approvals = sum(
                1 for leave in employee_leaves
                if (getattr(leave, "status", "") or "").strip() == LeaveStatus.PENDING.value
            )

            # Get active teams count (if team system exists)
            # For now, we'll use a placeholder - this would need to be implemented based on team structure
            active_teams = 1  # Placeholder - employee is part of at least their own team/department

            return {
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "pending_approvals": pending_approvals,
                "active_teams": active_teams,
            }

        # Manager, CompanyAdmin, and SuperAdmin - keep existing response
        else:
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
            task_status = getattr(task, "status", None)

            # Determine activity type based on task status
            if task_status == TaskStatus.COMPLETED.value:
                activity_type = "TaskCompleted"
            elif task_status == TaskStatus.IN_PROGRESS.value:
                activity_type = "TaskUpdated"
            else:
                activity_type = "TaskCreated"

            activities.append({
                "type": activity_type,
                "entity_id": getattr(task, "id", None),
                "title": title,
                "description": f"Task '{title}' was {activity_type.replace('Task', '').lower()}",
                "status": task_status,
                "timestamp": getattr(task, "created_at", datetime.min),
                "user": f"User {getattr(task, 'assignee_id', None)}" if getattr(task, "assignee_id", None) else "System",
            })

        # Get recent leaves (last N) - treat as approval requests
        leaves = list_leaves_by_tenant(db, str(company_id))
        recent_leaves = sorted(
            leaves,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )[:limit]

        for leave in recent_leaves:
            leave_type = getattr(leave, "type", "Leave")
            leave_status = getattr(leave, "status", None)

            # Determine activity type based on leave status
            if leave_status == LeaveStatus.PENDING.value:
                activity_type = "ApprovalRequested"
            elif leave_status == LeaveStatus.APPROVED.value:
                activity_type = "ApprovalGranted"
            else:
                activity_type = "ApprovalRejected"

            activities.append({
                "type": activity_type,
                "entity_id": getattr(leave, "id", None),
                "title": f"Leave Request - {leave_type}",
                "description": f"Leave request for {leave_type} was {activity_type.replace('Approval', '').lower()}",
                "status": leave_status,
                "timestamp": getattr(leave, "created_at", datetime.min),
                "user": f"Employee {getattr(leave, 'employee_id', 'N/A')}",
            })

        # Add some sample team activities (placeholder for team system)
        # In a real implementation, this would come from a teams table
        team_activities = [
            {
                "type": "TeamJoined",
                "entity_id": 1,  # Would be actual team ID
                "title": "Team Assignment",
                "description": "You were assigned to Development Team",
                "status": "Active",
                "timestamp": datetime.now(),
                "user": "System",
            }
        ]

        activities.extend(team_activities)

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
        user_role = getattr(current_user, "role", "Employee").strip()

        # Employee-specific: only show their own tasks
        if user_role == "Employee":
            tasks = list_tasks(db, company_id)
            tasks = [
                task for task in tasks
                if getattr(task, "assignee_id", None) == current_user.id
            ]
        else:
            # Manager, CompanyAdmin, SuperAdmin: show all company tasks
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


@router.get("/charts/reports")
def get_reports_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get reports/requests distribution for charts (profile updates, leave requests)
    """
    try:
        company_id = _require_company_id(current_user)
        user_role = getattr(current_user, "role", "Employee").strip()

        # Import the profile update request model
        from ..models.profile_update_request import ProfileUpdateRequest

        # Employee-specific: only show their own requests
        if user_role == "Employee":
            # Get their own profile update requests
            profile_requests = db.query(ProfileUpdateRequest).filter(
                ProfileUpdateRequest.user_id == current_user.id
            ).all()

            # Get their own leave requests
            leaves = list_leaves_by_tenant(db, str(company_id))
            leaves = [
                leave for leave in leaves
                if getattr(leave, "employee_id", None) == current_user.id
            ]
        else:
            # Manager, CompanyAdmin, SuperAdmin: show all company requests
            profile_requests = db.query(ProfileUpdateRequest).filter(
                ProfileUpdateRequest.user_id.in_(
                    db.query(User.id).filter(User.company_id == company_id)
                )
            ).all()

            # Get all leave requests for the company
            leaves = list_leaves_by_tenant(db, str(company_id))

        # Count profile update requests by status
        profile_status_count = {"pending": 0, "approved": 0, "rejected": 0}
        for request in profile_requests:
            status = getattr(request, "status", "pending")
            if status in profile_status_count:
                profile_status_count[status] += 1

        # Count leave requests by status
        leave_status_count = {"Pending": 0, "Approved": 0, "Rejected": 0}
        for leave in leaves:
            status = getattr(leave, "status", "Pending")
            if status in leave_status_count:
                leave_status_count[status] += 1

        # Combine the data for the chart
        # For employees, show their own requests
        # For managers/admins, show company-wide requests
        reports_data = [
            {"name": "Submitted", "value": profile_status_count["pending"] + leave_status_count["Pending"]},
            {"name": "Pending Review", "value": profile_status_count["pending"] + leave_status_count["Pending"]},
            {"name": "Approved", "value": profile_status_count["approved"] + leave_status_count["Approved"]},
            {"name": "Rejected", "value": profile_status_count["rejected"] + leave_status_count["Rejected"]},
        ]

        return reports_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reports data: {str(e)}")


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
