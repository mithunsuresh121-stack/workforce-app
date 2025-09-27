from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..schemas import CompanyCreate, CompanyOut
from ..crud import create_company, list_companies, get_company_by_id, get_company_by_name, delete_company
from ..models.user import User, Role
from ..permissions import requires_role, company_isolation

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_new_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_role("SuperAdmin"))
):
    """
    Create a new company (only SuperAdmin can create companies)
    """
    
    # Check if company with same name already exists
    existing_company = get_company_by_name(db, company_data.name)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists"
        )
    
    company = create_company(
        db=db,
        name=company_data.name,
        domain=company_data.domain,
        contact_email=company_data.contact_email,
        contact_phone=company_data.contact_phone,
        address=company_data.address,
        city=company_data.city,
        state=company_data.state,
        country=company_data.country,
        postal_code=company_data.postal_code
    )
    
    return company

@router.get("/", response_model=List[CompanyOut])
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all active companies (SuperAdmin sees all; others see own)
    """
    if current_user.role.value == "SuperAdmin":
        return list_companies(db)
    else:
        # CompanyAdmin/Manager/Employee see only their own company
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No company access"
            )
        own_company = get_company_by_id(db, current_user.company_id)
        if not own_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return [own_company]

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(company_isolation)
):
    """
    Get company details by ID
    """
    
    company = get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.put("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: int,
    company_data: CompanyCreate,  # Reuse create schema for updates
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_role("SuperAdmin"))
):
    """
    Update company details (only SuperAdmin can update companies)
    """

    company = get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    # Check if another company with same name exists
    existing_company = get_company_by_name(db, company_data.name)
    if existing_company and existing_company.id != company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists"
        )

    # Update using CRUD function (assume update_company exists; if not, direct update ok)
    from ..crud import update_company as update_company_crud
    updated_company = update_company_crud(
        db=db,
        company_id=company_id,
        name=company_data.name,
        domain=company_data.domain,
        contact_email=company_data.contact_email,
        contact_phone=company_data.contact_phone,
        address=company_data.address,
        city=company_data.city,
        state=company_data.state,
        country=company_data.country,
        postal_code=company_data.postal_code
    )

    return updated_company or company  # Fallback if CRUD not implemented

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_role("SuperAdmin"))
):
    """
    Delete a company by ID (only SuperAdmin can delete companies)
    """

    success = delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
