from .models.user import Role
from fastapi import Depends, HTTPException, status, Path
from .deps import get_current_user

# Static permissions map: Role -> list of permissions
PERMISSIONS_MAP = {
    Role.SUPERADMIN: [
        "user.create",
        "user.read",
        "user.update",
        "user.delete",
        "company.create",
        "company.read",
        "company.update",
        "company.delete",
        "profile.create",
        "profile.read",
        "profile.update",
        "profile.delete",
        "attendance.create",
        "attendance.read",
        "attendance.update",
        "attendance.delete",
        "leave.create",
        "leave.read",
        "leave.update",
        "leave.delete",
        "shift.create",
        "shift.read",
        "shift.update",
        "shift.delete",
        "task.create",
        "task.read",
        "task.update",
        "task.delete",
        "notification.create",
        "notification.read",
        "notification.update",
        "notification.delete",
        "document.create",
        "document.read",
        "document.update",
        "document.delete",
        "workflow.create",
        "workflow.read",
        "workflow.update",
        "workflow.delete",
        "report.read",
        "admin.full_access"
    ],
    Role.COMPANYADMIN: [
        "user.create",
        "user.read",
        "user.update",
        "user.delete",
        "company.read",
        "company.update",
        "profile.create",
        "profile.read",
        "profile.update",
        "profile.delete",
        "attendance.read",
        "attendance.update",
        "leave.create",
        "leave.read",
        "leave.update",
        "leave.delete",
        "shift.create",
        "shift.read",
        "shift.update",
        "shift.delete",
        "task.create",
        "task.read",
        "task.update",
        "task.delete",
        "notification.create",
        "notification.read",
        "notification.update",
        "notification.delete",
        "document.create",
        "document.read",
        "document.update",
        "document.delete",
        "workflow.create",
        "workflow.read",
        "workflow.update",
        "workflow.delete",
        "report.read"
    ],
    Role.MANAGER: [
        "user.read",
        "profile.read",
        "profile.update",
        "attendance.read",
        "leave.create",
        "leave.read",
        "leave.update",
        "leave.approve",
        "shift.create",
        "shift.read",
        "shift.update",
        "shift.delete",
        "task.create",
        "task.read",
        "task.update",
        "task.delete",
        "notification.create",
        "notification.read",
        "notification.update",
        "document.read",
        "document.update",
        "workflow.read",
        "workflow.update",
        "report.read"
    ],
    Role.EMPLOYEE: [
        "user.read",
        "profile.read",
        "profile.update",
        "attendance.create",
        "attendance.read",
        "attendance.update",
        "leave.create",
        "leave.read",
        "shift.read",
        "task.read",
        "task.update",
        "notification.read",
        "document.read"
    ]
}

def has_permission(user, permission: str) -> bool:
    """Check if user has the required permission based on their role."""
    if not user or not user.role:
        return False
    user_permissions = PERMISSIONS_MAP.get(user.role, [])
    return permission in user_permissions

def require_permission(permission: str):
    """Dependency function to require a specific permission."""
    def dependency(user = Depends(get_current_user)):
        if not has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission} required"
            )
        return user
    return dependency

def requires_role(role: str):
    """Dependency function to require a specific role."""
    def dependency(user = Depends(get_current_user)):
        if not user or user.role.value != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {role} required"
            )
        return user
    return dependency

def company_isolation(company_id: int = Path(...), user = Depends(get_current_user)):
    """Dependency function to enforce company isolation."""
    if user.role.value == "SuperAdmin":
        return user  # SuperAdmin can access all
    if user.role.value == "CompanyAdmin" and user.company_id == company_id:
        return user  # CompanyAdmin can access their own company
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: company isolation"
    )
