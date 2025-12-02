import secrets
from datetime import datetime, timedelta

import bcrypt
import structlog
from jose import jwt

from app.config import settings

logger = structlog.get_logger(__name__)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(
    sub: str, company_id: int | None, role: str, expires_minutes: int = 15
) -> str:
    payload = {
        "sub": sub,
        "company_id": company_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    logger.info(
        "Access token created",
        user_email=sub,
        company_id=company_id,
        role=role,
        expires_minutes=expires_minutes,
    )
    return token


def create_refresh_token(sub: str, company_id: int | None, role: str) -> str:
    # Generate a unique token identifier to avoid duplicates
    token_id = secrets.token_urlsafe(32)
    payload = {
        "sub": sub,
        "company_id": company_id,
        "role": role,
        "type": "refresh",
        "token_id": token_id,
        "exp": datetime.utcnow() + timedelta(days=7),  # 7 days expiry
    }
    token = jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=settings.JWT_ALG)
    logger.info(
        "Refresh token created",
        user_email=sub,
        company_id=company_id,
        role=role,
        token_id=token_id,
    )
    return token


def verify_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.JWT_REFRESH_SECRET, algorithms=[settings.JWT_ALG]
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning(
            "Refresh token expired",
            token_sub=payload.get("sub") if "payload" in locals() else None,
        )
        return None
    except jwt.JWTError as e:
        logger.error("Invalid refresh token", error=str(e))
        return None
