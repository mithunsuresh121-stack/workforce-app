from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..deps import get_db, get_current_user
from ..schemas import ShiftCreate, ShiftOut
from ..crud import (
    create_shift,
    get_shift_by_id,
    list_shifts_by_employee,
    list_shifts_by_company,
    update_shift,
    delete_shift
)
from ..crud_notifications import create_notification
from ..models.user import User
from ..models.notification import NotificationType
from ..models.swap_request import SwapRequest, SwapStatus
from ..schemas.swap_request import SwapRequestCreate, SwapRequestOut

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
        shifts = list_shifts_by_company(db, current_user.company_id)
    else:
        shifts = list_shifts_by_company(db, current_user.company_id)
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
    if current_user.role != "SuperAdmin" and payload.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create shift schedule for another company"
        )

    shift = create_shift(
        db=db,
        company_id=payload.company_id,
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
            company_id=payload.company_id,
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
    if current_user.role != "SuperAdmin" and shift.company_id != current_user.company_id:
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
    if current_user.role != "SuperAdmin" and shift.company_id != current_user.company_id:
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

@router.get("/swaps", response_model=List[SwapRequestOut])
def get_shift_swaps(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get shift swap requests, optionally filtered by status
    """
    # Role-based access control - managers and admins can view swaps
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view shift swap requests"
        )

    query = db.query(SwapRequest)
    if status:
        query = query.filter(SwapRequest.status == status)

    # Ensure user can only access swaps from their company
    if current_user.role != "SuperAdmin":
        query = query.filter(SwapRequest.company_id == current_user.company_id)

    swaps = query.all()
    return swaps

@router.post("/swap-request/", response_model=SwapRequestOut, status_code=status.HTTP_201_CREATED)
def request_shift_swap(
    payload: SwapRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request a shift swap with another employee
    """
    # Get the requester's shift
    requester_shift = get_shift_by_id(db, payload.requester_shift_id)
    if not requester_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester shift not found"
        )

    # Get the target shift
    target_shift = get_shift_by_id(db, payload.target_shift_id)
    if not target_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target shift not found"
        )

    # Ensure both shifts belong to the same company
    if requester_shift.company_id != target_shift.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot swap shifts from different companies"
        )

    # Ensure the requester owns the requester shift
    if requester_shift.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request swaps for your own shifts"
        )

    # Ensure shifts are not in the past or completed
    from datetime import datetime
    if requester_shift.start_at < datetime.utcnow() or target_shift.start_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot swap past or current shifts"
        )

    # Create swap request
    swap_request = SwapRequest(
        company_id=requester_shift.company_id,
        requester_shift_id=payload.requester_shift_id,
        target_shift_id=payload.target_shift_id,
        requester_id=current_user.id,
        target_employee_id=target_shift.employee_id,
        reason=payload.reason
    )
    db.add(swap_request)
    db.commit()
    db.refresh(swap_request)

    # Create notification for target employee
    try:
        create_notification(
            db=db,
            user_id=target_shift.employee_id,
            company_id=requester_shift.company_id,
            title="Shift Swap Request",
            message=f"{current_user.full_name} has requested to swap shifts with you. Reason: {payload.reason or 'No reason provided'}",
            type=NotificationType.SHIFT_SWAP_REQUESTED
        )
    except Exception as e:
        print(f"Warning: Failed to create swap request notification: {e}")

    return swap_request

@router.post("/swap-approve/{swap_request_id}", response_model=SwapRequestOut)
def approve_shift_swap(
    swap_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve a shift swap request (managers and target employee can approve)
    """
    swap_request = db.query(SwapRequest).filter(SwapRequest.id == swap_request_id).first()
    if not swap_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )

    # Check permissions: target employee or manager/admin
    can_approve = (
        swap_request.target_employee_id == current_user.id or
        current_user.role in ["SuperAdmin", "CompanyAdmin", "Manager"]
    )

    if not can_approve:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to approve this swap request"
        )

    if swap_request.status != SwapStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Swap request is not pending"
        )

    # Swap the employee assignments
    requester_shift = get_shift_by_id(db, swap_request.requester_shift_id)
    target_shift = get_shift_by_id(db, swap_request.target_shift_id)

    if not requester_shift or not target_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both shifts not found"
        )

    # Perform the swap
    temp_employee = requester_shift.employee_id
    requester_shift.employee_id = target_shift.employee_id
    target_shift.employee_id = temp_employee

    # Update swap request
    swap_request.status = SwapStatus.APPROVED
    swap_request.reviewed_by = current_user.id
    swap_request.reviewed_at = datetime.utcnow()

    db.commit()

    # Create notifications
    try:
        # Notify requester
        create_notification(
            db=db,
            user_id=swap_request.requester_id,
            company_id=swap_request.company_id,
            title="Shift Swap Approved",
            message="Your shift swap request has been approved.",
            type=NotificationType.SHIFT_SWAP_APPROVED
        )
        # Notify target
        create_notification(
            db=db,
            user_id=swap_request.target_employee_id,
            company_id=swap_request.company_id,
            title="Shift Swap Approved",
            message="A shift swap request has been approved.",
            type=NotificationType.SHIFT_SWAP_APPROVED
        )
    except Exception as e:
        print(f"Warning: Failed to create approval notifications: {e}")

    return swap_request

@router.post("/swap-reject/{swap_request_id}", response_model=SwapRequestOut)
def reject_shift_swap(
    swap_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject a shift swap request (managers and target employee can reject)
    """
    swap_request = db.query(SwapRequest).filter(SwapRequest.id == swap_request_id).first()
    if not swap_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Swap request not found"
        )

    # Check permissions: target employee or manager/admin
    can_reject = (
        swap_request.target_employee_id == current_user.id or
        current_user.role in ["SuperAdmin", "CompanyAdmin", "Manager"]
    )

    if not can_reject:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to reject this swap request"
        )

    if swap_request.status != SwapStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Swap request is not pending"
        )

    # Update swap request
    swap_request.status = SwapStatus.REJECTED
    swap_request.reviewed_by = current_user.id
    swap_request.reviewed_at = datetime.utcnow()

    db.commit()

    # Create notifications
    try:
        create_notification(
            db=db,
            user_id=swap_request.requester_id,
            company_id=swap_request.company_id,
            title="Shift Swap Rejected",
            message="Your shift swap request has been rejected.",
            type=NotificationType.SHIFT_SWAP_REJECTED
        )
    except Exception as e:
        print(f"Warning: Failed to create rejection notification: {e}")

    return swap_request
