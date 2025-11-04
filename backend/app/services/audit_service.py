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

    @staticmethod
    def log_admin_action(db: Session, action: str, user_id: int, company_id: int = None, details: dict = None):
        """Log admin action for observability"""
        AuditService.log_event(
            db=db,
            event_type=f"ADMIN_{action.upper()}",
            user_id=user_id,
            company_id=company_id,
            resource_type="admin",
            resource_id=None,
            details=details or {}
        )

    @staticmethod
    def log_org_created(db: Session, user_id: int, company_id: int, resource_type: str, resource_id: int, details: dict = None):
        """Log organization creation events"""
        AuditService.log_event(
            db=db,
            event_type="ORG_CREATED",
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {}
        )

    @staticmethod
    def log_channel_created(db: Session, user_id: int, company_id: int, channel_id: int, details: dict = None):
        """Log channel creation events"""
        AuditService.log_event(
            db=db,
            event_type="CHANNEL_CREATED",
            user_id=user_id,
            company_id=company_id,
            resource_type="channel",
            resource_id=channel_id,
            details=details or {}
        )

    @staticmethod
    def log_meeting_created(db: Session, user_id: int, company_id: int, meeting_id: int, details: dict = None):
        """Log meeting creation events"""
        AuditService.log_event(
            db=db,
            event_type="MEETING_CREATED",
            user_id=user_id,
            company_id=company_id,
            resource_type="meeting",
            resource_id=meeting_id,
            details=details or {}
        )

    @staticmethod
    def log_user_assigned_role(db: Session, user_id: int, target_user_id: int, company_id: int, role: str, details: dict = None):
        """Log user role assignment events"""
        AuditService.log_event(
            db=db,
            event_type="USER_ASSIGNED_ROLE",
            user_id=user_id,
            company_id=company_id,
            resource_type="user",
            resource_id=target_user_id,
            details={"assigned_role": role, **(details or {})}
        )

    @staticmethod
    def log_permission_denied(db: Session, user_id: int, company_id: int, action: str, resource_type: str = None, resource_id: int = None, details: dict = None):
        """Log permission denial events"""
        AuditService.log_event(
            db=db,
            event_type="PERMISSION_DENIED",
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"denied_action": action, **(details or {})}
        )

    @staticmethod
    def log_user_invited(db: Session, user_id: int, target_user_id: int, company_id: int, resource_type: str, resource_id: int, details: dict = None):
        """Log user invitation events"""
        AuditService.log_event(
            db=db,
            event_type="USER_INVITED",
            user_id=user_id,
            company_id=company_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"invited_user_id": target_user_id, **(details or {})}
        )

    @staticmethod
    def log_auth_failure(db: Session, user_id: int, company_id: int = None, details: dict = None, ip_address: str = None, user_agent: str = None):
        """Log authentication failure events"""
        from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity

        # Check for anomalies
        escalated_severity = SecurityService.check_anomaly_rules(db, user_id, SecurityEvent.AUTH_FAILURE, details)

        SecurityService.log_security_event(
            db=db,
            event_type=SecurityEvent.AUTH_FAILURE,
            user_id=user_id,
            company_id=company_id,
            severity=escalated_severity or SecuritySeverity.LOW,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def log_role_attempt(db: Session, user_id: int, target_user_id: int, company_id: int, attempted_role: str, details: dict = None):
        """Log role change attempt events"""
        from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity

        # Check for superadmin downgrade
        escalated_severity = SecurityService.check_anomaly_rules(
            db, user_id, SecurityEvent.ROLE_ATTEMPT,
            {"target_role": attempted_role, "action": "downgrade" if attempted_role != "SUPERADMIN" else "attempt"}
        )

        SecurityService.log_security_event(
            db=db,
            event_type=SecurityEvent.ROLE_ATTEMPT,
            user_id=user_id,
            company_id=company_id,
            severity=escalated_severity or SecuritySeverity.MEDIUM,
            details={"target_user_id": target_user_id, "attempted_role": attempted_role, **(details or {})},
        )

    @staticmethod
    def log_cross_org_access(db: Session, user_id: int, attempted_company_id: int, action: str, details: dict = None):
        """Log cross-organization access attempts"""
        from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity

        # Check for repeated attempts
        escalated_severity = SecurityService.check_anomaly_rules(db, user_id, SecurityEvent.CROSS_ORG_ACCESS, details)

        SecurityService.log_security_event(
            db=db,
            event_type=SecurityEvent.CROSS_ORG_ACCESS,
            user_id=user_id,
            company_id=attempted_company_id,
            severity=escalated_severity or SecuritySeverity.MEDIUM,
            details={"action": action, **(details or {})},
        )

    @staticmethod
    def log_admin_impersonation(db: Session, user_id: int, target_user_id: int, company_id: int, details: dict = None):
        """Log admin impersonation attempts"""
        from app.services.security_service import SecurityService, SecurityEvent, SecuritySeverity

        SecurityService.log_security_event(
            db=db,
            event_type=SecurityEvent.ADMIN_IMPERSONATION,
            user_id=user_id,
            company_id=company_id,
            severity=SecuritySeverity.HIGH,
            details={"target_user_id": target_user_id, **(details or {})},
        )

    @staticmethod
    def log_ai_event(
        db: Session,
        user_id: int,
        company_id: int,
        request_text: str,
        capability: str,
        decision: str,
        scope_valid: bool,
        required_role: str,
        user_role: str,
        severity: str = "low",
        details: dict = None
    ):
        """Log AI request events"""
        audit_log = AuditLog(
            event_type="AI_REQUEST",
            user_id=user_id,
            company_id=company_id,
            resource_type="ai",
            resource_id=None,
            details=details or {},
            ai_request_text=request_text,
            ai_capability=capability,
            ai_decision=decision,
            ai_scope_valid=scope_valid,
            ai_required_role=required_role,
            ai_user_role=user_role,
            ai_severity=severity
        )
        db.add(audit_log)
        db.commit()
        logger.info(
            "AI event logged",
            user_id=user_id,
            company_id=company_id,
            capability=capability,
            decision=decision,
            severity=severity
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
