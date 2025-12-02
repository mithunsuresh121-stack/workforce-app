from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import UserRole, require_role
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.ai import (AIQueryRequest, AIQueryResponse, ApprovalDecision,
                            ApprovalRequest, AutoRestriction, PolicyDSL,
                            RiskAssessment)
from app.services.ai_service import AIService
from app.services.approval_service import ApprovalService
from app.services.policy_engine import policy_engine
from app.services.risk_governor import RiskGovernor
from app.services.trust_service import TrustService

router = APIRouter()


@router.post("/query", response_model=AIQueryResponse)
def ai_query(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process AI query with adaptive risk governance"""
    try:
        # Use risk governor for comprehensive evaluation
        decision, reason, evaluation_context = RiskGovernor.evaluate_request(
            db,
            current_user,
            request.capability.value,
            {"query_text": request.query_text},
        )

        if decision.value == "blocked":
            return AIQueryResponse(
                status=decision,
                reason=reason,
                mock_response="",
                approval_required=False,
            )

        elif decision.value == "pending_approval":
            return AIQueryResponse(
                status=decision, reason=reason, mock_response="", approval_required=True
            )

        # Process the query if allowed
        response = AIService.process_ai_query(db, current_user, request)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI query processing failed: {str(e)}"
        )


@router.get("/risk-assessment", response_model=RiskAssessment)
def get_risk_assessment(
    capability: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get risk assessment for a capability"""
    try:
        risk_score = TrustService.calculate_risk_score(db, current_user, capability)
        risk_level = TrustService.assess_risk_level(risk_score)

        # Get recent violations for context
        recent_violations = TrustService.get_recent_violations(
            db, current_user.id, hours=24
        )

        return RiskAssessment(
            user_id=current_user.id,
            capability=capability,
            risk_score=risk_score,
            risk_level=risk_level,
            factors={
                "trust_score": current_user.trust_score,
                "user_role": current_user.role.value,
                "recent_violations": recent_violations,
            },
            context={
                "is_off_peak": RiskGovernor._is_off_peak(),
                "is_weekend": RiskGovernor._is_weekend(),
            },
            timestamp=evaluation_context.get("timestamp", datetime.utcnow()),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.get("/policies", response_model=PolicyDSL)
@require_role([UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_policies(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get current policy rules (admin only)"""
    try:
        rules = policy_engine.get_policy_rules()
        return PolicyDSL(rules=rules, version="1.0")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get policies: {str(e)}")


@router.post("/policies")
@require_role([UserRole.SUPERADMIN])
def update_policies(
    dsl_text: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update policy rules via DSL (superadmin only)"""
    try:
        new_rules = policy_engine.parse_policy_dsl(dsl_text)

        # Validate rules
        for rule in new_rules:
            is_valid, error = policy_engine.validate_policy_rule(rule)
            if not is_valid:
                raise HTTPException(
                    status_code=400, detail=f"Invalid rule {rule.rule_id}: {error}"
                )

        # Add rules to engine
        for rule in new_rules:
            policy_engine.add_rule(rule)

        return {
            "message": f"Added {len(new_rules)} policy rules",
            "rules": [r.rule_id for r in new_rules],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update policies: {str(e)}"
        )


@router.get("/approvals/pending")
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_pending_approvals(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get pending approvals for current user"""
    try:
        approvals = ApprovalService.get_pending_approvals(db, current_user)
        return {"approvals": approvals, "count": len(approvals)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get approvals: {str(e)}"
        )


@router.post("/approvals/{approval_id}/decide")
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def decide_approval(
    approval_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Make decision on approval request"""
    try:
        success = ApprovalService.process_approval(
            db, approval_id, current_user, decision.decision, decision.notes
        )

        if not success:
            raise HTTPException(status_code=403, detail="Cannot process this approval")

        return {"message": f"Approval {decision.decision}", "approval_id": approval_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process approval: {str(e)}"
        )


@router.post("/approvals/{approval_id}/escalate")
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def escalate_approval(
    approval_id: int,
    escalation_reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Escalate approval to higher authority"""
    try:
        success = ApprovalService.escalate_approval(
            db, approval_id, escalation_reason, current_user
        )

        if not success:
            raise HTTPException(
                status_code=404, detail="Approval not found or cannot be escalated"
            )

        return {"message": "Approval escalated", "approval_id": approval_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to escalate approval: {str(e)}"
        )


@router.get("/restrictions/{user_id}")
@require_role([UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_user_restrictions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get active restrictions for a user (admin only)"""
    try:
        restriction = RiskGovernor.get_active_restriction(db, user_id)

        if restriction:
            return AutoRestriction(
                user_id=user_id,
                level=restriction.get("level", "none"),
                reason=restriction.get("reason", ""),
                expires_at=restriction.get("expires_at"),
                risk_level=restriction.get("risk_level", "LOW"),
            )
        else:
            return {"user_id": user_id, "level": "none", "active": False}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get restrictions: {str(e)}"
        )


@router.post("/restrictions/{user_id}/lift")
@require_role([UserRole.SUPERADMIN])
def lift_restriction(
    user_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lift user restriction (superadmin only)"""
    try:
        success = RiskGovernor.lift_restriction(db, user_id, current_user, reason)

        if not success:
            raise HTTPException(status_code=404, detail="No active restriction found")

        return {"message": "Restriction lifted", "user_id": user_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to lift restriction: {str(e)}"
        )


@router.get("/system/status")
@require_role([UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_system_status(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get overall system risk status"""
    try:
        status = RiskGovernor.get_system_status(db)
        degradation_check = RiskGovernor.graceful_degradation_check(db)

        return {"risk_status": status, "degradation_check": degradation_check}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get system status: {str(e)}"
        )
