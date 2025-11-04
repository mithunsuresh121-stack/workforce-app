from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.rbac import require_superadmin, require_company_access
from app.services.analytics_service import AnalyticsService
from app.services.audit_service import AuditService
from app.services.security_service import SecurityService
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
