from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..schemas import ShiftCreate, ShiftOut
from ..crud import (
    create_shift,
    get_shift_by_id,
    list_shifts_by_employee,
    list_shifts_by_tenant,
    update_shift,
    delete_shift
)
from ..crud_notifications import create_notification
from ..models.user import User
from ..models.notification import NotificationType

router = APIRouter(prefix="/shifts", tags=["Shifts"])

@router.get("/", response_model=List[ShiftOut])
def get_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all shifts for the current user's company
    """
    # For SuperAdmin, get all shifts; for others, get shifts for their company
    if current_user.role == "SuperAdmin":
        shifts = list_shifts_by_tenant(db, current_user.company_id or "default")
    else:
        shifts = list_shifts_by_tenant(db, str(current_user.company_id))
    return shifts

@router.post("/", response_model=ShiftOut, status_code=status.HTTP_201_CREATED)
def create_shift_schedule(
    payload: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new shift schedule
    """
    # Role-based access control - managers and admins can create shifts
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create shift schedules"
        )

    # Ensure the shift is created for the user's company
    if current_user.role != "SuperAdmin" and payload.tenant_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create shift schedule for another company"
        )

    shift = create_shift(
        db=db,
        tenant_id=payload.tenant_id,
        employee_id=payload.employee_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        location=payload.location
    )

    # Create notification for shift assignment
    try:
        create_notification(
            db=db,
            user_id=payload.employee_id,
            company_id=int(payload.tenant_id),
            title="New Shift Scheduled",
            message=f"You have been scheduled for a shift from {payload.start_at.strftime('%Y-%m-%d %H:%M')} to {payload.end_at.strftime('%Y-%m-%d %H:%M')}",
            type=NotificationType.SHIFT_SCHEDULED
        )
    except Exception as e:
        # Log the error but don't fail the shift creation
        print(f"Warning: Failed to create shift notification: {e}")

    return shift

@router.get("/{shift_id}", response_model=ShiftOut)
def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific shift by ID
    """
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    # Ensure user can only access shifts from their company
    if current_user.role != "SuperAdmin" and shift.tenant_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access shift from another company"
        )

    # Employees can only view their own shifts
    if current_user.role == "Employee" and shift.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only view their own shifts"
        )

    return shift

@router.put("/{shift_id}", response_model=ShiftOut)
def update_shift_schedule(
    shift_id: int,
    payload: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a shift schedule
    """
    # Role-based access control - managers and admins can update shifts
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update shift schedules"
        )

    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    # Ensure user can only update shifts from their company
    if current_user.role != "SuperAdmin" and shift.tenant_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update shift from another company"
        )

    updated_shift = update_shift(
        db=db,
        shift_id=shift_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        location=payload.location
    )
    if not updated_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    return updated_shift

@router.delete("/{shift_id}")
def delete_shift_schedule(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a shift schedule
    """
    # Role-based access control - managers and admins can delete shifts
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete shift schedules"
        )

    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    # Ensure user can only delete shifts from their company
    if current_user.role != "SuperAdmin" and shift.tenant_id != str(current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete shift from another company"
        )

    success = delete_shift(db, shift_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    return {"message": "Shift schedule deleted successfully"}

@router.get("/my-shifts/", response_model=List[ShiftOut])
def get_my_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get shift schedules for the current user
    """
    shifts = list_shifts_by_employee(db, current_user.id)
    return shifts
