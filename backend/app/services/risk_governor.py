from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.ai import AICapability, AIDecision
from app.services.approval_service import ApprovalPriority, ApprovalService
from app.services.audit_chain_service import AuditChainService
from app.services.audit_service import AuditService
from app.services.policy_engine import policy_engine
from app.services.trust_service import TrustService

logger = structlog.get_logger(__name__)


class RiskGovernor:
    """Adaptive risk governor with auto-restrictions and graceful degradation"""

    # Restriction levels
    RESTRICTION_NONE = "none"
    RESTRICTION_COOLDOWN = "cooldown"
    RESTRICTION_LIMITED = "limited"
    RESTRICTION_BLOCKED = "blocked"

    # Cooldown periods (minutes)
    COOLDOWN_LOW = 15
    COOLDOWN_MEDIUM = 60
    COOLDOWN_HIGH = 240  # 4 hours
    COOLDOWN_CRITICAL = 1440  # 24 hours

    def __init__(self):
        self.active_restrictions: Dict[int, Dict] = {}  # user_id -> restriction_info

    @staticmethod
    def evaluate_request(
        db: Session, user: User, capability: str, request_data: dict = None
    ) -> Tuple[AIDecision, str, Dict[str, any]]:
        """
        Comprehensive risk evaluation and decision making

        Returns:
            Tuple of (decision, reason, evaluation_context)
        """

        evaluation_context = {
            "user_id": user.id,
            "capability": capability,
            "timestamp": datetime.utcnow(),
            "request_data": request_data or {},
        }

        # Check for active restrictions first
        restriction = RiskGovernor.get_active_restriction(db, user.id)
        if restriction:
            evaluation_context["restriction"] = restriction
            decision, reason = RiskGovernor._handle_restricted_request(restriction)
            return decision, reason, evaluation_context

        # Calculate risk score
        recent_violations = TrustService.get_recent_violations(db, user.id, hours=24)
        context = {
            "current_time": datetime.utcnow(),
            "recent_violations": recent_violations,
        }
        risk_score = TrustService.calculate_risk_score(db, user, capability, context)
        risk_level = TrustService.assess_risk_level(risk_score)

        evaluation_context.update(
            {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recent_violations": recent_violations,
                "trust_score": user.trust_score,
                "user_role": user.role.value,
            }
        )

        # Evaluate against policy engine
        policy_context = {
            "user_id": user.id,
            "capability": capability,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "trust_score": user.trust_score,
            "user_role": user.role.value,
            "recent_violations": recent_violations,
            "is_off_peak": RiskGovernor._is_off_peak(),
            "is_weekend": RiskGovernor._is_weekend(),
            "company_id": user.company_id,
        }

        policy_decision, matched_rules, policy_details = (
            policy_engine.evaluate_policies(
                db, user.id, user.company_id, policy_context
            )
        )

        evaluation_context["policy_decision"] = policy_decision
        evaluation_context["matched_rules"] = matched_rules
        evaluation_context["policy_details"] = policy_details

        # Make final decision based on policy
        if policy_decision == policy_engine.ACTION_ALLOW:
            decision = AIDecision.ALLOWED
            reason = f"Policy allows request (rules: {', '.join(matched_rules)})"

        elif policy_decision == policy_engine.ACTION_DENY:
            decision = AIDecision.BLOCKED
            reason = f"Policy blocks request (rules: {', '.join(matched_rules)})"

            # Apply auto-restriction for denied requests
            RiskGovernor._apply_auto_restriction(
                db, user, risk_level, f"Policy violation: {matched_rules}"
            )

        elif policy_decision == policy_engine.ACTION_CHALLENGE:
            decision = AIDecision.PENDING_APPROVAL
            reason = f"Request requires approval (rules: {', '.join(matched_rules)})"

            # Create approval request
            RiskGovernor._create_approval_request(
                db, user, capability, request_data, risk_score, matched_rules
            )

        elif policy_decision == policy_engine.ACTION_ESCALATE:
            decision = AIDecision.PENDING_APPROVAL
            reason = (
                f"Request escalated for approval (rules: {', '.join(matched_rules)})"
            )

            # Create high-priority approval request
            RiskGovernor._create_approval_request(
                db,
                user,
                capability,
                request_data,
                risk_score,
                matched_rules,
                priority=ApprovalPriority.HIGH,
            )

        else:
            # Default deny
            decision = AIDecision.BLOCKED
            reason = "Request denied by risk governor"

        # Log comprehensive evaluation
        AuditService.log_event(
            db=db,
            event_type="RISK_EVALUATION",
            user_id=user.id,
            company_id=user.company_id,
            resource_type="ai_capability",
            resource_id=capability,
            details=evaluation_context,
        )

        # Audit chain
        AuditChainService.log_ai_event(
            db=db,
            user_id=user.id,
            company_id=user.company_id,
            event_type="RISK_EVALUATION",
            data={
                "capability": capability,
                "decision": decision.value,
                "risk_score": risk_score,
                "policy_decision": policy_decision,
            },
        )

        logger.info(
            "Risk evaluation completed",
            user_id=user.id,
            capability=capability,
            decision=decision.value,
            risk_score=risk_score,
            policy_decision=policy_decision,
        )

        return decision, reason, evaluation_context

    @staticmethod
    def get_active_restriction(db: Session, user_id: int) -> Optional[Dict]:
        """Get any active restriction for a user"""
        # In production, this would check a database table
        # For now, using in-memory storage
        restriction = RiskGovernor().active_restrictions.get(user_id)

        if restriction:
            expires_at = restriction.get("expires_at")
            if expires_at and datetime.utcnow() > expires_at:
                # Restriction expired
                del RiskGovernor().active_restrictions[user_id]
                return None

        return restriction

    @staticmethod
    def _handle_restricted_request(restriction: Dict) -> Tuple[AIDecision, str]:
        """Handle a request from a restricted user"""
        restriction_level = restriction.get("level", RiskGovernor.RESTRICTION_NONE)

        if restriction_level == RiskGovernor.RESTRICTION_BLOCKED:
            return (
                AIDecision.BLOCKED,
                f"User is blocked until {restriction.get('expires_at')}",
            )

        elif restriction_level == RiskGovernor.RESTRICTION_LIMITED:
            return (
                AIDecision.BLOCKED,
                f"User has limited access until {restriction.get('expires_at')}",
            )

        elif restriction_level == RiskGovernor.RESTRICTION_COOLDOWN:
            return (
                AIDecision.BLOCKED,
                f"User is in cooldown until {restriction.get('expires_at')}",
            )

        return AIDecision.ALLOWED, "No active restrictions"

    @staticmethod
    def _apply_auto_restriction(db: Session, user: User, risk_level: str, reason: str):
        """Apply automatic restriction based on risk level"""

        # Determine restriction level and duration
        if risk_level == "CRITICAL":
            level = RiskGovernor.RESTRICTION_BLOCKED
            duration_minutes = RiskGovernor.COOLDOWN_CRITICAL
        elif risk_level == "HIGH":
            level = RiskGovernor.RESTRICTION_LIMITED
            duration_minutes = RiskGovernor.COOLDOWN_HIGH
        elif risk_level == "MEDIUM":
            level = RiskGovernor.RESTRICTION_COOLDOWN
            duration_minutes = RiskGovernor.COOLDOWN_MEDIUM
        else:
            level = RiskGovernor.RESTRICTION_COOLDOWN
            duration_minutes = RiskGovernor.COOLDOWN_LOW

        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)

        restriction = {
            "level": level,
            "reason": reason,
            "applied_at": datetime.utcnow(),
            "expires_at": expires_at,
            "risk_level": risk_level,
        }

        # Store restriction (in production, save to database)
        RiskGovernor().active_restrictions[user.id] = restriction

        # Log restriction
        AuditService.log_event(
            db=db,
            event_type="AUTO_RESTRICTION_APPLIED",
            user_id=user.id,
            company_id=user.company_id,
            resource_type="user_access",
            resource_id=user.id,
            details=restriction,
        )

        # Audit chain
        AuditChainService.log_ai_event(
            db=db,
            user_id=user.id,
            company_id=user.company_id,
            event_type="AUTO_RESTRICTION",
            data={
                "restriction_level": level,
                "reason": reason,
                "duration_minutes": duration_minutes,
            },
        )

        logger.warning(
            "Auto-restriction applied",
            user_id=user.id,
            restriction_level=level,
            reason=reason,
            expires_at=expires_at,
        )

    @staticmethod
    def _create_approval_request(
        db: Session,
        user: User,
        capability: str,
        request_data: dict,
        risk_score: int,
        matched_rules: List[str],
        priority: ApprovalPriority = ApprovalPriority.MEDIUM,
    ):
        """Create an approval request for the user"""

        request_data_full = {
            "capability": capability,
            "request_data": request_data,
            "risk_score": risk_score,
            "matched_rules": matched_rules,
            "evaluation_timestamp": datetime.utcnow().isoformat(),
        }

        approval = ApprovalService.create_approval_request(
            db=db,
            requestor=user,
            request_type="ai_capability",
            request_data=request_data_full,
            risk_score=risk_score,
            priority=priority,
            notes=f"Auto-generated approval request for {capability} (rules: {', '.join(matched_rules)})",
        )

        logger.info(
            "Approval request created for risky request",
            user_id=user.id,
            capability=capability,
            approval_id=approval.id,
            risk_score=risk_score,
        )

    @staticmethod
    def _is_off_peak() -> bool:
        """Check if current time is off-peak"""
        hour = datetime.utcnow().hour
        return hour < 6 or hour > 22

    @staticmethod
    def _is_weekend() -> bool:
        """Check if current day is weekend"""
        return datetime.utcnow().weekday() >= 5

    @staticmethod
    def lift_restriction(
        db: Session, user_id: int, lifted_by: User, reason: str = ""
    ) -> bool:
        """Manually lift a user's restriction"""

        restriction = RiskGovernor.get_active_restriction(db, user_id)
        if not restriction:
            return False

        # Remove restriction
        if user_id in RiskGovernor().active_restrictions:
            del RiskGovernor().active_restrictions[user_id]

        # Log lifting
        AuditService.log_event(
            db=db,
            event_type="RESTRICTION_LIFTED",
            user_id=lifted_by.id,
            company_id=lifted_by.company_id,
            resource_type="user_access",
            resource_id=user_id,
            details={
                "target_user_id": user_id,
                "reason": reason,
                "previous_restriction": restriction,
            },
        )

        logger.info(
            "Restriction lifted", user_id=user_id, lifted_by=lifted_by.id, reason=reason
        )

        return True

    @staticmethod
    def get_system_status(db: Session) -> Dict[str, any]:
        """Get overall system risk status"""

        # Count active restrictions
        active_restrictions = len(RiskGovernor().active_restrictions)

        # Get recent high-risk evaluations
        recent_high_risk = (
            db.query(AuditService)
            .filter(
                and_(
                    AuditService.event_type == "RISK_EVALUATION",
                    AuditService.created_at >= datetime.utcnow() - timedelta(hours=1),
                    AuditService.details["risk_level"].astext.in_(["HIGH", "CRITICAL"]),
                )
            )
            .count()
        )

        # Calculate system risk level
        if active_restrictions > 10 or recent_high_risk > 20:
            system_risk = "CRITICAL"
        elif active_restrictions > 5 or recent_high_risk > 10:
            system_risk = "HIGH"
        elif active_restrictions > 2 or recent_high_risk > 5:
            system_risk = "MEDIUM"
        else:
            system_risk = "LOW"

        return {
            "system_risk_level": system_risk,
            "active_restrictions": active_restrictions,
            "recent_high_risk_evaluations": recent_high_risk,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def graceful_degradation_check(db: Session) -> Dict[str, bool]:
        """Check if system should enter graceful degradation mode"""

        status = RiskGovernor.get_system_status(db)

        # Define degradation thresholds
        should_degrade = (
            status["active_restrictions"] > 15
            or status["recent_high_risk_evaluations"] > 30
            or status["system_risk_level"] == "CRITICAL"
        )

        return {
            "should_degrade": should_degrade,
            "reason": "High system risk levels detected" if should_degrade else None,
            "degradation_actions": (
                [
                    "Increase approval requirements",
                    "Enable additional monitoring",
                    "Reduce concurrent request limits",
                ]
                if should_degrade
                else []
            ),
        }
