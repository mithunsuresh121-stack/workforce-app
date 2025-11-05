from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.rbac import require_superadmin, require_company_access
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService
from app.schemas.ai import (
    AIPolicyUpdate, AIApprovalRequest, TrustScoreUpdate,
    RiskHeatMapData, ComplianceExportRequest, WebhookAlertConfig
)
from app.services.trust_service import TrustService
from app.services.threat_monitor_service import ThreatMonitorService
from app.services.compliance_export_service import ComplianceExportService
from app.services.audit_chain_service import AuditChainService
from app.deps import get_current_user
from app.models.user import User, UserRole
from app.core.rbac import RBACService
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

@router.get("/stats/users")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: Optional[int] = Query(None, description="Company ID for scoping (required for COMPANY_ADMIN)")
):
    """Get user statistics - SUPERADMIN: all companies, COMPANY_ADMIN: scoped to company"""
    if current_user.role.name == "SUPERADMIN":
        # SUPERADMIN can see all or specify company
        pass
    elif current_user.role.name == "COMPANY_ADMIN":
        if not company_id:
            company_id = current_user.company_id
        elif company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied to other companies")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stats = AnalyticsService.get_user_stats(db, company_id)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VIEW_USER_STATS",
        user_id=current_user.id,
        company_id=company_id,
        details={"stats_type": "users"}
    )

    return stats

@router.get("/stats/channels")
def get_channel_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: Optional[int] = Query(None, description="Company ID for scoping (required for COMPANY_ADMIN)")
):
    """Get channel statistics - SUPERADMIN: all companies, COMPANY_ADMIN: scoped to company"""
    if current_user.role.name == "SUPERADMIN":
        pass
    elif current_user.role.name == "COMPANY_ADMIN":
        if not company_id:
            company_id = current_user.company_id
        elif company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied to other companies")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stats = AnalyticsService.get_channel_stats(db, company_id)

    AuditService.log_admin_action(
        db=db,
        action="VIEW_CHANNEL_STATS",
        user_id=current_user.id,
        company_id=company_id,
        details={"stats_type": "channels"}
    )

    return stats

@router.get("/stats/meetings")
def get_meeting_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: Optional[int] = Query(None, description="Company ID for scoping (required for COMPANY_ADMIN)")
):
    """Get meeting statistics - SUPERADMIN: all companies, COMPANY_ADMIN: scoped to company"""
    if current_user.role.name == "SUPERADMIN":
        pass
    elif current_user.role.name == "COMPANY_ADMIN":
        if not company_id:
            company_id = current_user.company_id
        elif company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied to other companies")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stats = AnalyticsService.get_meeting_stats(db, company_id)

    AuditService.log_admin_action(
        db=db,
        action="VIEW_MEETING_STATS",
        user_id=current_user.id,
        company_id=company_id,
        details={"stats_type": "meetings"}
    )

    return stats

@router.get("/stats/audit")
def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: Optional[int] = Query(None, description="Company ID for scoping (required for COMPANY_ADMIN)")
):
    """Get audit statistics - SUPERADMIN: all companies, COMPANY_ADMIN: scoped to company"""
    if current_user.role.name == "SUPERADMIN":
        pass
    elif current_user.role.name == "COMPANY_ADMIN":
        if not company_id:
            company_id = current_user.company_id
        elif company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied to other companies")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    stats = AnalyticsService.get_audit_stats(db, company_id)

    AuditService.log_admin_action(
        db=db,
        action="VIEW_AUDIT_STATS",
        user_id=current_user.id,
        company_id=company_id,
        details={"stats_type": "audit"}
    )

    return stats


@router.get("/audit/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get audit logs - Superadmin only"""
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())

    if company_id:
        query = query.filter(AuditLog.company_id == company_id)

    total = query.count()
    logs = query.limit(limit).offset(offset).all()

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VIEW_AUDIT_LOGS",
        user_id=current_user.id,
        company_id=company_id,
        details={"limit": limit, "offset": offset}
    )

    return {
        "logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "company_id": log.company_id,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


class AuditSearchRequest(BaseModel):
    event_type: Optional[str] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    resource_type: Optional[str] = None
    limit: int = 50
    offset: int = 0


@router.post("/audit/search")
def search_audit_logs(
    search_request: AuditSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Search audit logs - Superadmin only"""
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())

    if search_request.event_type:
        query = query.filter(AuditLog.event_type == search_request.event_type)
    if search_request.user_id:
        query = query.filter(AuditLog.user_id == search_request.user_id)
    if search_request.company_id:
        query = query.filter(AuditLog.company_id == search_request.company_id)
    if search_request.resource_type:
        query = query.filter(AuditLog.resource_type == search_request.resource_type)
    if search_request.start_date:
        query = query.filter(AuditLog.created_at >= search_request.start_date)
    if search_request.end_date:
        query = query.filter(AuditLog.created_at <= search_request.end_date)

    total = query.count()
    logs = query.limit(search_request.limit).offset(search_request.offset).all()

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="SEARCH_AUDIT_LOGS",
        user_id=current_user.id,
        company_id=search_request.company_id,
        details=search_request.dict(exclude={"limit", "offset"})
    )

    return {
        "logs": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "user_id": log.user_id,
                "company_id": log.company_id,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "limit": search_request.limit,
        "offset": search_request.offset
    }


@router.get("/security/alerts")
def get_security_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get security alerts - Superadmin only"""
    alerts = SecurityService.get_security_alerts(db, company_id, limit)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VIEW_SECURITY_ALERTS",
        user_id=current_user.id,
        company_id=company_id,
        details={"limit": limit}
    )

    return alerts


@router.post("/users/{user_id}/unlock")
def unlock_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Unlock user account - Superadmin only"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is already unlocked or lock expired
    if not SecurityService.is_account_locked(target_user):
        raise HTTPException(status_code=400, detail="Account is not locked")

    SecurityService.unlock_account(db, user_id, current_user.id)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="UNLOCK_USER_ACCOUNT",
        user_id=current_user.id,
        company_id=target_user.company_id,
        details={"unlocked_user_id": user_id}
    )

    return {"message": f"User {user_id} account unlocked successfully"}


class UserRoleUpdate(BaseModel):
    role: UserRole
    company_id: Optional[int] = None
    department_id: Optional[int] = None
    team_id: Optional[int] = None


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update user role with protections (Superadmin only)"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cross-org prevention
    if not RBACService.can_manage_users(current_user, target_user):
        raise HTTPException(status_code=403, detail="Cannot manage users across organizations")

    # Last superadmin protection
    if target_user.role == UserRole.SUPERADMIN and role_update.role != UserRole.SUPERADMIN:
        # Check if this is the last superadmin
        superadmin_count = db.query(User).filter(User.role == UserRole.SUPERADMIN).count()
        if superadmin_count <= 1:
            raise HTTPException(
                status_code=403,
                detail="Cannot demote the last superadmin"
            )

    # Update role and org assignments
    target_user.role = role_update.role
    if role_update.company_id:
        target_user.company_id = role_update.company_id
    if role_update.department_id:
        target_user.department_id = role_update.department_id
    if role_update.team_id:
        target_user.team_id = role_update.team_id

    db.commit()

    # Audit log
    AuditService.log_user_assigned_role(
        db=db,
        user_id=current_user.id,
        target_user_id=user_id,
        company_id=current_user.company_id,
        role=role_update.role.value,
        details={
            "previous_role": target_user.role.value if hasattr(target_user, 'role') else None,
            "new_company_id": role_update.company_id,
            "new_department_id": role_update.department_id,
            "new_team_id": role_update.team_id
        }
    )

    return {"message": "User role updated successfully"}


@router.post("/ai/policy")
def update_ai_policy(
    policy_update: AIPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Update AI policy - Superadmin only"""
    # For now, just log the policy update (policies are hardcoded in RBAC)
    # In future, could store policies in database
    AuditService.log_admin_action(
        db=db,
        action="UPDATE_AI_POLICY",
        user_id=current_user.id,
        company_id=None,
        details=policy_update.dict()
    )

    return {"message": "AI policy updated successfully"}


@router.get("/ai/logs")
def get_ai_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get AI audit logs - Superadmin only"""
    query = db.query(AuditLog).filter(AuditLog.event_type == "AI_REQUEST").order_by(AuditLog.created_at.desc())

    if company_id:
        query = query.filter(AuditLog.company_id == company_id)

    total = query.count()
    logs = query.limit(limit).offset(offset).all()

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VIEW_AI_LOGS",
        user_id=current_user.id,
        company_id=company_id,
        details={"limit": limit, "offset": offset}
    )

    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "company_id": log.company_id,
                "ai_request_text": log.ai_request_text,
                "ai_capability": log.ai_capability,
                "ai_decision": log.ai_decision,
                "ai_scope_valid": log.ai_scope_valid,
                "ai_required_role": log.ai_required_role,
                "ai_user_role": log.ai_user_role,
                "ai_severity": log.ai_severity,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/ai/approve")
def approve_ai_request(
    approval: AIApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Approve pending AI request - Superadmin only"""
    # For now, just log the approval (no actual approval workflow implemented)
    AuditService.log_admin_action(
        db=db,
        action="APPROVE_AI_REQUEST",
        user_id=current_user.id,
        company_id=None,
        details=approval.dict()
    )

    return {"message": "AI request approved successfully"}


@router.get("/ai/trust-scores")
def get_trust_scores(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get trust scores for users - Superadmin only"""
    query = db.query(User).order_by(User.trust_score.desc())

    if company_id:
        query = query.filter(User.company_id == company_id)

    users = query.limit(limit).all()

    return {
        "trust_scores": [
            {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "trust_score": user.trust_score,
                "trust_tier": TrustService.get_trust_tier(user.trust_score),
                "access_limits": TrustService.get_access_limits(user.trust_score),
                "company_id": user.company_id,
                "role": user.role.value
            }
            for user in users
        ]
    }


@router.patch("/users/{user_id}/trust-score")
def update_trust_score(
    user_id: int,
    trust_update: TrustScoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Manually update user trust score - Superadmin only"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    old_score = target_user.trust_score
    target_user.trust_score = trust_update.new_score
    db.commit()

    # Log manual trust score update
    AuditService.log_admin_action(
        db=db,
        action="MANUAL_TRUST_SCORE_UPDATE",
        user_id=current_user.id,
        company_id=target_user.company_id,
        details={
            "target_user_id": user_id,
            "old_score": old_score,
            "new_score": trust_update.new_score,
            "reason": trust_update.reason
        }
    )

    return {
        "message": "Trust score updated successfully",
        "old_score": old_score,
        "new_score": trust_update.new_score,
        "new_tier": TrustService.get_trust_tier(trust_update.new_score)
    }


@router.post("/users/{user_id}/reset-trust")
def reset_user_trust(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Reset user trust score to maximum - Superadmin only"""
    success = TrustService.reset_trust_score(db, user_id, current_user.id, "Admin reset")

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User trust score reset to maximum"}


@router.get("/ai/trust-history/{user_id}")
def get_user_trust_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Get trust score history for a user - Superadmin only"""
    history = TrustService.get_trust_history(db, user_id, days)

    return {
        "user_id": user_id,
        "history": history.get(user_id, []),
        "days": days
    }


@router.get("/ai/threat-monitor")
def get_live_violations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    """Get live AI violation feed - Superadmin only"""
    violations = ThreatMonitorService.get_live_violations(db, company_id, limit)

    return {
        "violations": violations,
        "total": len(violations),
        "limit": limit
    }


@router.get("/ai/risk-heatmap")
def get_risk_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    company_id: Optional[int] = Query(None),
    time_range_hours: int = Query(24, ge=1, le=168)  # Max 1 week
):
    """Get AI risk heat map data - Superadmin only"""
    heatmap = ThreatMonitorService.get_risk_heatmap(db, company_id, time_range_hours)

    return RiskHeatMapData(
        company_id=company_id,
        time_range_hours=time_range_hours,
        risk_levels=heatmap
    )


@router.post("/ai/compliance-export")
def export_compliance_report(
    export_request: ComplianceExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Export compliance report - Superadmin only"""
    try:
        result = ComplianceExportService.export_report(db, export_request)

        # Log export action
        AuditService.log_admin_action(
            db=db,
            action="EXPORT_COMPLIANCE_REPORT",
            user_id=current_user.id,
            company_id=export_request.company_id,
            details={
                "format": export_request.format,
                "date_range": f"{export_request.start_date} to {export_request.end_date}",
                "include_logs": export_request.include_logs,
                "include_trust_history": export_request.include_trust_history
            }
        )

        if export_request.format.lower() == "pdf":
            from fastapi.responses import StreamingResponse
            import io

            return StreamingResponse(
                io.BytesIO(result["data"]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
            )
        else:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                content=json.loads(result["data"]),
                headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/ai/webhook-config")
def configure_alert_webhook(
    webhook_config: WebhookAlertConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Configure webhook for AI alerts - Superadmin only"""
    # For now, store in memory (in production, store in database)
    # This is a placeholder - implement proper webhook config storage

    AuditService.log_admin_action(
        db=db,
        action="CONFIGURE_AI_WEBHOOK",
        user_id=current_user.id,
        company_id=None,
        details={
            "url": webhook_config.url,
            "enabled": webhook_config.enabled,
            "alert_types": webhook_config.alert_types
        }
    )

    return {"message": "AI alert webhook configured successfully"}


# Audit Chain Verification Endpoints

@router.get("/audit-chain/verify/{chain_id}")
def verify_audit_chain(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Verify integrity of an audit chain - Superadmin only"""
    is_valid, issues = AuditChainService.verify_chain_integrity(db, chain_id)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VERIFY_AUDIT_CHAIN",
        user_id=current_user.id,
        company_id=None,
        details={
            "chain_id": chain_id,
            "is_valid": is_valid,
            "issues_count": len(issues)
        }
    )

    return {
        "chain_id": chain_id,
        "is_valid": is_valid,
        "issues": issues,
        "verified_at": datetime.utcnow().isoformat()
    }


@router.get("/audit-chain/stats/{chain_id}")
def get_audit_chain_stats(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Get statistics for an audit chain - Superadmin only"""
    stats = AuditChainService.get_chain_stats(db, chain_id)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="VIEW_AUDIT_CHAIN_STATS",
        user_id=current_user.id,
        company_id=None,
        details={"chain_id": chain_id}
    )

    return stats


@router.get("/audit-chain/replay/{chain_id}")
def replay_audit_chain(
    chain_id: str,
    start_sequence: int = Query(0, ge=0),
    end_sequence: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Replay audit chain entries - Superadmin only"""
    replay_data = AuditChainService.replay_chain(db, chain_id, start_sequence, end_sequence)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="REPLAY_AUDIT_CHAIN",
        user_id=current_user.id,
        company_id=None,
        details={
            "chain_id": chain_id,
            "start_sequence": start_sequence,
            "end_sequence": end_sequence,
            "entries_returned": len(replay_data)
        }
    )

    return {
        "chain_id": chain_id,
        "start_sequence": start_sequence,
        "end_sequence": end_sequence,
        "entries": replay_data
    }


@router.get("/audit-chain/tampering/{chain_id}")
def detect_chain_tampering(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """Detect tampering incidents in an audit chain - Superadmin only"""
    incidents = AuditChainService.detect_tampering(db, chain_id)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="DETECT_CHAIN_TAMPERING",
        user_id=current_user.id,
        company_id=None,
        details={
            "chain_id": chain_id,
            "incidents_found": len(incidents)
        }
    )

    return {
        "chain_id": chain_id,
        "tampering_incidents": incidents,
        "detected_at": datetime.utcnow().isoformat()
    }


@router.get("/audit-chain/all-chains")
def list_all_chains(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """List all audit chains with their stats - Superadmin only"""
    from sqlalchemy import distinct

    # Get unique chain IDs
    chain_ids = db.query(distinct(AuditChain.chain_id)).all()
    chains = []

    for (chain_id,) in chain_ids:
        stats = AuditChainService.get_chain_stats(db, chain_id)
        chains.append(stats)

    # Log admin action
    AuditService.log_admin_action(
        db=db,
        action="LIST_AUDIT_CHAINS",
        user_id=current_user.id,
        company_id=None,
        details={"chains_count": len(chains)}
    )

    return {
        "chains": chains,
        "total_chains": len(chains)
    }
