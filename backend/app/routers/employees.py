from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from ..deps import get_db, get_current_user
from ..schemas import EmployeeProfileCreate, EmployeeProfileOut, EmployeeProfileUpdate
from ..crud import (
    list_employee_profiles_by_company,
    create_employee_profile,
    get_employee_profile_by_user_id,
    update_employee_profile,
    delete_employee_profile
)
from ..models.user import User

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[EmployeeProfileOut])
def get_employee_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all employee profiles for the current user's company
    """
    profiles = list_employee_profiles_by_company(db, current_user.company_id)
    return profiles

@router.post("/", response_model=EmployeeProfileOut, status_code=status.HTTP_201_CREATED)
def create_employee_profile_endpoint(
    payload: EmployeeProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new employee profile for the current user's company
    """
    print(f"DEBUG: create_employee_profile_endpoint called with user_id={payload.user_id}, company_id={payload.company_id}")
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create employee profiles"
        )

    # Ensure the profile is created for the user's company (SuperAdmin can create for any)
    if current_user.role != "SuperAdmin" and payload.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create employee profile for another company"
        )

    # Pre-insert check to avoid DB constraint violation
    existing_profile = get_employee_profile_by_user_id(db, payload.user_id, payload.company_id)
    if existing_profile:
        print(f"DEBUG: Found existing profile for user_id={payload.user_id}, company_id={payload.company_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee profile already exists for this user"
        )

    print(f"DEBUG: No existing profile found, proceeding with creation for user_id={payload.user_id}")
    try:
        profile = create_employee_profile(
            db=db,
            user_id=payload.user_id,
            company_id=payload.company_id,
            department=payload.department,
            position=payload.position,
            phone=payload.phone,
            hire_date=payload.hire_date,
            manager_id=payload.manager_id
        )
        print(f"DEBUG: Successfully created profile for user_id={payload.user_id}")
        return profile
    except IntegrityError as e:
        import traceback
        print(f"DEBUG: IntegrityError caught: {e}")
        print(f"DEBUG: Exception orig: {e.orig}")
        traceback.print_exc()
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee profile already exists for this user"
            )
        raise
    except Exception as e:
        import traceback
        print(f"DEBUG: Unexpected exception: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise

@router.get("/{user_id}", response_model=EmployeeProfileOut)
def get_employee_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific employee profile by user ID
    """
    profile = get_employee_profile_by_user_id(db, user_id, current_user.company_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return profile

@router.put("/{user_id}", response_model=EmployeeProfileOut)
def update_employee_profile_endpoint(
    user_id: int,
    payload: EmployeeProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an employee profile
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        # Users can update their own profile
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update employee profiles"
            )

    # Additional validation for phone number
    if payload.phone:
        import re
        phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
        if not phone_pattern.match(payload.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format. Please use format: +1 (555) 123-4567 or similar"
            )

    # Validate hire date is not in the future
    if payload.hire_date:
        from datetime import datetime
        if payload.hire_date > datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hire date cannot be in the future"
            )

    profile = update_employee_profile(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id,
        department=payload.department,
        position=payload.position,
        phone=payload.phone,
        hire_date=payload.hire_date,
        manager_id=payload.manager_id,
        is_active=payload.is_active
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return profile

@router.delete("/{user_id}")
def delete_employee_profile_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an employee profile (soft delete)
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete employee profiles"
        )

    success = delete_employee_profile(db, user_id, current_user.company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    return {"message": "Employee profile deleted successfully"}
