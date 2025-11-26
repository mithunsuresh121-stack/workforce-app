import structlog
import requests
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.ai import WebhookAlertConfig, AIPolicySeverity
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService, SecuritySeverity

logger = structlog.get_logger(__name__)

class ThreatMonitorService:
    @staticmethod
    def get_live_violations(db: Session, company_id: int = None, limit: int = 50) -> list:
        """Get live feed of recent AI violations and anomalies"""
        query = db.query(AuditLog).filter(
            AuditLog.event_type.like("SECURITY_AI_%")
        ).order_by(AuditLog.created_at.desc())

        if company_id:
            query = query.filter(AuditLog.company_id == company_id)

        violations = query.limit(limit).all()

        return [{
            "id": v.id,
            "event_type": v.event_type,
            "user_id": v.user_id,
            "company_id": v.company_id,
            "details": v.details,
            "severity": v.details.get("severity", "LOW") if v.details else "LOW",
            "created_at": v.created_at.isoformat(),
            "user_email": v.user.email if v.user else None
        } for v in violations]

    @staticmethod
    def get_risk_heatmap(db: Session, company_id: int = None, time_range_hours: int = 24) -> dict:
        """Generate risk heat map data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)

        query = db.query(
            AuditLog.details['severity'].label('severity'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.event_type.like("SECURITY_AI_%"),
            AuditLog.created_at >= cutoff_time
        ).group_by(AuditLog.details['severity'])

        if company_id:
            query = query.filter(AuditLog.company_id == company_id)

        results = query.all()

        heatmap = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }

        for result in results:
            severity = result.severity.upper() if result.severity else "LOW"
            heatmap[severity] = result.count

        return heatmap

    @staticmethod
    def check_threshold_alerts(db: Session, company_id: int = None) -> list:
        """Check for threshold breaches that should trigger alerts"""
        alerts = []

        # Check for high volume of violations in short time
        cutoff_time = datetime.utcnow() - timedelta(hours=1)

        high_severity_count = db.query(AuditLog).filter(
            AuditLog.event_type.like("SECURITY_AI_%"),
            AuditLog.details['severity'].astext.in_(['HIGH', 'CRITICAL']),
            AuditLog.created_at >= cutoff_time
        )

        if company_id:
            high_severity_count = high_severity_count.filter(AuditLog.company_id == company_id)

        count = high_severity_count.count()

        if count >= 10:  # Threshold for alert
            alerts.append({
                "type": "HIGH_VOLUME_VIOLATIONS",
                "severity": "CRITICAL",
                "message": f"High volume of AI violations detected: {count} in last hour",
                "details": {"violation_count": count, "time_range": "1 hour"}
            })

        # Check for individual user abuse
        user_violations = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('violation_count')
        ).filter(
            AuditLog.event_type.like("SECURITY_AI_%"),
            AuditLog.created_at >= cutoff_time
        ).group_by(AuditLog.user_id).having(func.count(AuditLog.id) >= 5).all()

        for user_id, count in user_violations:
            user = db.query(User).filter(User.id == user_id).first()
            alerts.append({
                "type": "USER_ABUSE_DETECTED",
                "severity": "HIGH",
                "message": f"User {user.email if user else user_id} has {count} violations in last hour",
                "details": {"user_id": user_id, "violation_count": count, "user_email": user.email if user else None}
            })

        return alerts

    @staticmethod
    def send_webhook_alert(webhook_config: WebhookAlertConfig, alert_data: dict) -> bool:
        """Send alert via webhook"""
        if not webhook_config.enabled:
            return False

        # Check if alert severity matches configured alert types
        if alert_data.get("severity") not in webhook_config.alert_types:
            return False

        try:
            headers = webhook_config.headers or {}
            headers["Content-Type"] = "application/json"

            payload = {
                "alert_type": alert_data["type"],
                "severity": alert_data["severity"],
                "message": alert_data["message"],
                "details": alert_data["details"],
                "timestamp": datetime.utcnow().isoformat()
            }

            response = requests.post(
                webhook_config.url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Webhook alert sent successfully", url=webhook_config.url, alert_type=alert_data["type"])
                return True
            else:
                logger.error("Webhook alert failed",
                            url=webhook_config.url,
                            status_code=response.status_code,
                            response=response.text)
                return False

        except Exception as e:
            logger.error("Webhook alert exception", url=webhook_config.url, error=str(e))
            return False

    @staticmethod
    def auto_throttle_user(db: Session, user_id: int, violation_count: int) -> bool:
        """Auto-throttle abusive user based on violation patterns"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # Calculate throttling level based on violation count
        if violation_count >= 10:
            # Severe throttling - reduce trust score significantly
            from app.services.trust_service import TrustService
            TrustService.update_trust_score(
                db, user_id, None, AIPolicySeverity.CRITICAL,
                f"Auto-throttled due to {violation_count} violations"
            )
            logger.warning("User auto-throttled severely", user_id=user_id, violation_count=violation_count)
            return True

        return False

    @staticmethod
    def auto_lock_high_risk_user(db: Session, user_id: int, risk_score: int) -> bool:
        """Auto-lock user for high-risk events until review"""
        if risk_score >= 90:  # Very high risk threshold
            SecurityService.lock_account(db, user_id, "Auto-locked due to high-risk AI violations")

            # Log critical security event
            SecurityService.log_security_event(
                db=db,
                event_type=SecurityEvent.AI_ADMIN_NO_SIGNOFF,
                user_id=user_id,
                severity=SecuritySeverity.CRITICAL,
                details={"auto_locked": True, "risk_score": risk_score}
            )

            logger.critical("User auto-locked for high-risk violations", user_id=user_id, risk_score=risk_score)
            return True

        return False

    @staticmethod
    def monitor_and_alert(db: Session, webhook_configs: list = None):
        """Main monitoring function - check for alerts and send notifications"""
        alerts = ThreatMonitorService.check_threshold_alerts(db)

        for alert in alerts:
            logger.warning("Threat alert triggered", alert_type=alert["type"], severity=alert["severity"])

            # Send webhooks if configured
            if webhook_configs:
                for config in webhook_configs:
                    ThreatMonitorService.send_webhook_alert(config, alert)

            # Handle auto-throttling for user abuse
            if alert["type"] == "USER_ABUSE_DETECTED":
                user_id = alert["details"]["user_id"]
                violation_count = alert["details"]["violation_count"]
                ThreatMonitorService.auto_throttle_user(db, user_id, violation_count)

        return alerts
