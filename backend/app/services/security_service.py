import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

import structlog
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)


class SecurityEvent(str, Enum):
    AUTH_FAILURE = "AUTH_FAILURE"
    ROLE_ATTEMPT = "ROLE_ATTEMPT"
    CROSS_ORG_ACCESS = "CROSS_ORG_ACCESS"
    LOCKOUT = "LOCKOUT"
    ADMIN_IMPERSONATION = "ADMIN_IMPERSONATION"
    AI_CROSS_ORG = "AI_CROSS_ORG"
    AI_UNAUTHORIZED_CAPABILITY = "AI_UNAUTHORIZED_CAPABILITY"
    AI_ADMIN_NO_SIGNOFF = "AI_ADMIN_NO_SIGNOFF"


class SecuritySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityService:
    # Configuration
    LOCKOUT_DURATION_MINUTES = 15
    MAX_FAILED_LOGINS = 5
    CROSS_ORG_THRESHOLD = 3  # Number of cross-org attempts before high severity

    @staticmethod
    def log_security_event(
        db: Session,
        event_type: SecurityEvent,
        user_id: int,
        company_id: int = None,
        severity: SecuritySeverity = SecuritySeverity.LOW,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None,
    ):
        """Log a security event to multiple streams"""
        event_data = {
            "event_type": event_type.value,
            "severity": severity.value,
            "user_id": user_id,
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # Log to database via AuditService
        AuditService.log_event(
            db=db,
            event_type=f"SECURITY_{event_type.value}",
            user_id=user_id,
            company_id=company_id,
            resource_type="security",
            resource_id=None,
            details={"severity": severity.value, **(details or {})},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Log to stdout
        logger.warning(
            "Security event",
            event_type=event_type.value,
            severity=severity.value,
            user_id=user_id,
            company_id=company_id,
            details=details,
        )

        # Log to file
        SecurityService._log_to_file(event_data)

    @staticmethod
    def _log_to_file(event_data: dict):
        """Log security event to file"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "security_events.log")

        with open(log_file, "a") as f:
            f.write(json.dumps(event_data) + "\n")

    @staticmethod
    def check_anomaly_rules(
        db: Session, user_id: int, event_type: SecurityEvent, details: dict = None
    ) -> Optional[SecuritySeverity]:
        """Check for security anomalies and return escalated severity if triggered"""
        if event_type == SecurityEvent.AUTH_FAILURE:
            # Check for 5 failed logins
            recent_failures = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id == user_id,
                    AuditLog.event_type
                    == f"SECURITY_{SecurityEvent.AUTH_FAILURE.value}",
                    AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                )
                .count()
            )

            if (
                recent_failures >= SecurityService.MAX_FAILED_LOGINS - 1
            ):  # -1 because current event not yet counted
                SecurityService.lock_account(
                    db,
                    user_id,
                    f"Too many failed login attempts ({recent_failures + 1})",
                )
                return SecuritySeverity.HIGH

        elif event_type == SecurityEvent.CROSS_ORG_ACCESS:
            # Check for repeated cross-org attempts
            recent_cross_org = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id == user_id,
                    AuditLog.event_type
                    == f"SECURITY_{SecurityEvent.CROSS_ORG_ACCESS.value}",
                    AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                )
                .count()
            )

            if (
                recent_cross_org >= SecurityService.CROSS_ORG_THRESHOLD - 1
            ):  # -1 because current event not yet counted
                return SecuritySeverity.HIGH

        elif event_type == SecurityEvent.ROLE_ATTEMPT:
            # Check for superadmin downgrade attempt
            if details and details.get("attempted_role") != UserRole.SUPERADMIN.value:
                # Check if target user is superadmin
                target_user_id = details.get("target_user_id")
                if target_user_id:
                    target_user = (
                        db.query(User).filter(User.id == target_user_id).first()
                    )
                    if target_user and target_user.role == UserRole.SUPERADMIN:
                        return SecuritySeverity.CRITICAL

        elif event_type == SecurityEvent.AI_CROSS_ORG:
            # Check for repeated AI cross-org attempts
            recent_ai_cross_org = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id == user_id,
                    AuditLog.event_type.like("SECURITY_AI_%"),
                    AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                )
                .count()
            )

            if recent_ai_cross_org >= 3:  # Threshold for AI abuse
                return SecuritySeverity.HIGH

        elif event_type == SecurityEvent.AI_UNAUTHORIZED_CAPABILITY:
            # Check for repeated unauthorized AI capability attempts
            recent_unauth = (
                db.query(AuditLog)
                .filter(
                    AuditLog.user_id == user_id,
                    AuditLog.event_type
                    == f"SECURITY_{SecurityEvent.AI_UNAUTHORIZED_CAPABILITY.value}",
                    AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                )
                .count()
            )

            if recent_unauth >= 5:  # Higher threshold for capability abuse
                return SecuritySeverity.HIGH

        return None  # No anomaly detected

    @staticmethod
    def lock_account(db: Session, user_id: int, reason: str):
        """Lock user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=SecurityService.LOCKOUT_DURATION_MINUTES
            )
            db.commit()

            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.LOCKOUT,
                user_id=user_id,
                company_id=user.company_id,
                severity=SecuritySeverity.MEDIUM,
                details={
                    "reason": reason,
                    "locked_until": user.locked_until.isoformat(),
                },
            )

    @staticmethod
    def unlock_account(db: Session, user_id: int, unlocked_by: int):
        """Unlock user account (admin action)"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_locked = False
            user.locked_until = None
            db.commit()

            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.LOCKOUT,
                user_id=user_id,
                company_id=user.company_id,
                severity=SecuritySeverity.LOW,
                details={"action": "unlocked", "unlocked_by": unlocked_by},
            )

    @staticmethod
    def is_account_locked(user: User) -> bool:
        """Check if account is currently locked"""
        if not user.is_locked:
            return False

        if user.locked_until and datetime.utcnow() > user.locked_until:
            # Auto-unlock expired lockouts
            return False

        return user.is_locked

    @staticmethod
    def get_security_alerts(
        db: Session, company_id: Optional[int] = None, limit: int = 50
    ) -> List[Dict]:
        """Get recent security alerts"""
        query = db.query(AuditLog).filter(AuditLog.event_type.like("SECURITY_%"))

        if company_id:
            query = query.filter(AuditLog.company_id == company_id)

        alerts = query.order_by(AuditLog.created_at.desc()).limit(limit).all()

        return [
            {
                "id": alert.id,
                "event_type": alert.event_type,
                "user_id": alert.user_id,
                "company_id": alert.company_id,
                "details": alert.details,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in alerts
        ]


# Convenience functions
def log_security_event(
    event_type: SecurityEvent,
    user_id: int,
    company_id: int = None,
    severity: SecuritySeverity = SecuritySeverity.LOW,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None,
):
    """Convenience function to log security events"""
    db = SessionLocal()
    try:
        SecurityService.log_security_event(
            db=db,
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            severity=severity,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    finally:
        db.close()


def check_account_lock(user: User) -> bool:
    """Convenience function to check if account is locked"""
    return SecurityService.is_account_locked(user)
