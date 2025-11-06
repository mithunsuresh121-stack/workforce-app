from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas.ai import ApprovalRequest, ApprovalDecision
from app.services.approval_service import ApprovalService
from app.deps import get_current_user
from app.models.user import User
from app.core.rbac import require_role, UserRole

router = APIRouter()

@router.post("/", response_model=dict)
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def create_approval_request(
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new approval request"""
    try:
        from app.schemas.ai import ApprovalPriority
        priority = ApprovalPriority(request.priority.lower())

        approval = ApprovalService.create_approval_request(
            db=db,
            requestor=current_user,
            request_type=request.request_type,
            request_data=request.request_data,
            risk_score=request.risk_score,
            priority=priority,
            notes=request.notes
        )

        return {
            "message": "Approval request created",
            "approval_id": approval.id,
            "status": approval.status.value
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create approval: {str(e)}")

@router.get("/pending", response_model=dict)
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_my_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending approvals assigned to current user"""
    try:
        approvals = ApprovalService.get_pending_approvals(db, current_user)
        return {
            "approvals": [
                {
                    "id": a.id,
                    "request_type": a.request_type,
                    "requestor_id": a.requestor_id,
                    "requestor_name": a.requestor.email if a.requestor else None,
                    "risk_score": a.risk_score,
                    "priority": a.priority.value,
                    "created_at": a.created_at.isoformat(),
                    "expires_at": a.expires_at.isoformat() if a.expires_at else None,
                    "request_data": a.request_data
                } for a in approvals
            ],
            "count": len(approvals)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approvals: {str(e)}")

@router.post("/{approval_id}/decide", response_model=dict)
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def decide_approval(
    approval_id: int,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
        raise HTTPException(status_code=500, detail=f"Failed to process approval: {str(e)}")

@router.post("/{approval_id}/escalate", response_model=dict)
@require_role([UserRole.DEPARTMENT_ADMIN, UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def escalate_approval(
    approval_id: int,
    escalation_reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Escalate approval to higher authority"""
    try:
        success = ApprovalService.escalate_approval(
            db, approval_id, escalation_reason, current_user
        )

        if not success:
            raise HTTPException(status_code=404, detail="Approval not found or cannot be escalated")

        return {"message": "Approval escalated", "approval_id": approval_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to escalate approval: {str(e)}")

@router.get("/stats", response_model=dict)
@require_role([UserRole.COMPANY_ADMIN, UserRole.SUPERADMIN])
def get_approval_stats(
    company_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get approval queue statistics"""
    try:
        # If not superadmin, restrict to own company
        if current_user.role != UserRole.SUPERADMIN:
            company_id = current_user.company_id

        stats = ApprovalService.get_approval_stats(db, company_id)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/cleanup", response_model=dict)
@require_role([UserRole.SUPERADMIN])
def cleanup_expired_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up expired pending approvals (superadmin only)"""
    try:
        cleaned_count = ApprovalService.cleanup_expired_approvals(db)
        return {"message": f"Cleaned up {cleaned_count} expired approvals"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")
