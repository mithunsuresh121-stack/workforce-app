import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..db import get_db
from ..crud_notification_preferences import (
    get_user_preferences,
    create_user_preferences,
    update_user_preferences,
    get_or_create_user_preferences
)
from ..deps import get_current_user

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/notification-preferences", tags=["Notification Preferences"])

@router.get("/")
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get notification preferences for the current user"""
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User must be associated with a company")

    preferences = get_or_create_user_preferences(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    return {"preferences": preferences.preferences}

@router.post("/")
def create_notification_preferences(
    preferences: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create notification preferences for the current user"""
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User must be associated with a company")

    # Check if preferences already exist
    existing = get_user_preferences(db, current_user.id, current_user.company_id)
    if existing:
        raise HTTPException(status_code=400, detail="Preferences already exist. Use PUT to update.")

    db_preferences = create_user_preferences(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        preferences=preferences
    )
    return {"message": "Preferences created", "preferences": db_preferences.preferences}

@router.put("/")
def update_notification_preferences(
    preferences: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update notification preferences for the current user"""
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User must be associated with a company")

    updated_preferences = update_user_preferences(
        db=db,
        user_id=current_user.id,
        company_id=current_user.company_id,
        preferences=preferences
    )
    if not updated_preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return {"message": "Preferences updated", "preferences": updated_preferences.preferences}

@router.delete("/")
def delete_notification_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete notification preferences for the current user (resets to defaults)"""
    if current_user.company_id is None:
        raise HTTPException(status_code=400, detail="User must be associated with a company")

    from ..crud_notification_preferences import delete_user_preferences
    success = delete_user_preferences(db, current_user.id, current_user.company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return {"message": "Preferences deleted and reset to defaults"}
