from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..deps import get_db, get_current_user
from ..schemas import CompanyCreate, CompanyOut
from ..crud import create_company, list_companies, get_company_by_id, get_company_by_name, delete_company
from ..models.user import User

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

@router.get("/{company_id}/users")
def get_company_users(
    company_id: int,
    department: Optional[str] = None,
    position: Optional[str] = None,
    sort_by: Optional[str] = "full_name",
    sort_order: Optional[str] = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users for a company with optional filtering and sorting
    """
    from ..crud import list_users_by_company, list_employee_profiles_by_company
    from sqlalchemy import asc, desc

    # Users can only access their own company unless they are SuperAdmin
    if current_user.role != "SuperAdmin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    # Get users for the company
    users = list_users_by_company(db, company_id)

    # Get employee profiles for additional filtering
    employee_profiles = list_employee_profiles_by_company(db, company_id)

    # Create a mapping of user_id to employee_profile
    profile_map = {profile.user_id: profile for profile in employee_profiles}

    # Filter and sort users
    filtered_users = []
    for user in users:
        profile = profile_map.get(user.id)

        # Apply filters
        if department and profile and profile.department != department:
            continue
        if position and profile and profile.position != position:
            continue

        # Add profile data to user
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "company_id": user.company_id,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "employee_profile": profile
        }
        filtered_users.append(user_data)

    # Sort users
    if sort_by == "full_name":
        filtered_users.sort(key=lambda x: x["full_name"] or "", reverse=(sort_order == "desc"))
    elif sort_by == "role":
        filtered_users.sort(key=lambda x: x["role"], reverse=(sort_order == "desc"))
    elif sort_by == "department":
        filtered_users.sort(key=lambda x: x["employee_profile"].department if x["employee_profile"] else "", reverse=(sort_order == "desc"))
    elif sort_by == "position":
        filtered_users.sort(key=lambda x: x["employee_profile"].position if x["employee_profile"] else "", reverse=(sort_order == "desc"))

    return {
        "company_id": company_id,
        "total_users": len(filtered_users),
        "users": filtered_users
    }

@router.get("/{company_id}/departments")
def get_company_departments(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all unique departments for a company
    """
    from ..crud import list_employee_profiles_by_company

    # Users can only access their own company unless they are SuperAdmin
    if current_user.role != "SuperAdmin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    employee_profiles = list_employee_profiles_by_company(db, company_id)
    departments = set()
    for profile in employee_profiles:
        if profile.department:
            departments.add(profile.department)

    return {
        "company_id": company_id,
        "departments": sorted(list(departments))
    }

@router.get("/{company_id}/positions")
def get_company_positions(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all unique positions for a company
    """
    from ..crud import list_employee_profiles_by_company

    # Users can only access their own company unless they are SuperAdmin
    if current_user.role != "SuperAdmin" and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )

    employee_profiles = list_employee_profiles_by_company(db, company_id)
    positions = set()
    for profile in employee_profiles:
        if profile.position:
            positions.add(profile.position)

    return {
        "company_id": company_id,
        "positions": sorted(list(positions))
    }

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
