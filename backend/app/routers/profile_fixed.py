from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import (create_employee_profile, create_profile_update_request,
                      get_employee_profile_by_user_id,
                      list_profile_update_requests, update_employee_profile,
                      update_profile_update_request_status)
from app.deps import get_current_user, get_db
from app.models.profile_update_request import RequestStatus
from app.models.user import User
from app.schemas import (EmployeeProfileOut, ProfileUpdateRequestCreate,
                         ProfileUpdateRequestOut, ProfileUpdateRequestReview)

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=EmployeeProfileOut)
def get_my_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile
    """
    profile = get_employee_profile_by_user_id(
        db, current_user.id, current_user.company_id
    )
    if not profile:
        # For demo purposes, create a basic profile if it doesn't exist
        if current_user.email == "admin@app.com":
            profile = create_employee_profile(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id
                or 4,  # Default to company ID 4 if None
                department="IT",
                position="System Administrator",
                phone="+1234567890",
                hire_date="2023-01-01",
                manager_id=None,
            )
        elif current_user.email == "demo@company.com":
            profile = create_employee_profile(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id
                or 4,  # Default to company ID 4 if None
                department="Engineering",
                position="Software Engineer",
                phone="+1234567891",
                hire_date="2023-06-01",
                manager_id=None,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please contact your administrator to create your profile.",
            )
    return profile


@router.post(
    "/request-update",
    response_model=ProfileUpdateRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def request_profile_update(
    payload: ProfileUpdateRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Request a profile update (for employees/managers)
    """
    # Only allow users to request updates for themselves
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot request updates for other users",
        )

    # Validate payload for update requests
    if payload.request_type == "update" and not payload.payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload required for update requests",
        )

    request = create_profile_update_request(
        db=db,
        user_id=payload.user_id,
        requested_by_id=current_user.id,
        request_type=payload.request_type,
        payload=payload.payload,
    )
    return request


@router.post(
    "/request-delete",
    response_model=ProfileUpdateRequestOut,
    status_code=status.HTTP_201_CREATED,
)
def request_account_deletion(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Request account deletion (for employees/managers)
    """
    request = create_profile_update_request(
        db=db,
        user_id=current_user.id,
        requested_by_id=current_user.id,
        request_type="delete",
        payload=None,
    )
    return request


@router.get("/requests", response_model=List[ProfileUpdateRequestOut])
def get_profile_update_requests(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all profile update requests (Super Admin only)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admin can view all requests",
        )

    # Fix: list_profile_update_requests takes only db argument, filter manually if needed
    requests = list_profile_update_requests(db)
    if status_filter:
        requests = [r for r in requests if r.status == status_filter]
    return requests


@router.put("/requests/{request_id}/approve", response_model=ProfileUpdateRequestOut)
def approve_profile_update_request(
    request_id: int,
    review: ProfileUpdateRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Approve a profile update request (Super Admin only)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admin can approve requests",
        )

    request = update_profile_update_request_status(
        db=db,
        request_id=request_id,
        status=RequestStatus.approved,
        reviewed_by_id=current_user.id,
        review_comment=review.review_comment,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
        )

    # If approved and it's an update, apply the changes
    if request.request_type == "update" and request.payload:
        update_employee_profile(
            db=db,
            user_id=request.user_id,
            company_id=request.user.company_id,
            **request.payload
        )
    elif request.request_type == "delete":
        # Soft delete: set is_active to False
        update_employee_profile(
            db=db,
            user_id=request.user_id,
            company_id=request.user.company_id,
            is_active=False,
        )

    return request


@router.put("/requests/{request_id}/reject", response_model=ProfileUpdateRequestOut)
def reject_profile_update_request(
    request_id: int,
    review: ProfileUpdateRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reject a profile update request (Super Admin only)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admin can reject requests",
        )

    request = update_profile_update_request_status(
        db=db,
        request_id=request_id,
        status=RequestStatus.rejected,
        reviewed_by_id=current_user.id,
        review_comment=review.review_comment,
    )
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request not found"
        )
    return request
