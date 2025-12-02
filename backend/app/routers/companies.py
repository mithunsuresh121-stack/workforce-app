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
    current_user: User = Depends(require_superadmin),
):
    """
    Create a new company with full bootstrap (only SuperAdmin can create companies)
    """

    # Check if company with same name already exists
    existing_company = get_company_by_name(db, company_data.name)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists",
        )

    try:
        # Bootstrap the company with all required components
        result = CompanyService.bootstrap_company(
            db=db, company_name=company_data.name, superadmin_user=current_user
        )

        return {
            "company": CompanyOut.from_orm(result["company"]),
            "first_admin_user": {
                "id": result["first_admin_user"].id,
                "email": result["first_admin_user"].email,
                "full_name": result["first_admin_user"].full_name,
                "role": result["first_admin_user"].role,
            },
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
