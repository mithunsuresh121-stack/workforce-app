from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from ..deps import get_db, get_current_user
from ..crud import list_users_by_company, list_tasks, list_leaves_by_company, list_shifts_by_company
from ..models.user import User
from ..models.task import TaskStatus
from ..schemas.schemas import LeaveStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _require_company_id(user: User) -> int | None:
    """
    Get company_id for the user. Returns None for SuperAdmin (global access).
    Raises 400 for users without company who are not SuperAdmin.
    """
    if user.company_id is None:
        if getattr(user, "role", "").value == "SuperAdmin":
            return None  # SuperAdmin can access all
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

        # SuperAdmin: return global stats or zeros for Phase 1
        if company_id is None:
            return {
                "total_employees": 0,
                "active_tasks": 0,
                "pending_leaves": 0,
                "shifts_today": 0,
            }

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
            leaves = list_leaves_by_company(db, company_id)
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
            leaves = list_leaves_by_company(db, company_id)
            pending_leaves = sum(
                1
                for leave in leaves
                if (getattr(leave, "status", "") or "").strip() == LeaveStatus.PENDING.value
            )

            # Get shifts for today
            today = date.today()
            shifts = list_shifts_by_company(db, company_id)
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

        # SuperAdmin: return empty for Phase 1
        if company_id is None:
            return []

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
        leaves = list_leaves_by_company(db, company_id)
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

        # SuperAdmin: stub for Phase 1
        if company_id is None:
            return [
                {"name": "Pending", "value": 0},
                {"name": "In Progress", "value": 0},
                {"name": "Completed", "value": 0},
                {"name": "Overdue", "value": 0},
            ]

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

        # SuperAdmin: stub for Phase 1
        if company_id is None:
            return [
                {"name": "Submitted", "value": 0},
                {"name": "Pending Review", "value": 0},
                {"name": "Approved", "value": 0},
                {"name": "Rejected", "value": 0},
            ]

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
            leaves = list_leaves_by_company(db, company_id)
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
            leaves = list_leaves_by_company(db, company_id)

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

        # SuperAdmin: stub for Phase 1
        if company_id is None:
            return [
                {"name": "Super Admin", "value": 0},
                {"name": "Company Admin", "value": 0},
                {"name": "Manager", "value": 0},
                {"name": "Employee", "value": 0},
            ]

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


@router.get("/charts/contribution/tasks-completed")
def get_tasks_completed_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tasks completed by the employee over time for contribution charts
    """
    try:
        company_id = _require_company_id(current_user)
        user_role = getattr(current_user, "role", "Employee").strip()

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is for employees only.")

        from datetime import datetime, timedelta

        # Get tasks completed by this employee
        tasks = list_tasks(db, company_id)
        employee_tasks = [
            task for task in tasks
            if getattr(task, "assignee_id", None) == current_user.id
        ]

        # Group by completion status and time periods
        completed_tasks = [
            task for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.COMPLETED.value
        ]

        # Group by time periods (last 30 days, 30-60 days, 60-90 days, older)
        now = datetime.now()
        time_periods = {
            "Last 7 days": timedelta(days=7),
            "Last 30 days": timedelta(days=30),
            "Last 90 days": timedelta(days=90),
            "Older": None
        }

        time_data = {period: 0 for period in time_periods.keys()}

        for task in completed_tasks:
            updated_at = getattr(task, "updated_at", None)
            if updated_at:
                if now - updated_at <= time_periods["Last 7 days"]:
                    time_data["Last 7 days"] += 1
                elif now - updated_at <= time_periods["Last 30 days"]:
                    time_data["Last 30 days"] += 1
                elif now - updated_at <= time_periods["Last 90 days"]:
                    time_data["Last 90 days"] += 1
                else:
                    time_data["Older"] += 1

        return [
            {"name": "Last 7 days", "value": time_data["Last 7 days"]},
            {"name": "Last 30 days", "value": time_data["Last 30 days"]},
            {"name": "Last 90 days", "value": time_data["Last 90 days"]},
            {"name": "Older", "value": time_data["Older"]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks completed data: {str(e)}")


@router.get("/charts/contribution/tasks-created")
def get_tasks_created_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get tasks created/assigned by the employee for contribution charts
    """
    try:
        company_id = _require_company_id(current_user)
        user_role = getattr(current_user, "role", "Employee").strip()

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is for employees only.")

        # Get tasks created by this employee
        tasks = list_tasks(db, company_id)
        created_tasks = [
            task for task in tasks
            if getattr(task, "assigned_by", None) == current_user.id
        ]

        # Group by status
        status_data = {s.value: 0 for s in TaskStatus}

        for task in created_tasks:
            s = (getattr(task, "status", "") or "").strip()
            if s in status_data:
                status_data[s] += 1

        return [
            {"name": "Pending", "value": status_data["Pending"]},
            {"name": "In Progress", "value": status_data["In Progress"]},
            {"name": "Completed", "value": status_data["Completed"]},
            {"name": "Overdue", "value": status_data["Overdue"]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks created data: {str(e)}")


@router.get("/charts/contribution/productivity")
def get_productivity_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get productivity metrics for the employee for contribution charts
    """
    try:
        company_id = _require_company_id(current_user)
        user_role = getattr(current_user, "role", "Employee").strip()

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(status_code=403, detail="Access denied. This endpoint is for employees only.")

        # Get tasks assigned to this employee
        tasks = list_tasks(db, company_id)
        employee_tasks = [
            task for task in tasks
            if getattr(task, "assignee_id", None) == current_user.id
        ]

        total_tasks = len(employee_tasks)
        if total_tasks == 0:
            return [
                {"name": "No Tasks", "value": 1}
            ]

        # Calculate productivity metrics
        completed_tasks = sum(
            1 for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.COMPLETED.value
        )

        in_progress_tasks = sum(
            1 for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.IN_PROGRESS.value
        )

        pending_tasks = sum(
            1 for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.PENDING.value
        )

        overdue_tasks = sum(
            1 for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.OVERDUE.value
        )

        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        return [
            {"name": "Completed", "value": completed_tasks},
            {"name": "In Progress", "value": in_progress_tasks},
            {"name": "Pending", "value": pending_tasks},
            {"name": "Overdue", "value": overdue_tasks},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching productivity data: {str(e)}")
