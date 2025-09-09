from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from ..deps import get_db, get_current_user
from ..schemas import UserCreate, UserUpdate, LoginPayload, Token, UserOut
from ..crud import create_user, authenticate_user, get_user_by_email, get_company_by_id, list_users_by_company, get_users_by_email, authenticate_user_by_email, get_user_by_email_only
from ..auth import create_access_token

class Notification(BaseModel):
    id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(tags=["Auth"])

@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email_only(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = create_user(
        db,
        payload.email,
        payload.password,
        payload.full_name or "",
        payload.role.value,
        payload.company_id  # Use company_id from payload
    )
    return user

@router.post("/login", response_model=Token)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = authenticate_user_by_email(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    access_token = create_access_token(
        sub=user.email, 
        company_id=user.company_id,  # May be None for Super Admin
        role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{company_id}", response_model=List[UserOut])
def get_users(company_id: int, db: Session = Depends(get_db)):
    return list_users_by_company(db, company_id)

from fastapi import Response

@router.get("/me", response_model=UserOut)
def get_current_user_profile(response: Response, current_user: UserOut = Depends(get_current_user)):
    """Get current authenticated user profile"""
    # Fix role value if invalid (e.g., 'user' instead of enum)
    valid_roles = {"SuperAdmin", "CompanyAdmin", "Manager", "Employee"}
    if current_user.role not in valid_roles:
        # Map invalid role to Employee as fallback
        current_user.role = "Employee"
    return current_user

@router.get("/me/profile")
def get_current_user_full_profile(db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """Get current authenticated user's full profile including employee details"""
    from ..crud import get_employee_profile_by_user_id

    user_profile = {
        "user": current_user,
        "employee_profile": None
    }

    # Get employee profile if it exists
    if current_user.company_id:
        employee_profile = get_employee_profile_by_user_id(db, current_user.id, current_user.company_id)
        if employee_profile:
            user_profile["employee_profile"] = employee_profile

    return user_profile

@router.get("/notifications", response_model=List[Notification])
def get_notifications(current_user: UserOut = Depends(get_current_user)):
    """Get user notifications"""
    # Mock notifications for now - will be replaced with real data later
    notifications = [
        {
            "id": 1,
            "title": "Welcome to Workforce App",
            "message": "Your account has been successfully created",
            "type": "info",
            "read": True,
            "created_at": datetime.now()
        },
        {
            "id": 2,
            "title": "New Task Assigned",
            "message": "You have been assigned a new task: 'Review quarterly reports'",
            "type": "task",
            "read": False,
            "created_at": datetime.now()
        },
        {
            "id": 3,
            "title": "System Update",
            "message": "Scheduled maintenance will occur tomorrow at 2:00 AM",
            "type": "system",
            "read": False,
            "created_at": datetime.now()
        }
    ]
    return notifications

@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """Update user information"""
    from ..crud import get_user_by_id, update_user

    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user with partial data
    updated_user = update_user(
        db,
        user_id,
        payload.email,
        payload.password,
        payload.full_name,
        payload.role.value if payload.role else None,
        payload.company_id
    )
    return updated_user

@router.put("/me/profile")
def update_current_user_profile(payload: dict, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """Update current user's profile including employee details"""
    from ..crud import get_employee_profile_by_user_id, update_employee_profile, update_user
    from ..schemas import EmployeeProfileUpdate
    import re
    from datetime import datetime

    # Update basic user info if provided
    user_update_data = payload.get("user", {})
    if user_update_data:
        update_user(
            db,
            current_user.id,
            user_update_data.get("email"),
            user_update_data.get("password"),
            user_update_data.get("full_name"),
            user_update_data.get("role"),
            user_update_data.get("company_id")
        )

    # Update employee profile if provided
    employee_update_data = payload.get("employee_profile", {})
    if employee_update_data and current_user.company_id:
        # Additional validation for phone number
        phone = employee_update_data.get("phone")
        if phone:
            phone_pattern = re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$')
            if not phone_pattern.match(phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format. Please use format: +1 (555) 123-4567 or similar"
                )

        # Validate hire date is not in the future
        hire_date = employee_update_data.get("hire_date")
        if hire_date:
            if isinstance(hire_date, str):
                hire_date = datetime.fromisoformat(hire_date.replace('Z', '+00:00')).date()
            if hire_date > datetime.now().date():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hire date cannot be in the future"
                )

        # Convert dict to EmployeeProfileUpdate
        employee_update = EmployeeProfileUpdate(**employee_update_data)
        update_employee_profile(
            db=db,
            user_id=current_user.id,
            company_id=current_user.company_id,
            department=employee_update.department,
            position=employee_update.position,
            phone=employee_update.phone,
            hire_date=employee_update.hire_date,
            manager_id=employee_update.manager_id,
            is_active=employee_update.is_active
        )

    # Return updated profile
    return get_current_user_full_profile(db, current_user)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """Delete user"""
    from ..crud import get_user_by_id, delete_user

    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}
