from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import (create_leave, delete_leave, get_leave_by_id,
                      list_leaves_by_employee, list_leaves_by_tenant,
                      update_leave_status)
from app.crud_notifications import create_notification
from app.deps import get_current_user, get_db
from app.models.notification import NotificationType
from app.models.user import User
from app.schemas import LeaveCreate, LeaveOut, LeaveStatus

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.get("/", response_model=List[LeaveOut])
def get_leaves(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all leave requests for the current user's company
    """
    # For SuperAdmin, get all leaves; for others, get leaves for their company
    if current_user.role == "SuperAdmin":
        leaves = list_leaves_by_tenant(db, str(current_user.company_id or "default"))
    else:
        leaves = list_leaves_by_tenant(db, str(current_user.company_id))
    return leaves


@router.get("/balances", response_model=Dict[str, Dict[str, int]])
def get_leave_balances(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get leave balances for the current user
    """
    # This is a simplified implementation - in a real app, you'd calculate
    # actual balances based on approved leaves and company policies
    balances = {
        "Vacation": {"used": 0, "total": 25},
        "Sick Leave": {"used": 0, "total": 10},
        "Personal Leave": {"used": 0, "total": 5},
        "Maternity Leave": {"used": 0, "total": 90},
        "Paternity Leave": {"used": 0, "total": 10},
        "Bereavement Leave": {"used": 0, "total": 5},
    }

    # Get actual used days from approved leaves
    leaves = list_leaves_by_employee(db, current_user.id)
    for leave in leaves:
        if leave.status.value == "Approved" and leave.type in balances:
            # Calculate days for this leave
            start_date = leave.start_at.date()
            end_date = leave.end_at.date()
            days = (end_date - start_date).days + 1
            balances[leave.type]["used"] += days

    return balances


@router.post("/", response_model=LeaveOut, status_code=status.HTTP_201_CREATED)
def create_leave_request(
    payload: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new leave request
    """
    # Role-based access control - employees can create their own leave requests
    # Managers and admins can create leave requests for others
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager", "Employee"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create leave requests",
        )

    # Ensure the leave is created for the user's company
    if current_user.role != "SuperAdmin" and payload.tenant_id != str(
        current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create leave request for another company",
        )

    # Employees can only create leave requests for themselves
    if current_user.role == "Employee" and payload.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only create leave requests for themselves",
        )

    leave = create_leave(
        db=db,
        tenant_id=payload.tenant_id,
        employee_id=payload.employee_id,
        type=payload.type,
        start_at=payload.start_at,
        end_at=payload.end_at,
        status=payload.status,
    )
    return leave


@router.get("/{leave_id}", response_model=LeaveOut)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific leave request by ID
    """
    leave = get_leave_by_id(db, leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found"
        )

    # Ensure user can only access leaves from their company
    if current_user.role != "SuperAdmin" and leave.tenant_id != str(
        current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access leave request from another company",
        )

    # Employees can only view their own leave requests
    if current_user.role == "Employee" and leave.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only view their own leave requests",
        )

    return leave


from pydantic import BaseModel


class LeaveStatusUpdate(BaseModel):
    status: LeaveStatus


@router.put("/{leave_id}/status", response_model=LeaveOut)
def update_leave_status_endpoint(
    leave_id: int,
    status_update: LeaveStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the status of a leave request (approve/reject)
    """
    # Role-based access control - only managers and admins can approve/reject
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update leave status",
        )

    leave = get_leave_by_id(db, leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found"
        )

    # Ensure user can only update leaves from their company
    if current_user.role != "SuperAdmin" and leave.tenant_id != str(
        current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update leave request from another company",
        )

    updated_leave = update_leave_status(db, leave_id, status_update.status.value)
    if not updated_leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found"
        )

    # Create notification for the employee
    new_status = status_update.status.value
    try:
        create_notification(
            db=db,
            user_id=leave.employee_id,
            company_id=int(leave.tenant_id),
            title="Leave Approved" if new_status == "APPROVED" else "Leave Rejected",
            message=f"Your leave request ({leave.type}) was {new_status.lower()} by {current_user.full_name}.",
            type=(
                NotificationType.LEAVE_APPROVED
                if new_status == "APPROVED"
                else NotificationType.LEAVE_REJECTED
            ),
        )
        logger.info(
            "leave_notification_created",
            event="leave_status_update_notification",
            user_id=current_user.id,
            company_id=current_user.company_id,
            leave_id=leave_id,
            employee_id=leave.employee_id,
            new_status=new_status,
        )
    except Exception as e:
        logger.warning(
            "failed_to_create_leave_notification",
            event="leave_status_update_notification_error",
            user_id=current_user.id,
            company_id=current_user.company_id,
            leave_id=leave_id,
            employee_id=leave.employee_id,
            error=str(e),
        )

    return updated_leave


@router.delete("/{leave_id}")
def delete_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a leave request
    """
    # Role-based access control - only managers and admins can delete
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete leave requests",
        )

    leave = get_leave_by_id(db, leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found"
        )

    # Ensure user can only delete leaves from their company
    if current_user.role != "SuperAdmin" and leave.tenant_id != str(
        current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete leave request from another company",
        )

    success = delete_leave(db, leave_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found"
        )
    return {"message": "Leave request deleted successfully"}


@router.get("/my-leaves/", response_model=List[LeaveOut])
def get_my_leaves(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get leave requests for the current user
    """
    leaves = list_leaves_by_employee(db, current_user.id)
    return leaves
