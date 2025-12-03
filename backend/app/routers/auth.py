from datetime import datetime, timedelta
from typing import List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.auth import create_refresh_token as auth_create_refresh_token
from app.auth import verify_refresh_token
from app.crud import (authenticate_user, authenticate_user_by_email,
                      create_refresh_token, create_user, get_company_by_id,
                      get_refresh_token_by_token, get_user_by_email,
                      get_user_by_email_only, get_users_by_email,
                      list_users_by_company, revoke_all_user_refresh_tokens,
                      revoke_refresh_token)
from app.deps import get_current_user, get_db
from app.schemas import (LoginPayload, RefreshTokenRequest, Token, UserCreate,
                         UserOut, UserUpdate)
from app.services.email_service import email_service
from app.services.fcm_service import fcm_service

logger = structlog.get_logger(__name__)


def determine_company_and_role(email_domain: str, payload: UserCreate, db: Session) -> tuple[Optional[int], str]:
    """Determine company_id and role based on email domain."""
    generic_domains = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"
    }
    if email_domain in generic_domains:
        return None, "EMPLOYEE"

    company_name = email_domain.replace(".", " ").title()
    existing_company = get_company_by_name(db, company_name)
    if existing_company:
        return existing_company.id, "EMPLOYEE"

    new_company = create_company(db, company_name)
    return new_company.id, "COMPANY_ADMIN"


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = get_user_by_email_only(db, payload.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Extract domain from email
    email_domain = payload.email.split("@")[-1].lower()

    company_id, role = determine_company_and_role(email_domain, payload, db)

    user = create_user(
        db, payload.email, payload.password, payload.full_name or "", role, company_id
    )

    # Send welcome email
    try:
        # Get company name if available
        company_name = "Your Company"
        if user.company_id:
            company = get_company_by_id(db, user.company_id)
            if company:
                company_name = company.name
        email_service.send_welcome_email(
            user.email, user.full_name or user.email, company_name
        )
    except Exception as e:
        logger.warning(
            "Failed to send welcome email", error=str(e), user_email=user.email
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
        role=user.role,
    )

    refresh_token_str = auth_create_refresh_token(
        sub=user.email, company_id=user.company_id, role=user.role
    )

    # Store refresh token in database
    expires_at = datetime.utcnow() + timedelta(days=7)
    create_refresh_token(db, user.id, refresh_token_str, expires_at)

    logger.info("User logged in", user_email=user.email, user_id=user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


@router.get("/users/{company_id}", response_model=List[UserOut])
def get_users(company_id: int, db: Session = Depends(get_db)):
    return list_users_by_company(db, company_id)


from fastapi import Response


@router.get("/me", response_model=UserOut)
def get_current_user_profile(current_user: UserOut = Depends(get_current_user)):
    """Get current authenticated user profile"""
    # Use enum for roles (assume from schemas.Role)
    from app.schemas import Role

    valid_roles = {role.value for role in Role}
    if current_user.role not in valid_roles:
        current_user.role = Role.EMPLOYEE.value

    # Include company information if user has a company_id
    if current_user.company_id:
        company = get_company_by_id(next(get_db()), current_user.company_id)
        if company:
            current_user.company = company

    return current_user


# Removed dead/mock get_notifications endpoint and Notification class


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
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
        payload.company_id,
    )
    return updated_user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Delete user"""
    from app.crud import delete_user, get_user_by_id

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
            sub=user_email, company_id=company_id, role=role
        )
        new_refresh_token_str = auth_create_refresh_token(
            sub=user_email, company_id=company_id, role=role
        )

        # Store new refresh token
        expires_at = datetime.utcnow() + timedelta(days=7)
        create_refresh_token(db, user.id, new_refresh_token_str, expires_at)

        logger.info("Token refreshed", user_email=user_email, user_id=user.id)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token_str,
            "token_type": "bearer",
        }

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
    current_user: UserOut = Depends(get_current_user),
):
    """Update FCM token for push notifications"""
    success = fcm_service.update_user_fcm_token(db, current_user.id, payload.fcm_token)
    if success:
        logger.info("FCM token updated", user_id=current_user.id)
        return {"message": "FCM token updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update FCM token")


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
def forgot_password(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    user = get_user_by_email_only(db, payload.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}

    # Generate reset token (simplified - in production use proper JWT)
    import secrets

    reset_token = secrets.token_urlsafe(32)

    # Store reset token in database with expiry (1 hour)
    from datetime import datetime, timedelta

    from app.models.reset_token import ResetToken

    expires_at = datetime.utcnow() + timedelta(hours=1)
    db_reset_token = ResetToken(
        user_id=user.id, token=reset_token, expires_at=expires_at
    )
    db.add(db_reset_token)
    db.commit()

    # Send email
    try:
        email_service.send_password_reset_email(
            user.email, reset_token, user.full_name or user.email
        )
        logger.info("Password reset email sent", user_email=user.email)
    except Exception as e:
        logger.error(
            "Failed to send password reset email", error=str(e), user_email=user.email
        )
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token"""
    from datetime import datetime

    from app.auth import hash_password
    from app.crud import update_user_password
    from app.models.reset_token import ResetToken

    # Verify token exists and not expired
    reset_token = (
        db.query(ResetToken)
        .filter(
            ResetToken.token == payload.token, ResetToken.expires_at > datetime.utcnow()
        )
        .first()
    )

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Update password
        try:
            update_user_password(db, reset_token.user_id, payload.new_password)
            # Mark token as used
            reset_token.used = True
            db.commit()
            logger.info("Password reset successful", user_id=reset_token.user_id)
            return {"message": "Password reset successfully"}
        except Exception as e:
            db.rollback()
            logger.error(
                "Password reset failed", error=str(e), user_id=reset_token.user_id
            )
            raise HTTPException(status_code=500, detail="Failed to reset password")
