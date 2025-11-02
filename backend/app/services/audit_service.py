import structlog
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.audit_log import AuditLog

logger = structlog.get_logger(__name__)

class AuditService:
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        user_id: int,
        company_id: int = None,
        resource_type: str = None,
        resource_id: int = None,
        details: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log an audit event"""
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        logger.info(
            "Audit event logged",
            event_type=event_type,
            user_id=user_id,
            company_id=company_id
        )

    @staticmethod
    def log_company_bootstrapped(db: Session, user_id: int, company_id: int, details: dict = None):
        """Log company bootstrap event"""
        AuditService.log_event(
            db=db,
            event_type="COMPANY_BOOTSTRAPPED",
            user_id=user_id,
            company_id=company_id,
            resource_type="company",
            resource_id=company_id,
            details=details or {}
        )

# Convenience functions
def log_audit_event(
    event_type: str,
    user_id: int,
    company_id: int = None,
    resource_type: str = None,
    resource_id: int = None,
    details: dict = None,
    ip_address: str = None,
    user_agent: str = None
):
    """Convenience function to log audit events"""
    db = SessionLocal()
    try:
        AuditService.log_event(
            db=db,
            event_type=event_type,
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    finally:
        db.close()

def log_company_bootstrapped(user_id: int, company_id: int, details: dict = None):
    """Convenience function to log company bootstrap"""
    db = SessionLocal()
    try:
        AuditService.log_company_bootstrapped(db, user_id, company_id, details)
    finally:
        db.close()
