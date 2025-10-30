from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.deps import get_db, get_current_user
from app.schemas import UserCreate, UserUpdate, LoginPayload, Token, UserOut, RefreshTokenRequest
from app.crud import create_user, authenticate_user, get_user_by_email, get_company_by_id, list_users_by_company, get_users_by_email, authenticate_user_by_email, get_user_by_email_only, create_refresh_token, get_refresh_token_by_token, revoke_refresh_token, revoke_all_user_refresh_tokens
from app.auth import create_access_token, create_refresh_token as auth_create_refresh_token, verify_refresh_token
from app.services.fcm_service import fcm_service
import structlog

logger = structlog.get_logger(__name__)

class Notification(BaseModel):
    id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

router = APIRouter(prefix="/auth", tags=["Auth"])

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

    refresh_token_str = auth_create_refresh_token(
        sub=user.email,
        company_id=user.company_id,
        role=user.role
    )

    # Store refresh token in database
    expires_at = datetime.utcnow() + timedelta(days=7)
    create_refresh_token(db, user.id, refresh_token_str, expires_at)

    logger.info("User logged in", user_email=user.email, user_id=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token_str, "token_type": "bearer"}

@router.get("/users/{company_id}", response_model=List[UserOut])
def get_users(company_id: int, db: Session = Depends(get_db)):
    return list_users_by_company(db, company_id)

from fastapi import Response

@router.get("/me", response_model=UserOut)
def get_current_user_profile(response: Response, current_user: UserOut = Depends(get_current_user)):
    """Get current authenticated user profile"""
    # Fix role value if invalid (e.g., 'user' instead of enum)
    valid_roles = {"SUPERADMIN", "COMPANYADMIN", "MANAGER", "EMPLOYEE"}
    if current_user.role not in valid_roles:
        # Map invalid role to Employee as fallback
        current_user.role = "EMPLOYEE"

    # Include company information if user has a company_id
    if current_user.company_id:
        from app.crud import get_company_by_id
        from app.deps import get_db
        from sqlalchemy.orm import Session

        # Create a new session to get company data
        db = next(get_db())
        try:
            company = get_company_by_id(db, current_user.company_id)
            if company:
                current_user.company = company
        except Exception:
            # If there's an error getting company data, continue without it
            pass

    return current_user

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
    from app.crud import get_user_by_id, update_user

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

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    """Delete user"""
    from app.crud import get_user_by_id, delete_user

    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    delete_user(db, user_id)
    return {"message": "User deleted successfully"}

@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token exists in database and is not revoked
        stored_token = get_refresh_token_by_token(db, payload.refresh_token)
        if not stored_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Verify JWT token
        jwt_payload = verify_refresh_token(payload.refresh_token)
        if not jwt_payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_email = jwt_payload.get("sub")
        company_id = jwt_payload.get("company_id")
        role = jwt_payload.get("role")

        # Verify user still exists and is active
        user = get_user_by_email_only(db, user_email)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Revoke old refresh token
        revoke_refresh_token(db, payload.refresh_token)

        # Create new tokens
        access_token = create_access_token(
            sub=user_email,
            company_id=company_id,
            role=role
        )
        new_refresh_token_str = auth_create_refresh_token(
            sub=user_email,
            company_id=company_id,
            role=role
        )

        # Store new refresh token
        expires_at = datetime.utcnow() + timedelta(days=7)
        create_refresh_token(db, user.id, new_refresh_token_str, expires_at)

        logger.info("Token refreshed", user_email=user_email, user_id=user.id)
        return {"access_token": access_token, "refresh_token": new_refresh_token_str, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid refresh token")

class FCMTokenUpdate(BaseModel):
    fcm_token: str

@router.post("/update-fcm-token")
def update_fcm_token(
    payload: FCMTokenUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    """Update FCM token for push notifications"""
    success = fcm_service.update_user_fcm_token(db, current_user.id, payload.fcm_token)
    if success:
        logger.info("FCM token updated", user_id=current_user.id)
        return {"message": "FCM token updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update FCM token")
