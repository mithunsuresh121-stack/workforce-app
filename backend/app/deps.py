from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.db import SessionLocal
from app.base_crud import get_user_by_email, get_user_by_email_only

import structlog
logger = structlog.get_logger(__name__)
logger.info("import_fix_applied", file="deps.py", status="success")

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_claims(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(db: Session = Depends(get_db), claims: dict = Depends(get_current_claims)):
    email = claims.get("sub")
    company_id = claims.get("company_id")

    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")

    from app.crud import get_user_by_email_only

    if company_id is None:
        user = get_user_by_email_only(db, email)
    else:
        user = get_user_by_email(db, email, company_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")

    return user
