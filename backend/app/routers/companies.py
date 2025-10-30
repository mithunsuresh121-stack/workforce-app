import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app.deps import get_db, get_current_user
from app.schemas import CompanyCreate, CompanyOut
from app.crud import create_company, list_companies, get_company_by_id, get_company_by_name, delete_company
from app.models.user import User

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
def create_new_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new company (only SuperAdmin can create companies)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SuperAdmin can create companies"
        )
    
    # Check if company with same name already exists
    existing_company = get_company_by_name(db, company_data.name)
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BORBIDDEN,
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
    Get list of all active companies (only SuperAdmin can see all companies)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SuperAdmin can view all companies"
        )
    
    return list_companies(db)

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get company details by ID
    """
    # Users can only access their own company unless they are SuperAdmin
    if current_user.role != "SuperAdmin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    company = get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_endpoint(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a company by ID (only SuperAdmin can delete companies)
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only SuperAdmin can delete companies"
        )
    
    success = delete_company(db, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
