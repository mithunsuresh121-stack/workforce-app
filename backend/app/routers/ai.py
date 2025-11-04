from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.ai import AIQueryRequest, AIQueryResponse
from app.services.ai_service import AIService
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/query", response_model=AIQueryResponse)
def ai_query(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process AI query with security validation and logging"""
    try:
        response = AIService.process_ai_query(db, current_user, request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query processing failed: {str(e)}")
