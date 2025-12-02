from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

from app.models.approval_queue import (ApprovalPriority, ApprovalQueue,
                                       ApprovalQueueItem, ApprovalStatus)
from app.models.user import User, UserRole
from app.services.audit_chain_service import AuditChainService
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService, SecuritySeverity

logger = structlog.get_logger(__name__)


class ApprovalService:
    """Service for managing approval queues and workflows"""

    # Approval timeouts (hours)
    APPROVAL_TIMEOUT_LOW = 24
    APPROVAL_TIMEOUT_MEDIUM = 12
    APPROVAL_TIMEOUT_HIGH = 6
    APPROVAL_TIMEOUT_CRITICAL = 2

    @staticmethod
    def create_approval_request(
        db: Session,
        requestor: User,
        request_type: str,
        request_data: dict,
        risk_score: int = None,
        priority: ApprovalPriority = ApprovalPriority.MEDIUM,
        notes: str = None,
    ) -> ApprovalQueue:
        """Create a new approval request"""

        # Determine initial approver based on request type and risk
        initial_approver = ApprovalService._determine_initial_approver(
            db, requestor, request_type, risk_score
        )

        # Calculate expiration time
        timeout_hours = ApprovalService._get_timeout_hours(priority)
        expires_at = datetime.utcnow() + timedelta(hours=timeout_hours)

        # Create approval queue entry
        approval = ApprovalQueue(
            company_id=requestor.company_id,
            request_type=request_type,
            request_data=str(request_data),  # JSON serialized
            risk_score=risk_score,
            priority=priority,
            requestor_id=requestor.id,
            requestor_notes=notes,
            current_approver_id=initial_approver.id if initial_approver else None,
            assigned_at=datetime.utcnow(),
            expires_at=expires_at,
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        # Create approval steps if needed
        ApprovalService._create_approval_steps(db, approval)

        # Log creation
        AuditService.log_event(
            db=db,
            event_type="APPROVAL_REQUEST_CREATED",
            user_id=requestor.id,
            company_id=requestor.company_id,
            resource_type="approval_queue",
            resource_id=approval.id,
            details={
                "request_type": request_type,
                "priority": priority.value,
                "risk_score": risk_score,
                "initial_approver_id": (
                    initial_approver.id if initial_approver else None
                ),
            },
        )

        # Audit chain
        AuditChainService.log_ai_event(
            db=db,
            user_id=requestor.id,
            company_id=requestor.company_id,
            event_type="APPROVAL_REQUEST",
            data={
                "approval_id": approval.id,
                "request_type": request_type,
                "risk_score": risk_score,
            },
        )

        logger.info(
            "Approval request created",
            approval_id=approval.id,
            requestor_id=requestor.id,
            request_type=request_type,
            priority=priority.value,
        )

        return approval

    @staticmethod
    def _determine_initial_approver(
        db: Session, requestor: User, request_type: str, risk_score: int = None
    ) -> Optional[User]:
        """Determine who should initially review this approval"""

        # For AI capabilities, escalate based on risk and requestor role
        if request_type == "ai_capability":
            if risk_score and risk_score >= 80:
                # Critical risk - go straight to SUPERADMIN
                approver = (
                    db.query(User)
                    .filter(
                        and_(
                            User.company_id == requestor.company_id,
                            User.role == UserRole.SUPERADMIN,
                            User.is_active == True,
                        )
                    )
                    .first()
                )
                return approver
            elif risk_score and risk_score >= 60:
                # High risk - COMPANY_ADMIN
                approver = (
                    db.query(User)
                    .filter(
                        and_(
                            User.company_id == requestor.company_id,
                            User.role == UserRole.COMPANY_ADMIN,
                            User.is_active == True,
                        )
                    )
                    .first()
                )
                return approver
            else:
                # Medium/low risk - DEPARTMENT_ADMIN
                approver = (
                    db.query(User)
                    .filter(
                        and_(
                            User.company_id == requestor.company_id,
                            User.role == UserRole.DEPARTMENT_ADMIN,
                            User.is_active == True,
                        )
                    )
                    .first()
                )
                return approver

        # Default fallback
        return None

    @staticmethod
    def _get_timeout_hours(priority: ApprovalPriority) -> int:
        """Get timeout hours based on priority"""
        timeout_map = {
            ApprovalPriority.LOW: ApprovalService.APPROVAL_TIMEOUT_LOW,
            ApprovalPriority.MEDIUM: ApprovalService.APPROVAL_TIMEOUT_MEDIUM,
            ApprovalPriority.HIGH: ApprovalService.APPROVAL_TIMEOUT_HIGH,
            ApprovalPriority.CRITICAL: ApprovalService.APPROVAL_TIMEOUT_CRITICAL,
        }
        return timeout_map.get(priority, ApprovalService.APPROVAL_TIMEOUT_MEDIUM)

    @staticmethod
    def _create_approval_steps(db: Session, approval: ApprovalQueue):
        """Create multi-step approval process if needed"""
        # For now, single-step process
        # In production, this could create multiple steps based on risk/complexity

        step = ApprovalQueueItem(
            approval_queue_id=approval.id,
            step_number=1,
            step_type="human_review",
            required_role=(
                approval.current_approver.role.value
                if approval.current_approver
                else None
            ),
            assigned_to_id=approval.current_approver_id,
        )

        db.add(step)
        db.commit()

    @staticmethod
    def process_approval(
        db: Session, approval_id: int, approver: User, decision: str, notes: str = None
    ) -> bool:
        """Process an approval decision"""

        approval = (
            db.query(ApprovalQueue).filter(ApprovalQueue.id == approval_id).first()
        )
        if not approval:
            return False

        # Verify approver has permission
        if not ApprovalService._can_approve(approver, approval):
            logger.warning(
                "Unauthorized approval attempt",
                approval_id=approval_id,
                approver_id=approver.id,
                required_role=(
                    approval.current_approver.role.value
                    if approval.current_approver
                    else None
                ),
            )
            return False

        # Update approval status
        old_status = approval.status
        approval.status = ApprovalStatus(decision)
        approval.approved_by_id = approver.id
        approval.approved_at = datetime.utcnow()
        approval.approval_notes = notes

        # Update approval step
        step = (
            db.query(ApprovalQueueItem)
            .filter(
                and_(
                    ApprovalQueueItem.approval_queue_id == approval_id,
                    ApprovalQueueItem.status == ApprovalStatus.PENDING,
                )
            )
            .first()
        )

        if step:
            step.status = ApprovalStatus(decision)
            step.completed_at = datetime.utcnow()
            step.decision = decision
            step.notes = notes

        db.commit()

        # Execute approved action if needed
        if decision == "approved":
            ApprovalService._execute_approved_action(db, approval)

        # Log decision
        AuditService.log_event(
            db=db,
            event_type="APPROVAL_DECISION",
            user_id=approver.id,
            company_id=approver.company_id,
            resource_type="approval_queue",
            resource_id=approval_id,
            details={
                "decision": decision,
                "old_status": old_status.value,
                "new_status": approval.status.value,
                "approver_notes": notes,
            },
        )

        # Audit chain
        AuditChainService.log_policy_decision(
            db=db,
            user_id=approver.id,
            company_id=approver.company_id,
            decision=decision,
            policy_version="1.0",
            data={
                "approval_id": approval_id,
                "request_type": approval.request_type,
                "decision": decision,
            },
        )

        logger.info(
            "Approval processed",
            approval_id=approval_id,
            approver_id=approver.id,
            decision=decision,
        )

        return True

    @staticmethod
    def _can_approve(approver: User, approval: ApprovalQueue) -> bool:
        """Check if user can approve this request"""
        if approval.current_approver_id != approver.id:
            return False

        # Role-based approval permissions
        if approval.request_type == "ai_capability":
            # SUPERADMIN can approve anything
            if approver.role == UserRole.SUPERADMIN:
                return True
            # COMPANY_ADMIN can approve DEPARTMENT_ADMIN and below
            elif approver.role == UserRole.COMPANY_ADMIN:
                return approval.requestor.role in [
                    UserRole.DEPARTMENT_ADMIN,
                    UserRole.TEAM_LEAD,
                    UserRole.EMPLOYEE,
                ]
            # DEPARTMENT_ADMIN can approve TEAM_LEAD and EMPLOYEE
            elif approver.role == UserRole.DEPARTMENT_ADMIN:
                return approval.requestor.role in [
                    UserRole.TEAM_LEAD,
                    UserRole.EMPLOYEE,
                ]

        return False

    @staticmethod
    def _execute_approved_action(db: Session, approval: ApprovalQueue):
        """Execute the approved action"""
        # This would integrate with the AI service to actually execute the approved request
        # For now, just log it

        logger.info(
            "Executing approved action",
            approval_id=approval.id,
            request_type=approval.request_type,
        )

        # In production, this would call the appropriate service
        # e.g., AIService.execute_approved_request(approval.request_data)

    @staticmethod
    def get_pending_approvals(
        db: Session, approver: User, limit: int = 50
    ) -> List[ApprovalQueue]:
        """Get pending approvals for a user"""

        approvals = (
            db.query(ApprovalQueue)
            .filter(
                and_(
                    ApprovalQueue.current_approver_id == approver.id,
                    ApprovalQueue.status == ApprovalStatus.PENDING,
                    or_(
                        ApprovalQueue.expires_at.is_(None),
                        ApprovalQueue.expires_at > datetime.utcnow(),
                    ),
                )
            )
            .order_by(desc(ApprovalQueue.priority), ApprovalQueue.created_at)
            .limit(limit)
            .all()
        )

        return approvals

    @staticmethod
    def escalate_approval(
        db: Session, approval_id: int, escalation_reason: str, escalated_by: User
    ) -> bool:
        """Escalate an approval to higher authority"""

        approval = (
            db.query(ApprovalQueue).filter(ApprovalQueue.id == approval_id).first()
        )
        if not approval:
            return False

        # Find next level approver
        next_approver = ApprovalService._get_escalation_approver(db, approval)

        if not next_approver:
            logger.warning("No escalation approver found", approval_id=approval_id)
            return False

        # Update approval
        approval.current_approver_id = next_approver.id
        approval.assigned_at = datetime.utcnow()
        approval.escalated = True
        approval.escalation_reason = escalation_reason
        approval.escalation_level += 1

        # Extend timeout
        timeout_hours = ApprovalService._get_timeout_hours(approval.priority)
        approval.expires_at = datetime.utcnow() + timedelta(hours=timeout_hours)

        db.commit()

        # Log escalation
        AuditService.log_event(
            db=db,
            event_type="APPROVAL_ESCALATED",
            user_id=escalated_by.id,
            company_id=escalated_by.company_id,
            resource_type="approval_queue",
            resource_id=approval_id,
            details={
                "escalation_reason": escalation_reason,
                "new_approver_id": next_approver.id,
                "escalation_level": approval.escalation_level,
            },
        )

        logger.info(
            "Approval escalated",
            approval_id=approval_id,
            escalated_by=escalated_by.id,
            new_approver_id=next_approver.id,
        )

        return True

    @staticmethod
    def _get_escalation_approver(
        db: Session, approval: ApprovalQueue
    ) -> Optional[User]:
        """Get the next level approver for escalation"""

        current_role = (
            approval.current_approver.role if approval.current_approver else None
        )

        if current_role == UserRole.DEPARTMENT_ADMIN:
            # Escalate to COMPANY_ADMIN
            approver = (
                db.query(User)
                .filter(
                    and_(
                        User.company_id == approval.company_id,
                        User.role == UserRole.COMPANY_ADMIN,
                        User.is_active == True,
                    )
                )
                .first()
            )
            return approver
        elif current_role in [UserRole.COMPANY_ADMIN, UserRole.TEAM_LEAD]:
            # Escalate to SUPERADMIN
            approver = (
                db.query(User)
                .filter(
                    and_(
                        User.company_id == approval.company_id,
                        User.role == UserRole.SUPERADMIN,
                        User.is_active == True,
                    )
                )
                .first()
            )
            return approver

        return None

    @staticmethod
    def cleanup_expired_approvals(db: Session) -> int:
        """Clean up expired pending approvals"""

        expired_count = (
            db.query(ApprovalQueue)
            .filter(
                and_(
                    ApprovalQueue.status == ApprovalStatus.PENDING,
                    ApprovalQueue.expires_at <= datetime.utcnow(),
                )
            )
            .update({"status": ApprovalStatus.EXPIRED, "updated_at": datetime.utcnow()})
        )

        db.commit()

        if expired_count > 0:
            logger.info("Cleaned up expired approvals", count=expired_count)

        return expired_count

    @staticmethod
    def get_approval_stats(db: Session, company_id: int = None) -> Dict[str, int]:
        """Get approval queue statistics"""

        query = db.query(ApprovalQueue)
        if company_id:
            query = query.filter(ApprovalQueue.company_id == company_id)

        stats = {}
        for status in ApprovalStatus:
            count = query.filter(ApprovalQueue.status == status).count()
            stats[status.value] = count

        return stats
