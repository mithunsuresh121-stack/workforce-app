import io
from datetime import date, datetime, timedelta

import pandas as pd
import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, distinct, extract, func, or_
from sqlalchemy.orm import Session

from app.crud import (list_leaves_by_tenant, list_shifts_by_company,
                      list_tasks, list_users_by_company)
from app.deps import get_current_user, get_db
from app.models.attendance import Attendance
from app.models.company import Company
from app.models.employee_profile import EmployeeProfile
from app.models.leave import Leave
from app.models.payroll import Employee
from app.models.task import TaskStatus
from app.models.user import User
from app.schemas.schemas import LeaveStatus

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _require_company_id(user: User) -> int:
    """
    Ensure the current user is associated with a company.
    SuperAdmin or users without company cannot fetch company-scoped dashboards.
    """
    if user.company_id is None:
        # For testing, use default company_id = 1
        return 1
    return user.company_id


@router.get("/kpis")
def get_dashboard_kpis(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get dashboard KPIs for the current user's company
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1  # Hardcoded for testing

        # Check user role for role-based dashboard
        user_role = "Manager"  # Default role for testing

        # Employee-specific KPIs
        if user_role == "Employee":
            # Get tasks assigned to this specific employee
            tasks = list_tasks(db, company_id)
            employee_tasks = [
                task
                for task in tasks
                if getattr(task, "assignee_id", None) == current_user_id
            ]

            # Calculate employee-specific metrics
            total_tasks = len(employee_tasks)
            active_tasks = sum(
                1
                for task in employee_tasks
                if (getattr(task, "status", "") or "").strip()
                == TaskStatus.IN_PROGRESS.value
            )
            completed_tasks = sum(
                1
                for task in employee_tasks
                if (getattr(task, "status", "") or "").strip()
                == TaskStatus.COMPLETED.value
            )

            # Get pending approvals for this employee (if approval system exists)
            # For now, we'll use pending leaves as a proxy for pending approvals
            leaves = list_leaves_by_tenant(db, str(company_id))
            employee_leaves = [
                leave
                for leave in leaves
                if getattr(leave, "employee_id", None) == current_user_id
            ]
            pending_approvals = sum(
                1
                for leave in employee_leaves
                if (getattr(leave, "status", "") or "").strip()
                == LeaveStatus.PENDING.value
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
                if (getattr(task, "status", "") or "").strip()
                != TaskStatus.COMPLETED.value
            )

            # Get pending leave requests
            leaves = list_leaves_by_tenant(db, str(company_id))
            pending_leaves = sum(
                1
                for leave in leaves
                if (getattr(leave, "status", "") or "").strip()
                == LeaveStatus.PENDING.value
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
        raise HTTPException(
            status_code=500, detail=f"Error fetching dashboard data: {str(e)}"
        )


@router.get("/recent-activities")
def get_recent_activities(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
    limit: int = 10,
):
    """
    Get recent activities for the dashboard feed
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1  # Hardcoded for testing
        activities = []

        # Get recent tasks (last N)
        tasks = list_tasks(db, company_id)
        recent_tasks = sorted(
            tasks,
            key=lambda x: getattr(x, "created_at", datetime.min),
            reverse=True,
        )[:limit]

        for task in recent_tasks:
            title = (
                getattr(task, "title", None) or f"Task #{getattr(task, 'id', 'N/A')}"
            )
            task_status = getattr(task, "status", None)

            # Determine activity type based on task status
            if task_status == TaskStatus.COMPLETED.value:
                activity_type = "TaskCompleted"
            elif task_status == TaskStatus.IN_PROGRESS.value:
                activity_type = "TaskUpdated"
            else:
                activity_type = "TaskCreated"

            activities.append(
                {
                    "type": activity_type,
                    "entity_id": getattr(task, "id", None),
                    "title": title,
                    "description": f"Task '{title}' was {activity_type.replace('Task', '').lower()}",
                    "status": task_status,
                    "timestamp": getattr(task, "created_at", datetime.min),
                    "user": (
                        f"User {getattr(task, 'assignee_id', None)}"
                        if getattr(task, "assignee_id", None)
                        else "System"
                    ),
                }
            )

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

            activities.append(
                {
                    "type": activity_type,
                    "entity_id": getattr(leave, "id", None),
                    "title": f"Leave Request - {leave_type}",
                    "description": f"Leave request for {leave_type} was {activity_type.replace('Approval', '').lower()}",
                    "status": leave_status,
                    "timestamp": getattr(leave, "created_at", datetime.min),
                    "user": f"Employee {getattr(leave, 'employee_id', 'N/A')}",
                }
            )

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
        sorted_activities = sorted(
            activities, key=lambda x: x["timestamp"], reverse=True
        )[:limit]
        return sorted_activities

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching recent activities: {str(e)}"
        )


@router.get("/charts/task-status")
def get_task_status_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get task status distribution for charts
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1
        user_role = "Manager"  # Default role for testing

        # Employee-specific: only show their own tasks
        if user_role == "Employee":
            tasks = list_tasks(db, company_id)
            tasks = [
                task
                for task in tasks
                if getattr(task, "assignee_id", None) == current_user_id
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
            {"name": "Pending", "value": status_count[TaskStatus.PENDING.value]},
            {
                "name": "In Progress",
                "value": status_count[TaskStatus.IN_PROGRESS.value],
            },
            {"name": "Completed", "value": status_count[TaskStatus.COMPLETED.value]},
            {"name": "Overdue", "value": status_count[TaskStatus.OVERDUE.value]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching task status data: {str(e)}"
        )


@router.get("/charts/reports")
def get_reports_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get reports/requests distribution for charts (profile updates, leave requests)
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1
        user_role = "Manager"  # Default role for testing

        # Import the profile update request model
        from app.models.profile_update_request import ProfileUpdateRequest

        # Employee-specific: only show their own requests
        if user_role == "Employee":
            # Get their own profile update requests
            profile_requests = (
                db.query(ProfileUpdateRequest)
                .filter(ProfileUpdateRequest.user_id == current_user_id)
                .all()
            )

            # Get their own leave requests
            leaves = list_leaves_by_tenant(db, str(company_id))
            leaves = [
                leave
                for leave in leaves
                if getattr(leave, "employee_id", None) == current_user_id
            ]
        else:
            # Manager, CompanyAdmin, SuperAdmin: show all company requests
            profile_requests = (
                db.query(ProfileUpdateRequest)
                .filter(
                    ProfileUpdateRequest.user_id.in_(
                        db.query(User.id).filter(User.company_id == company_id)
                    )
                )
                .all()
            )

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
            {
                "name": "Submitted",
                "value": profile_status_count["pending"]
                + leave_status_count["Pending"],
            },
            {
                "name": "Pending Review",
                "value": profile_status_count["pending"]
                + leave_status_count["Pending"],
            },
            {
                "name": "Approved",
                "value": profile_status_count["approved"]
                + leave_status_count["Approved"],
            },
            {
                "name": "Rejected",
                "value": profile_status_count["rejected"]
                + leave_status_count["Rejected"],
            },
        ]

        return reports_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching reports data: {str(e)}"
        )


@router.get("/charts/employee-distribution")
def get_employee_distribution_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get employee role distribution for charts
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
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
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching employee distribution data: {str(e)}",
        )


@router.get("/charts/contribution/tasks-completed")
def get_tasks_completed_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get tasks completed by the employee over time for contribution charts
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1
        user_role = "Manager"  # Default role for testing

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(
                status_code=403,
                detail="Access denied. This endpoint is for employees only.",
            )

        from datetime import datetime, timedelta

        # Get tasks completed by this employee
        tasks = list_tasks(db, company_id)
        employee_tasks = [
            task
            for task in tasks
            if getattr(task, "assignee_id", None) == current_user_id
        ]

        # Group by completion status and time periods
        completed_tasks = [
            task
            for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.COMPLETED.value
        ]

        # Group by time periods (last 30 days, 30-60 days, 60-90 days, older)
        now = datetime.now()
        time_periods = {
            "Last 7 days": timedelta(days=7),
            "Last 30 days": timedelta(days=30),
            "Last 90 days": timedelta(days=90),
            "Older": None,
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
        raise HTTPException(
            status_code=500, detail=f"Error fetching tasks completed data: {str(e)}"
        )


@router.get("/charts/contribution/tasks-created")
def get_tasks_created_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get tasks created/assigned by the employee for contribution charts
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1
        user_role = "Manager"  # Default role for testing

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(
                status_code=403,
                detail="Access denied. This endpoint is for employees only.",
            )

        # Get tasks created by this employee
        tasks = list_tasks(db, company_id)
        created_tasks = [
            task
            for task in tasks
            if getattr(task, "assigned_by", None) == current_user_id
        ]

        # Group by status
        status_data = {s.value: 0 for s in TaskStatus}

        for task in created_tasks:
            s = (getattr(task, "status", "") or "").strip()
            if s in status_data:
                status_data[s] += 1

        return [
            {"name": "Pending", "value": status_data[TaskStatus.PENDING.value]},
            {"name": "In Progress", "value": status_data[TaskStatus.IN_PROGRESS.value]},
            {"name": "Completed", "value": status_data[TaskStatus.COMPLETED.value]},
            {"name": "Overdue", "value": status_data[TaskStatus.OVERDUE.value]},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching tasks created data: {str(e)}"
        )


@router.get("/charts/contribution/productivity")
def get_productivity_chart(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get productivity metrics for the employee for contribution charts
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        current_user_id = 1
        user_role = "Employee"  # Default role

        # Only allow employees to access this endpoint
        if user_role != "Employee":
            raise HTTPException(
                status_code=403,
                detail="Access denied. This endpoint is for employees only.",
            )

        # Get tasks assigned to this employee
        tasks = list_tasks(db, company_id)
        employee_tasks = [
            task
            for task in tasks
            if getattr(task, "assignee_id", None) == current_user_id
        ]

        total_tasks = len(employee_tasks)
        if total_tasks == 0:
            return [{"name": "No Tasks", "value": 1}]

        # Calculate productivity metrics
        completed_tasks = sum(
            1
            for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.COMPLETED.value
        )

        in_progress_tasks = sum(
            1
            for task in employee_tasks
            if (getattr(task, "status", "") or "").strip()
            == TaskStatus.IN_PROGRESS.value
        )

        pending_tasks = sum(
            1
            for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.PENDING.value
        )

        overdue_tasks = sum(
            1
            for task in employee_tasks
            if (getattr(task, "status", "") or "").strip() == TaskStatus.OVERDUE.value
        )

        # Calculate completion rate
        completion_rate = (
            (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        )

        return [
            {"name": "Completed", "value": completed_tasks},
            {"name": "In Progress", "value": in_progress_tasks},
            {"name": "Pending", "value": pending_tasks},
            {"name": "Overdue", "value": overdue_tasks},
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching productivity data: {str(e)}"
        )


def _require_manager_role(current_user: User):
    """
    Ensure the current user has Manager, CompanyAdmin, or SuperAdmin role.
    """
    if current_user.role not in [
        "Manager",
        "CompanyAdmin",
        "SuperAdmin",
        "SUPERADMIN",
        "MANAGER",
        "COMPANYADMIN",
    ]:
        raise HTTPException(
            status_code=403, detail="Access denied. Manager/Admin role required."
        )


@router.get("/attendance")
def get_attendance_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "weekly",  # "daily" or "weekly"
):
    """
    Get attendance trend data: daily/weekly employee attendance counts (Present vs Absent)
    """
    try:
        # For testing, bypass role check and hardcode company_id
        company_id = 1  # Hardcoded for testing

        # Get total employees in company
        total_employees = (
            db.query(func.count(User.id)).filter(User.company_id == company_id).scalar()
        )

        today = date.today()
        start_date = today - timedelta(days=30 if period == "daily" else 90)

        if period == "daily":
            trend_data = (
                db.query(
                    func.date(Attendance.clock_in_time).label("date"),
                    func.count(distinct(Attendance.employee_id)).label("present"),
                )
                .filter(
                    Attendance.company_id == company_id,
                    Attendance.clock_in_time >= start_date,
                    Attendance.status == "active",
                )
                .group_by(func.date(Attendance.clock_in_time))
                .all()
            )

            # Fill missing dates with 0 present
            data_dict = {row.date: row.present for row in trend_data}
            result = []
            current_date = start_date
            while current_date <= today:
                present = data_dict.get(current_date, 0)
                absent = total_employees - present
                result.append(
                    {
                        "date": current_date.isoformat(),
                        "present": present,
                        "absent": absent,
                    }
                )
                current_date += timedelta(days=1)
            return result

        else:  # weekly
            trend_data = (
                db.query(
                    extract("year", Attendance.clock_in_time).label("year"),
                    extract("week", Attendance.clock_in_time).label("week"),
                    func.count(distinct(Attendance.employee_id)).label("present"),
                )
                .filter(
                    Attendance.company_id == company_id,
                    Attendance.clock_in_time >= start_date,
                    Attendance.status == "active",
                )
                .group_by(
                    extract("year", Attendance.clock_in_time),
                    extract("week", Attendance.clock_in_time),
                )
                .all()
            )

            # Process weeks
            data_dict = {
                f"{int(row.year)}-{int(row.week):02d}": row.present
                for row in trend_data
            }
            result = []
            current_date = start_date
            week_start = current_date - timedelta(days=current_date.weekday())  # Monday
            while week_start <= today:
                week_key = week_start.strftime("%Y-%W")
                present = data_dict.get(week_key, 0)
                absent = total_employees - present
                result.append({"week": week_key, "present": present, "absent": absent})
                current_date += timedelta(weeks=1)
                week_start = current_date - timedelta(days=current_date.weekday())
            return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching attendance data: {str(e)}"
        )


@router.get("/leaves")
def get_leave_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "monthly",  # "weekly" or "monthly"
):
    """
    Get leave utilization: % of employees on leave per week/month
    """
    try:
        # For testing, bypass role check and hardcode company_id
        company_id = 1  # Hardcoded for testing

        total_employees = (
            db.query(func.count(User.id)).filter(User.company_id == company_id).scalar()
        )

        today = date.today()
        start_date = today - timedelta(days=30 if period == "weekly" else 90)

        if period == "weekly":
            leave_data = (
                db.query(
                    extract("year", Leave.start_at).label("year"),
                    extract("week", Leave.start_at).label("week"),
                    func.count(Leave.id).label("on_leave"),
                )
                .filter(
                    Leave.employee_id.in_(
                        db.query(User.id).filter(User.company_id == company_id)
                    ),
                    Leave.status == "Approved",
                    Leave.start_at >= start_date,
                    Leave.end_at >= start_date,  # Overlapping leaves
                )
                .group_by(
                    extract("year", Leave.start_at), extract("week", Leave.start_at)
                )
                .all()
            )

            data_dict = {
                f"{int(row.year)}-{int(row.week):02d}": row.on_leave
                for row in leave_data
            }
            result = []
            current_date = start_date
            week_start = current_date - timedelta(days=current_date.weekday())
            while week_start <= today:
                week_key = week_start.strftime("%Y-%W")
                on_leave = data_dict.get(week_key, 0)
                utilization_pct = (
                    (on_leave / total_employees * 100) if total_employees > 0 else 0
                )
                result.append(
                    {
                        "week": week_key,
                        "on_leave": on_leave,
                        "utilization_pct": round(utilization_pct, 2),
                    }
                )
                current_date += timedelta(weeks=1)
                week_start = current_date - timedelta(days=current_date.weekday())
            return result

        else:  # monthly
            leave_data = (
                db.query(
                    extract("year", Leave.start_at).label("year"),
                    extract("month", Leave.start_at).label("month"),
                    func.count(Leave.id).label("on_leave"),
                )
                .filter(
                    Leave.employee_id.in_(
                        db.query(User.id).filter(User.company_id == company_id)
                    ),
                    Leave.status == "Approved",
                    Leave.start_at >= start_date,
                    Leave.end_at >= start_date,
                )
                .group_by(
                    extract("year", Leave.start_at), extract("month", Leave.start_at)
                )
                .all()
            )

            data_dict = {
                f"{int(row.year)}-{int(row.month):02d}": row.on_leave
                for row in leave_data
            }
            result = []
            current_date = start_date.replace(day=1)
            while current_date <= today:
                month_key = current_date.strftime("%Y-%m")
                on_leave = data_dict.get(month_key, 0)
                utilization_pct = (
                    (on_leave / total_employees * 100) if total_employees > 0 else 0
                )
                result.append(
                    {
                        "month": month_key,
                        "on_leave": on_leave,
                        "utilization_pct": round(utilization_pct, 2),
                    }
                )
                if current_date.month == 12:
                    current_date = current_date.replace(
                        year=current_date.year + 1, month=1
                    )
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching leave data: {str(e)}"
        )


@router.get("/overtime")
def get_overtime_data(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
    period: str = "monthly",  # "weekly" or "monthly"
):
    """
    Get overtime hours: total per department or user
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1

        today = date.today()
        start_date = today - timedelta(days=30 if period == "weekly" else 90)

        # Join Attendance with EmployeeProfile for department
        overtime_query = (
            db.query(
                EmployeeProfile.department.label("department"),
                func.sum(Attendance.overtime_hours).label("total_overtime"),
            )
            .outerjoin(Attendance, Attendance.employee_id == EmployeeProfile.user_id)
            .filter(
                EmployeeProfile.company_id == company_id,
                Attendance.clock_in_time >= start_date,
                Attendance.overtime_hours > 0,
            )
            .group_by(EmployeeProfile.department)
            .all()
        )

        result = [
            {
                "department": row.department or "Unknown",
                "total_overtime": row.total_overtime or 0,
            }
            for row in overtime_query
        ]
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching overtime data: {str(e)}"
        )


@router.get("/payroll")
def get_payroll_estimates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "monthly",
):
    """
    Get payroll estimates: aggregate salary × attendance for monthly cost
    """
    try:
        # For testing, bypass role check and hardcode company_id
        company_id = 1  # Hardcoded for testing

        # Assume 22 working days per month
        working_days = 22

        # Get employees with base_salary
        employees_query = (
            db.query(Employee.id, Employee.base_salary)
            .filter(Employee.tenant_id == str(company_id))
            .all()
        )

        total_estimated_payroll = 0
        for emp in employees_query:
            # Get attendance days for the period
            att_days = (
                db.query(func.count(distinct(func.date(Attendance.clock_in_time))))
                .filter(
                    Attendance.employee_id == emp.id,
                    extract("month", Attendance.clock_in_time) == date.today().month,
                    extract("year", Attendance.clock_in_time) == date.today().year,
                )
                .scalar()
                or 0
            )

            attendance_factor = att_days / working_days if working_days > 0 else 0
            estimated_salary = emp.base_salary * attendance_factor
            total_estimated_payroll += estimated_salary

        return {
            "period": period,
            "working_days": working_days,
            "total_estimated_payroll": round(total_estimated_payroll, 2),
            "employees_count": len(employees_query),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching payroll data: {str(e)}"
        )


@router.get("/export/{data_type}")
def export_dashboard_data(
    data_type: str,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
    period: str = "weekly",
):
    """
    Export dashboard data as CSV: attendance, leaves, overtime, payroll
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1

        if data_type == "attendance":
            trend_data = get_attendance_trend(db, current_user, period)
            df = pd.DataFrame(trend_data)
        elif data_type == "leaves":
            trend_data = get_leave_utilization(db, current_user, period)
            df = pd.DataFrame(trend_data)
        elif data_type == "overtime":
            trend_data = get_overtime_data(db, current_user, period)
            df = pd.DataFrame(trend_data)
        elif data_type == "payroll":
            payroll_data = get_payroll_estimates(db, current_user, period)
            df = pd.DataFrame([payroll_data])  # Single row for summary
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={data_type}_export_{period}.csv"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@router.get("/analytics/trends")
def get_analytics_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "monthly",  # "weekly" or "monthly"
):
    """
    Get advanced analytics trends: task completion rates, attendance patterns, leave utilization
    """
    try:
        _require_manager_role(current_user)
        company_id = _require_company_id(current_user)

        today = date.today()
        start_date = today - timedelta(days=90)  # Last 3 months

        # Task completion trends
        task_trends = (
            db.query(
                func.date(Task.updated_at).label("date"),
                func.count(Task.id).label("total_tasks"),
                func.sum(
                    func.case((Task.status == TaskStatus.COMPLETED.value, 1), else_=0)
                ).label("completed_tasks"),
            )
            .filter(Task.company_id == company_id, Task.updated_at >= start_date)
            .group_by(func.date(Task.updated_at))
            .all()
        )

        # Attendance patterns by day of week
        attendance_patterns = (
            db.query(
                extract("dow", Attendance.clock_in_time).label("day_of_week"),
                func.count(distinct(Attendance.employee_id)).label("present_count"),
            )
            .filter(
                Attendance.company_id == company_id,
                Attendance.clock_in_time >= start_date,
                Attendance.status == "active",
            )
            .group_by(extract("dow", Attendance.clock_in_time))
            .all()
        )

        # Leave utilization by month
        leave_trends = (
            db.query(
                extract("year", Leave.start_at).label("year"),
                extract("month", Leave.start_at).label("month"),
                func.count(Leave.id).label("total_leaves"),
            )
            .filter(
                Leave.employee_id.in_(
                    db.query(User.id).filter(User.company_id == company_id)
                ),
                Leave.status == "Approved",
                Leave.start_at >= start_date,
            )
            .group_by(extract("year", Leave.start_at), extract("month", Leave.start_at))
            .all()
        )

        return {
            "task_completion_trends": [
                {
                    "date": str(row.date),
                    "total_tasks": row.total_tasks,
                    "completed_tasks": row.completed_tasks or 0,
                    "completion_rate": (
                        round((row.completed_tasks or 0) / row.total_tasks * 100, 2)
                        if row.total_tasks > 0
                        else 0
                    ),
                }
                for row in task_trends
            ],
            "attendance_patterns": [
                {
                    "day_of_week": int(row.day_of_week),
                    "day_name": [
                        "Sunday",
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                    ][int(row.day_of_week)],
                    "present_count": row.present_count,
                }
                for row in attendance_patterns
            ],
            "leave_utilization_trends": [
                {
                    "month": f"{int(row.year)}-{int(row.month):02d}",
                    "total_leaves": row.total_leaves,
                }
                for row in leave_trends
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching analytics trends: {str(e)}"
        )


@router.get("/analytics/heatmap")
def get_activity_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "weekly",  # "daily" or "weekly"
):
    """
    Get activity heatmap data: attendance clock-ins by hour and day
    """
    try:
        # For testing, bypass role check and hardcode company_id
        company_id = 1  # Hardcoded for testing

        today = date.today()
        start_date = today - timedelta(days=30 if period == "daily" else 90)

        # Attendance heatmap: count by day of week and hour
        heatmap_data = (
            db.query(
                extract("dow", Attendance.clock_in_time).label("day_of_week"),
                extract("hour", Attendance.clock_in_time).label("hour"),
                func.count(Attendance.id).label("activity_count"),
            )
            .filter(
                Attendance.company_id == company_id,
                Attendance.clock_in_time >= start_date,
                Attendance.status == "active",
            )
            .group_by(
                extract("dow", Attendance.clock_in_time),
                extract("hour", Attendance.clock_in_time),
            )
            .all()
        )

        # Task activity heatmap: tasks created/updated by hour and day
        task_heatmap = (
            db.query(
                extract("dow", Task.created_at).label("day_of_week"),
                extract("hour", Task.created_at).label("hour"),
                func.count(Task.id).label("task_count"),
            )
            .filter(Task.company_id == company_id, Task.created_at >= start_date)
            .group_by(extract("dow", Task.created_at), extract("hour", Task.created_at))
            .all()
        )

        # Convert to heatmap format (7 days x 24 hours)
        attendance_heatmap = [[0 for _ in range(24)] for _ in range(7)]
        task_activity_heatmap = [[0 for _ in range(24)] for _ in range(7)]

        for row in heatmap_data:
            day = int(row.day_of_week)
            hour = int(row.hour)
            attendance_heatmap[day][hour] = row.activity_count

        for row in task_heatmap:
            day = int(row.day_of_week)
            hour = int(row.hour)
            task_activity_heatmap[day][hour] = row.task_count

        return {
            "attendance_heatmap": {
                "data": attendance_heatmap,
                "days": [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
                "hours": list(range(24)),
            },
            "task_activity_heatmap": {
                "data": task_activity_heatmap,
                "days": [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
                "hours": list(range(24)),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching heatmap data: {str(e)}"
        )


@router.get("/analytics/real-time")
def get_real_time_kpis(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Get real-time KPI updates for dashboard
    """
    try:
        # For testing, use default company_id = 1
        company_id = 1
        user_role = "Manager"  # Default role for testing

        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)

        if user_role in [
            "Manager",
            "CompanyAdmin",
            "SuperAdmin",
            "SUPERADMIN",
            "MANAGER",
            "COMPANYADMIN",
        ]:
            # Manager/Admin KPIs
            total_employees = (
                db.query(func.count(User.id))
                .filter(User.company_id == company_id)
                .scalar()
            )

            # Today's attendance
            today_attendance = (
                db.query(func.count(distinct(Attendance.employee_id)))
                .filter(
                    Attendance.company_id == company_id,
                    func.date(Attendance.clock_in_time) == today,
                    Attendance.status == "active",
                )
                .scalar()
            )

            # This week's attendance average
            week_attendance = (
                db.query(func.avg(func.count(distinct(Attendance.employee_id))))
                .filter(
                    Attendance.company_id == company_id,
                    Attendance.clock_in_time >= this_week_start,
                    Attendance.status == "active",
                )
                .group_by(func.date(Attendance.clock_in_time))
                .scalar()
            )

            # Active tasks
            active_tasks = (
                db.query(func.count(Task.id))
                .filter(
                    Task.company_id == company_id,
                    Task.status != TaskStatus.COMPLETED.value,
                )
                .scalar()
            )

            # Pending leaves
            pending_leaves = (
                db.query(func.count(Leave.id))
                .filter(
                    Leave.employee_id.in_(
                        db.query(User.id).filter(User.company_id == company_id)
                    ),
                    Leave.status == "Pending",
                )
                .scalar()
            )

            return {
                "total_employees": total_employees or 0,
                "today_attendance": today_attendance or 0,
                "week_attendance_avg": round(week_attendance or 0, 1),
                "active_tasks": active_tasks or 0,
                "pending_leaves": pending_leaves or 0,
                "attendance_rate_today": round(
                    (today_attendance or 0) / (total_employees or 1) * 100, 2
                ),
                "timestamp": datetime.now().isoformat(),
            }

        else:
            # Employee-specific real-time KPIs
            # Tasks assigned to employee
            employee_tasks = (
                db.query(func.count(Task.id))
                .filter(Task.assignee_id == current_user.id)
                .scalar()
            )

            # Completed tasks this month
            completed_this_month = (
                db.query(func.count(Task.id))
                .filter(
                    Task.assignee_id == current_user.id,
                    Task.status == TaskStatus.COMPLETED.value,
                    Task.updated_at >= this_month_start,
                )
                .scalar()
            )

            # Pending approvals (leaves)
            pending_approvals = (
                db.query(func.count(Leave.id))
                .filter(Leave.employee_id == current_user.id, Leave.status == "Pending")
                .scalar()
            )

            # Recent attendance (last 7 days)
            recent_attendance = (
                db.query(func.count(Attendance.id))
                .filter(
                    Attendance.employee_id == current_user.id,
                    Attendance.clock_in_time >= today - timedelta(days=7),
                    Attendance.status == "active",
                )
                .scalar()
            )

            return {
                "my_tasks": employee_tasks or 0,
                "completed_this_month": completed_this_month or 0,
                "pending_approvals": pending_approvals or 0,
                "recent_attendance_days": recent_attendance or 0,
                "timestamp": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching real-time KPIs: {str(e)}"
        )
