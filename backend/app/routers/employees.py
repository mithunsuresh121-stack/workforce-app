from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import (create_employee_profile, delete_employee_profile,
                      get_employee_profile_by_user_id,
                      list_employee_profiles_by_company,
                      update_employee_profile)
from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import (EmployeeProfileCreate, EmployeeProfileOut,
                         EmployeeProfileUpdate)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/", response_model=List[EmployeeProfileOut])
def get_employee_profiles(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get all employee profiles for the current user's company
    """
    profiles = list_employee_profiles_by_company(db, current_user.company_id)
    return profiles


@router.post(
    "/", response_model=EmployeeProfileOut, status_code=status.HTTP_201_CREATED
)
def create_employee_profile_endpoint(
    payload: EmployeeProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new employee profile for the current user's company
    """
    logger.info(
        "create_employee_profile_endpoint called",
        event="create_employee_profile",
        user_id=current_user.id,
        company_id=current_user.company_id,
        payload_user_id=payload.user_id,
        payload_company_id=payload.company_id,
    )
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        logger.warning(
            "insufficient_permissions",
            event="create_employee_profile_denied",
            user_id=current_user.id,
            company_id=current_user.company_id,
            role=current_user.role,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create employee profiles",
        )

    # Ensure the profile is created for the user's company (SuperAdmin can create for any)
    if (
        current_user.role != "SuperAdmin"
        and payload.company_id != current_user.company_id
    ):
        logger.warning(
            "cross_company_access_denied",
            event="create_employee_profile_denied",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_company_id=payload.company_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create employee profile for another company",
        )

    # Pre-insert check to avoid DB constraint violation
    existing_profile = get_employee_profile_by_user_id(
        db, payload.user_id, payload.company_id
    )
    if existing_profile:
        logger.warning(
            "profile_already_exists",
            event="create_employee_profile_conflict",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_user_id=payload.user_id,
            target_company_id=payload.company_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee profile already exists for this user",
        )

    logger.info(
        "proceeding_with_profile_creation",
        event="create_employee_profile_start",
        user_id=current_user.id,
        company_id=current_user.company_id,
        target_user_id=payload.user_id,
    )
    try:
        profile = create_employee_profile(
            db=db,
            user_id=payload.user_id,
            company_id=payload.company_id,
            department=payload.department,
            position=payload.position,
            phone=payload.phone,
            hire_date=payload.hire_date,
            manager_id=payload.manager_id,
        )
        logger.info(
            "profile_created_successfully",
            event="create_employee_profile_success",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_user_id=payload.user_id,
            profile_id=profile.id,
        )
        return profile
    except IntegrityError as e:
        logger.error(
            "integrity_error_during_creation",
            event="create_employee_profile_error",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_user_id=payload.user_id,
            error=str(e),
            orig=str(e.orig),
        )
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee profile already exists for this user",
            )
        raise
    except Exception as e:
        logger.error(
            "unexpected_error_during_creation",
            event="create_employee_profile_error",
            user_id=current_user.id,
            company_id=current_user.company_id,
            target_user_id=payload.user_id,
            error_type=type(e).__name__,
            error=str(e),
        )
        raise


@router.get("/{user_id}", response_model=EmployeeProfileOut)
def get_employee_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific employee profile by user ID
    """
    profile = get_employee_profile_by_user_id(db, user_id, current_user.company_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee profile not found"
        )
    return profile


@router.put("/{user_id}", response_model=EmployeeProfileOut)
def update_employee_profile_endpoint(
    user_id: int,
    payload: EmployeeProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an employee profile
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update employee profiles",
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
        is_active=payload.is_active,
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee profile not found"
        )
    return profile


@router.delete("/{user_id}")
def delete_employee_profile_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an employee profile (soft delete)
    """
    # Role-based access control
    if current_user.role not in ["SuperAdmin", "CompanyAdmin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete employee profiles",
        )

    success = delete_employee_profile(db, user_id, current_user.company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee profile not found"
        )
    return {"message": "Employee profile deleted successfully"}
