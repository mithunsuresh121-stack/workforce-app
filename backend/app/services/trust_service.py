import structlog
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.ai import AIPolicyType, AIPolicySeverity, TrustScoreUpdate
from app.services.audit_service import AuditService

logger = structlog.get_logger(__name__)

class TrustService:
    # Trust score configuration
    MAX_TRUST_SCORE = 100
    MIN_TRUST_SCORE = 0
    DECAY_RATE_LOW = 1      # Points to decay for LOW severity violations
    DECAY_RATE_MEDIUM = 5   # Points to decay for MEDIUM severity violations
    DECAY_RATE_HIGH = 15    # Points to decay for HIGH severity violations
    DECAY_RATE_CRITICAL = 30  # Points to decay for CRITICAL severity violations
    RECOVERY_RATE = 1       # Points to recover per clean day
    RECOVERY_THRESHOLD_DAYS = 7  # Days without violations to start recovery

    # Risk scoring configuration
    RISK_BASELINE = 50.0  # Baseline risk score (0-100, higher = riskier)
    RISK_MAX = 100.0
    RISK_MIN = 0.0

    # Factor weights (sum to 1.0)
    TRUST_WEIGHT = 0.3
    ROLE_WEIGHT = 0.2
    CAPABILITY_WEIGHT = 0.25
    ANOMALY_WEIGHT = 0.15
    TIME_WEIGHT = 0.1

    @staticmethod
    def calculate_trust_score_decay(severity: AIPolicySeverity) -> int:
        """Calculate trust score decay based on violation severity"""
        decay_map = {
            AIPolicySeverity.LOW: TrustService.DECAY_RATE_LOW,
            AIPolicySeverity.MEDIUM: TrustService.DECAY_RATE_MEDIUM,
            AIPolicySeverity.HIGH: TrustService.DECAY_RATE_HIGH,
            AIPolicySeverity.CRITICAL: TrustService.DECAY_RATE_CRITICAL
        }
        return decay_map.get(severity, TrustService.DECAY_RATE_LOW)

    @staticmethod
    def update_trust_score(db: Session, user_id: int, violation_type: AIPolicyType = None,
                          severity: AIPolicySeverity = None, reason: str = "") -> int:
        """Update user's trust score based on violation or recovery"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning("User not found for trust score update", user_id=user_id)
            return TrustService.MAX_TRUST_SCORE

        old_score = user.trust_score

        if violation_type and severity:
            # Decay score for violation
            decay_amount = TrustService.calculate_trust_score_decay(severity)
            new_score = max(TrustService.MIN_TRUST_SCORE, old_score - decay_amount)
            user.trust_score = new_score

            logger.info("Trust score decayed due to violation",
                       user_id=user_id,
                       old_score=old_score,
                       new_score=new_score,
                       decay_amount=decay_amount,
                       violation_type=violation_type.value,
                       severity=severity.value)

        else:
            # Check for recovery eligibility
            if TrustService._should_recover_trust(db, user_id):
                recovery_amount = TrustService.RECOVERY_RATE
                new_score = min(TrustService.MAX_TRUST_SCORE, old_score + recovery_amount)
                user.trust_score = new_score

                logger.info("Trust score recovered",
                           user_id=user_id,
                           old_score=old_score,
                           new_score=new_score,
                           recovery_amount=recovery_amount)

        db.commit()

        # Log trust score change
        AuditService.log_event(
            db=db,
            event_type="TRUST_SCORE_UPDATE",
            user_id=user_id,
            company_id=user.company_id,
            resource_type="trust",
            resource_id=user_id,
            details={
                "old_score": old_score,
                "new_score": user.trust_score,
                "reason": reason,
                "violation_type": violation_type.value if violation_type else None,
                "severity": severity.value if severity else None
            }
        )

        return user.trust_score

    @staticmethod
    def _should_recover_trust(db: Session, user_id: int) -> bool:
        """Check if user should recover trust score based on clean history"""
        cutoff_date = datetime.utcnow() - timedelta(days=TrustService.RECOVERY_THRESHOLD_DAYS)

        # Count violations in recovery period
        violation_count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.event_type.like("SECURITY_AI_%"),
            AuditLog.created_at >= cutoff_date
        ).count()

        return violation_count == 0

    @staticmethod
    def get_trust_score(db: Session, user_id: int) -> int:
        """Get current trust score for user"""
        user = db.query(User).filter(User.id == user_id).first()
        return user.trust_score if user else TrustService.MAX_TRUST_SCORE

    @staticmethod
    def get_trust_tier(trust_score: int) -> str:
        """Get trust tier based on score"""
        if trust_score >= 90:
            return "PLATINUM"
        elif trust_score >= 75:
            return "GOLD"
        elif trust_score >= 50:
            return "SILVER"
        elif trust_score >= 25:
            return "BRONZE"
        else:
            return "RESTRICTED"

    @staticmethod
    def get_access_limits(trust_score: int) -> dict:
        """Get access limits based on trust score"""
        tier = TrustService.get_trust_tier(trust_score)

        limits = {
            "PLATINUM": {
                "max_requests_per_hour": 1000,
                "max_context_size": 32000,
                "allowed_capabilities": ["all"]
            },
            "GOLD": {
                "max_requests_per_hour": 500,
                "max_context_size": 16000,
                "allowed_capabilities": ["all"]
            },
            "SILVER": {
                "max_requests_per_hour": 100,
                "max_context_size": 8000,
                "allowed_capabilities": ["READ_TEAM_DATA", "SUGGEST_TASKS"]
            },
            "BRONZE": {
                "max_requests_per_hour": 50,
                "max_context_size": 4000,
                "allowed_capabilities": ["READ_TEAM_DATA"]
            },
            "RESTRICTED": {
                "max_requests_per_hour": 10,
                "max_context_size": 1000,
                "allowed_capabilities": ["READ_TEAM_DATA"]
            }
        }

        return limits.get(tier, limits["RESTRICTED"])

    @staticmethod
    def get_trust_history(db: Session, user_id: int, days: int = 30) -> list:
        """Get trust score history for user"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.event_type == "TRUST_SCORE_UPDATE",
            AuditLog.created_at >= cutoff_date
        ).order_by(AuditLog.created_at).all()

        history = []
        for log in logs:
            history.append({
                "timestamp": log.created_at.isoformat(),
                "old_score": log.details.get("old_score"),
                "new_score": log.details.get("new_score"),
                "reason": log.details.get("reason"),
                "violation_type": log.details.get("violation_type"),
                "severity": log.details.get("severity")
            })

        return history

    @staticmethod
    def reset_trust_score(db: Session, user_id: int, admin_user_id: int, reason: str = "") -> bool:
        """Reset user trust score to maximum (admin action)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        old_score = user.trust_score
        user.trust_score = TrustService.MAX_TRUST_SCORE
        db.commit()

        # Log admin action
        AuditService.log_admin_action(
            db=db,
            action="RESET_TRUST_SCORE",
            user_id=admin_user_id,
            company_id=user.company_id,
            details={
                "target_user_id": user_id,
                "old_score": old_score,
                "new_score": TrustService.MAX_TRUST_SCORE,
                "reason": reason
            }
        )

        logger.info("Trust score reset by admin",
                   admin_user_id=admin_user_id,
                   target_user_id=user_id,
                   old_score=old_score,
                   new_score=TrustService.MAX_TRUST_SCORE)

        return True

    @staticmethod
    def calculate_risk_score(
        db: Session,
        user: 'User',
        capability: str,
        context: dict = None
    ) -> float:
        """
        Calculate comprehensive risk score combining multiple factors:
        - Trust score
        - User role
        - Capability sensitivity
        - Anomaly detection
        - Time context
        """
        context = context or {}
        current_time = context.get('current_time', datetime.utcnow())
        recent_violations = context.get('recent_violations', 0)

        # Factor 1: Trust Score (inverted - low trust = high risk)
        trust_factor = max(0, 1.0 - (user.trust_score / TrustService.MAX_TRUST_SCORE))
        trust_risk = trust_factor * TrustService.TRUST_WEIGHT * TrustService.RISK_MAX

        # Factor 2: Role Risk (higher roles = lower risk)
        role_risk_map = {
            'SUPERADMIN': 0.1,
            'COMPANY_ADMIN': 0.2,
            'DEPARTMENT_ADMIN': 0.3,
            'TEAM_LEAD': 0.4,
            'EMPLOYEE': 0.6
        }
        role_risk = role_risk_map.get(user.role.value, 0.5) * TrustService.ROLE_WEIGHT * TrustService.RISK_MAX

        # Factor 3: Capability Risk (sensitive capabilities = higher risk)
        capability_risk_map = {
            'READ_COMPANY_DATA': 0.8,
            'GENERATE_SUMMARY': 0.6,
            'SUGGEST_TASKS': 0.4,
            'READ_TEAM_DATA': 0.3
        }
        capability_risk = capability_risk_map.get(capability, 0.5) * TrustService.CAPABILITY_WEIGHT * TrustService.RISK_MAX

        # Factor 4: Anomaly Detection (recent violations, unusual patterns)
        anomaly_score = min(1.0, recent_violations / 5.0)  # Normalize to 0-1
        # Add behavioral anomaly (simple: off-peak usage)
        hour = current_time.hour
        is_off_peak = hour < 6 or hour > 22
        anomaly_score += 0.2 if is_off_peak else 0
        anomaly_score = min(1.0, anomaly_score)
        anomaly_risk = anomaly_score * TrustService.ANOMALY_WEIGHT * TrustService.RISK_MAX

        # Factor 5: Time Context (off-hours, weekends = higher risk)
        is_weekend = current_time.weekday() >= 5
        time_risk = (0.3 if is_off_peak else 0) + (0.2 if is_weekend else 0)
        time_risk = min(1.0, time_risk) * TrustService.TIME_WEIGHT * TrustService.RISK_MAX

        # Combine weighted factors
        total_risk = (
            trust_risk * TrustService.TRUST_WEIGHT +
            role_risk * TrustService.ROLE_WEIGHT +
            capability_risk * TrustService.CAPABILITY_WEIGHT +
            anomaly_risk * TrustService.ANOMALY_WEIGHT +
            time_risk * TrustService.TIME_WEIGHT
        )

        # Normalize to 0-100
        total_risk = max(TrustService.RISK_MIN, min(TrustService.RISK_MAX, total_risk))

        # Log risk assessment
        logger.info(
            "Risk score calculated",
            user_id=user.id,
            capability=capability,
            trust_risk=trust_risk,
            role_risk=role_risk,
            capability_risk=capability_risk,
            anomaly_risk=anomaly_risk,
            time_risk=time_risk,
            total_risk=total_risk
        )

        # Audit the risk assessment
        from app.services.audit_service import AuditService
        AuditService.log_event(
            db=db,
            event_type="RISK_ASSESSMENT",
            user_id=user.id,
            company_id=user.company_id,
            resource_type="ai_capability",
            resource_id=capability,
            details={
                "risk_score": float(total_risk),
                "trust_factor": float(trust_factor),
                "role_factor": role_risk_map.get(user.role.value, 0.5),
                "capability_factor": capability_risk_map.get(capability, 0.5),
                "anomaly_factor": float(anomaly_score),
                "time_factor": float(time_risk / TrustService.RISK_MAX),
                "context": {
                    "recent_violations": recent_violations,
                    "is_off_peak": is_off_peak,
                    "is_weekend": is_weekend
                }
            }
        )

        return total_risk

    @staticmethod
    def get_recent_violations(db: Session, user_id: int, hours: int = 24) -> int:
        """Get count of recent violations for anomaly detection"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        from app.models.audit_log import AuditLog
        count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.event_type.like("SECURITY_AI_%"),
            AuditLog.created_at >= cutoff
        ).count()
        return count

    @staticmethod
    def assess_risk_level(risk_score: float) -> str:
        """Assess risk level based on score"""
        if risk_score >= 80:
            return "CRITICAL"
        elif risk_score >= 60:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
