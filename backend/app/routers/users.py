from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..deps import get_db, get_current_user
from ..schemas import EmployeeUserOut, UserCreate, UserUpdate, UserOut
from ..crud import create_user, get_user_by_id, update_user, delete_user, list_users_by_company
from ..models.user import User, Role
from ..permissions import has_permission, require_permission, company_isolation

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user.create"))
):
    """
    Create a new user (CompanyAdmin and SuperAdmin only)
    """

    # Validate role logic
    if current_user.role == Role.COMPANYADMIN:
        # CompanyAdmin can only create Employees and Managers in their company
        if user_data.role not in [Role.EMPLOYEE, Role.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CompanyAdmin can only create Employee or Manager roles"
            )
        if user_data.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create users for other companies"
            )
    elif current_user.role == Role.SUPERADMIN:
        # SuperAdmin can create any role, including CompanyAdmin
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create users"
        )

    # Check if user already exists
    from ..crud import get_user_by_email_only
    existing_user = get_user_by_email_only(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    user = create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role.value,
        company_id=user_data.company_id
    )

    return user

@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all users for the current user's company.
    SuperAdmin can see all users across companies.
    """
    if current_user.role == Role.SUPERADMIN:
        # SuperAdmin sees all users
        users = db.query(User).all()
    else:
        # Others see only their company users
        users = list_users_by_company(db, current_user.company_id)

    return users

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user details by ID
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check company isolation (unless SuperAdmin)
    if current_user.role != Role.SUPERADMIN and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user information
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions and company isolation
    if current_user.role != Role.SUPERADMIN and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    # Only allow self-update for non-admin roles, or admin permissions
    if current_user.id != user_id and not has_permission(current_user, "user.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update this user"
        )

    # Validate role changes (similar to create)
    if user_data.role and current_user.role == Role.COMPANYADMIN:
        if user_data.role not in [Role.EMPLOYEE, Role.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CompanyAdmin can only assign Employee or Manager roles"
            )

    updated_user = update_user(
        db=db,
        user_id=user_id,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role.value if user_data.role else None,
        company_id=user_data.company_id
    )

    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user (CompanyAdmin and SuperAdmin only)
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check permissions and company isolation
    if current_user.role != Role.SUPERADMIN and user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this user"
        )

    if not has_permission(current_user, "user.delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete users"
        )

    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/employees", response_model=List[EmployeeUserOut])
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all employees for the current user's company.
    SuperAdmin can see all employees across companies.
    """
    query = db.query(User).filter(
        User.role == Role.EMPLOYEE,
        User.is_active == True
    )
    if current_user.role != Role.SUPERADMIN:
        query = query.filter(User.company_id == current_user.company_id)

    employees = query.all()

    # Map to EmployeeUserOut
    result = []
    for emp in employees:
        result.append(EmployeeUserOut(
            id=emp.id,
            name=emp.full_name or emp.email,  # Use full_name if available, else email
            email=emp.email
        ))

    return result
