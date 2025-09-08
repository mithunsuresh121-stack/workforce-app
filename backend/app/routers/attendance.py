from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging
from typing import List
from ..deps import get_db, get_current_user
from ..schemas.attendance import (
    Attendance,
    Break,
    ClockInRequest,
    ClockOutRequest,
    BreakStartRequest,
    BreakEndRequest,
    AttendanceSummary
)
from ..crud import (
    create_attendance,
    get_active_attendance_by_employee,
    clock_out_attendance,
    list_attendance_by_employee,
    create_break,
    get_break_by_id,
    end_break,
    list_breaks_by_attendance,
    get_attendance_by_id
)
from ..models.user import User

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/clock-in", response_model=Attendance, status_code=status.HTTP_201_CREATED)
def clock_in(
    payload: ClockInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clock in for the specified employee
    """
    # Check if user already has an active attendance record
    active_attendance = get_active_attendance_by_employee(db, payload.employee_id)
    if active_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active attendance record"
        )

    # Verify the employee_id matches the current user or user has permission
    if current_user.id != payload.employee_id and current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    attendance = create_attendance(
        db=db,
        employee_id=payload.employee_id,
        clock_in_time=datetime.now(timezone.utc),
        notes=payload.notes
    )
    logging.info(f"Attendance clock-in created for employee {payload.employee_id} at {attendance.clock_in_time}")
    return attendance


@router.put("/clock-out", response_model=Attendance)
def clock_out(
    payload: ClockOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clock out the specified attendance record
    """
    try:
        # Verify the attendance belongs to the current user or user has permission
        attendance = get_attendance_by_id(db, payload.attendance_id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        if attendance.employee_id != payload.employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID mismatch"
            )

        if current_user.id != payload.employee_id and current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        print(f"Clocking out attendance {payload.attendance_id} for employee {payload.employee_id}")

        updated_attendance = clock_out_attendance(
            db=db,
            attendance_id=payload.attendance_id,
            notes=payload.notes
        )
        if not updated_attendance:
            print(f"Clock out failed for attendance {payload.attendance_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clock out"
            )
        print(f"Successfully clocked out attendance {updated_attendance.id}")
        return updated_attendance
    except Exception as e:
        print(f"Error in clock_out endpoint: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/breaks/start", response_model=Break, status_code=status.HTTP_201_CREATED)
def start_break(
    payload: BreakStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a break for the current active attendance or specified attendance_id
    """
    attendance_id = getattr(payload, "attendance_id", None)
    if attendance_id is None:
        active_attendance = get_active_attendance_by_employee(db, current_user.id)
        if not active_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active attendance record found"
            )
        attendance_id = active_attendance.id
    else:
        # Verify attendance belongs to current user or user has permission
        attendance = get_attendance_by_id(db, attendance_id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        if attendance.employee_id != current_user.id and current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    # Check if there's already an active break
    breaks = list_breaks_by_attendance(db, attendance_id)
    active_break = next((b for b in breaks if b.break_end is None), None)
    if active_break:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active break"
        )

    break_record = create_break(
        db=db,
        attendance_id=attendance_id,
        break_start=datetime.now(timezone.utc),
        break_type=payload.break_type
    )
    return break_record


@router.post("/break-start", response_model=Break, status_code=status.HTTP_201_CREATED)
def start_break_with_payload(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a break with employee_id and attendance_id in payload
    """
    employee_id = payload.get("employee_id")
    attendance_id = payload.get("attendance_id")
    break_type = payload.get("break_type", "lunch")

    # Verify the attendance belongs to the current user
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance or attendance.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check if there's already an active break
    breaks = list_breaks_by_attendance(db, attendance_id)
    active_break = next((b for b in breaks if b.break_end is None), None)
    if active_break:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active break"
        )

    break_record = create_break(
        db=db,
        attendance_id=attendance_id,
        break_start=datetime.now(timezone.utc),
        break_type=break_type
    )
    return break_record


@router.post("/break-end", response_model=Break)
def end_break_with_payload(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End a break with employee_id and attendance_id in payload
    """
    employee_id = payload.get("employee_id")
    attendance_id = payload.get("attendance_id")

    # Verify the attendance belongs to the current user
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance or attendance.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Find the active break for this attendance
    breaks = list_breaks_by_attendance(db, attendance_id)
    active_break = next((b for b in breaks if b.break_end is None), None)
    if not active_break:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active break found"
        )

    updated_break = end_break(db=db, break_id=active_break.id)
    if not updated_break:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end break"
        )
    return updated_break


@router.put("/breaks/{break_id}/end", response_model=Break)
def end_break_endpoint(
    break_id: int,
    payload: BreakEndRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End a specific break
    """
    break_record = get_break_by_id(db, break_id)
    if not break_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Break record not found"
        )

    # Check if the break belongs to the current user or user has permission
    attendance = get_attendance_by_id(db, break_record.attendance_id)
    if attendance.employee_id != current_user.id and current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if break_record.break_end is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Break is already ended"
        )

    updated_break = end_break(db=db, break_id=break_id)
    if not updated_break:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end break"
        )
    return updated_break


@router.get("/my", response_model=List[Attendance])
def get_my_attendance(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's attendance records
    """
    return list_attendance_by_employee(db, current_user.id, limit)


@router.get("/{employee_id}", response_model=List[Attendance])
def get_employee_attendance(
    employee_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance records for a specific employee (role-based access)
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        # Employees can only view their own records
        if current_user.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return list_attendance_by_employee(db, employee_id, limit)


@router.get("/active/{employee_id}", response_model=List[Attendance])
def get_active_attendance_by_id(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get active attendance records for a specific employee (for cleanup/testing)
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        # Employees can only view their own records
        if current_user.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    active_attendance = get_active_attendance_by_employee(db, employee_id)
    if not active_attendance:
        return []
    return [active_attendance]


@router.get("/active", response_model=Attendance)
def get_active_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's active attendance record
    """
    active_attendance = get_active_attendance_by_employee(db, current_user.id)
    if not active_attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active attendance record found"
        )
    return active_attendance


@router.get("/breaks/{attendance_id}", response_model=List[Break])
def get_breaks_for_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all breaks for a specific attendance record
    """
    # Verify the attendance belongs to the current user
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )

    if attendance.employee_id != current_user.id:
        # Allow managers/admins to view breaks
        if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return list_breaks_by_attendance(db, attendance_id)
