from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from ..deps import get_db, get_current_user
from ..schemas import UserCreate, UserUpdate, LoginPayload, Token, UserOut
from ..crud import create_user, authenticate_user_by_email, get_user_by_email_only, get_user_by_id, get_company_by_id
from ..auth import create_access_token
from ..models.user import User

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
        role=user.role.value
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user profile"""
    # Fetch full user from db to ensure latest data
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Map role if invalid (fallback to Employee)
    valid_roles = {"SuperAdmin", "CompanyAdmin", "Manager", "Employee"}
    if user.role.value not in valid_roles:
        user.role = Role.EMPLOYEE

    # Fetch company if exists
    if user.company_id:
        company = get_company_by_id(db, user.company_id)
        if company:
            user.company = company

    return user
