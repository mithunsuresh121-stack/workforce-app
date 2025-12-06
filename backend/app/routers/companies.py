from typing import Any, Dict, List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.rbac import require_company_access, require_superadmin
from app.crud import (create_company, delete_company, get_company_by_id,
                      get_company_by_name, list_companies)
from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import CompanyCreate, CompanyOut
from app.services.company_service import CompanyService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_new_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new company. If user has no company, they become SUPERADMIN of the new company.
    If user already has a company, they must be SUPERADMIN to create another.
    """

    # Check if user already has a company
    if current_user.company_id is not None:
        # If they have a company, check if they are SUPERADMIN
        if current_user.role != "SUPERADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only SUPERADMIN can create additional companies",
            )

    # Check if company with same name already exists
    existing_company = get_company_by_name(db, company_data.name)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists",
        )

    try:
        # Create the company
        new_company = create_company(db, company_data.name)

        # Assign the creator as SUPERADMIN of the new company
        from app.crud import update_user
        updated_user = update_user(
            db,
            current_user.id,
            current_user.email,
            None,  # password not changing
            current_user.full_name,
            "SUPERADMIN",
            new_company.id
        )

        # Bootstrap the company with all required components
        result = CompanyService.bootstrap_company(
            db=db, company=new_company, superadmin_user=updated_user
        )

        # Generate new access token with updated role and company_id
        from app.auth import create_access_token
        new_access_token = create_access_token(
            sub=updated_user.email,
            company_id=new_company.id,
            role="SUPERADMIN"
        )

        return {
            "company": CompanyOut.from_orm(result["company"]),
            "superadmin_user": {
                "id": updated_user.id,
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "role": "SUPERADMIN",
            },
            "new_access_token": new_access_token,
            "bootstrap_status": result["bootstrap_status"],
            "temporary_access_link": result["temporary_access_link"],
            "token_expiry": result["token_expiry"],
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[CompanyOut])
def get_companies(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get list of all active companies (only SuperAdmin can see all companies)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SuperAdmin can view all companies",
        )

    return list_companies(db)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get company details by ID
    """
    # Users can only access their own company unless they are SuperAdmin
    if current_user.role != "SuperAdmin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company",
        )

    company = get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    return company


@router.post("/{company_id}/assign-user", response_model=Dict[str, Any])
def assign_user_to_company(
    company_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = payload.get("user_id")
    role = payload.get("role")
    """
    Assign a user to the company with a specific role. Only SUPERADMIN of the company can assign users.
    """
    # Check if current user is SUPERADMIN of this company
    if current_user.company_id != company_id or current_user.role != "SUPERADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SUPERADMIN of the company can assign users",
        )

    # Get the user to assign
    from app.crud import get_user_by_id
    user_to_assign = get_user_by_id(db, user_id)
    if not user_to_assign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if user is already assigned to another company
    if user_to_assign.company_id is not None and user_to_assign.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already assigned to another company",
        )

    # Validate role
    from app.schemas import Role
    if role not in [r.value for r in Role]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in Role])}",
        )

    # Update user
    from app.crud import update_user
    updated_user = update_user(
        db,
        user_id,
        user_to_assign.email,
        None,  # password not changing
        user_to_assign.full_name,
        role,
        company_id
    )

    return {
        "message": "User assigned to company successfully",
        "user": {
            "id": updated_user.id,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "role": updated_user.role,
            "company_id": updated_user.company_id,
        }
    }


@router.get("/user", response_model=List[CompanyOut])
def get_user_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get companies accessible by the current user.
    - If user is SUPERADMIN: return all companies
    - Otherwise: return the user's assigned company if exists
    """
    if current_user.role == "SUPERADMIN":
        return list_companies(db)
    else:
        if current_user.company_id:
            company = get_company_by_id(db, current_user.company_id)
            return [company] if company else []
        return []


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a company by ID (only SuperAdmin can delete companies)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SuperAdmin can delete companies",
        )

    success = delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
