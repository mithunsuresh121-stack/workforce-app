from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.channels import Channel
from app.models.meetings import Meeting
from app.deps import get_current_user

class RBACService:
    @staticmethod
    def check_superadmin(user: User) -> bool:
        """Check if user is SUPERADMIN"""
        return user.role == UserRole.SUPERADMIN

    @staticmethod
    def check_company_admin(user: User, company_id: int) -> bool:
        """Check if user is COMPANY_ADMIN for the given company"""
        return (user.role == UserRole.COMPANY_ADMIN and
                user.company_id == company_id)

    @staticmethod
    def check_department_admin(user: User, department_id: int) -> bool:
        """Check if user is DEPARTMENT_ADMIN for the given department"""
        return (user.role == UserRole.DEPARTMENT_ADMIN and
                user.department_id == department_id)

    @staticmethod
    def check_team_lead(user: User, team_id: int) -> bool:
        """Check if user is TEAM_LEAD for the given team"""
        return (user.role == UserRole.TEAM_LEAD and
                user.team_id == team_id)

    @staticmethod
    def check_employee(user: User) -> bool:
        """Check if user is EMPLOYEE"""
        return user.role == UserRole.EMPLOYEE

    @staticmethod
    def can_access_company(user: User, company_id: int) -> bool:
        """Check if user can access company resources"""
        if user.role == UserRole.SUPERADMIN:
            return True
        # Strict scoping: COMPANY_ADMIN can only access their own company
        if user.role == UserRole.COMPANY_ADMIN:
            return user.company_id == company_id
        # Sub-org roles can only access their company's resources
        return user.company_id == company_id

    @staticmethod
    def can_manage_department(user: User, department_id: int) -> bool:
        """Check if user can manage department"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.role == UserRole.COMPANY_ADMIN and user.company_id:
            # Check if department belongs to user's company
            return True  # Will be checked in endpoint
        return user.role == UserRole.DEPARTMENT_ADMIN and user.department_id == department_id

    @staticmethod
    def can_manage_team(user: User, team_id: int) -> bool:
        """Check if user can manage team"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.role == UserRole.COMPANY_ADMIN and user.company_id:
            return True
        if user.role == UserRole.DEPARTMENT_ADMIN and user.department_id:
            # Check if team belongs to user's department
            return True  # Will be checked in endpoint
        return user.role == UserRole.TEAM_LEAD and user.team_id == team_id

    @staticmethod
    def can_create_channel(user: User, team_id: Optional[int] = None, department_id: Optional[int] = None) -> bool:
        """Check if user can create channels"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.role == UserRole.COMPANY_ADMIN:
            return True
        if user.role == UserRole.DEPARTMENT_ADMIN and department_id == user.department_id:
            return True
        if user.role == UserRole.TEAM_LEAD and team_id == user.team_id:
            return True
        return False

    @staticmethod
    def can_join_channel(user: User, channel: Channel) -> bool:
        """Check if user can join a channel"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.company_id != channel.company_id:
            return False

        # Public channels - anyone in company can join
        if channel.type.name == "PUBLIC":
            return True

        # Private channels - check org membership
        if channel.team_id:
            return user.team_id == channel.team_id
        if channel.department_id:
            return user.department_id == channel.department_id

        return False

    @staticmethod
    def can_create_meeting(user: User, team_id: Optional[int] = None, department_id: Optional[int] = None) -> bool:
        """Check if user can create meetings"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.role == UserRole.COMPANY_ADMIN:
            return True
        if user.role == UserRole.DEPARTMENT_ADMIN and department_id == user.department_id:
            return True
        if user.role == UserRole.TEAM_LEAD and team_id == user.team_id:
            return True
        return False

    @staticmethod
    def can_join_meeting(user: User, meeting: Meeting) -> bool:
        """Check if user can join a meeting"""
        if user.role == UserRole.SUPERADMIN:
            return True
        if user.company_id != meeting.company_id:
            return False

        # Check org membership
        if meeting.team_id:
            return user.team_id == meeting.team_id
        if meeting.department_id:
            return user.department_id == meeting.department_id

        return True  # Company-wide meeting

    @staticmethod
    def can_manage_users(user: User, target_user: User) -> bool:
        """Check if user can manage other users"""
        if user.role == UserRole.SUPERADMIN:
            return True
        # Cross-org prevention: users can only manage users in their own org
        if user.company_id != target_user.company_id:
            return False
        if user.role == UserRole.COMPANY_ADMIN and user.company_id == target_user.company_id:
            return True
        if user.role == UserRole.DEPARTMENT_ADMIN and user.department_id == target_user.department_id:
            return True
        if user.role == UserRole.TEAM_LEAD and user.team_id == target_user.team_id:
            return True
        return False

    @staticmethod
    def can_send_cross_org_message(user: User, target_user: User) -> bool:
        """Check if user can send direct messages across org boundaries"""
        return user.company_id == target_user.company_id

    @staticmethod
    def can_invite_to_channel(user: User, channel: Channel, target_user: User) -> bool:
        """Check if user can invite others to channels across org boundaries"""
        # Must be in same company
        if user.company_id != target_user.company_id:
            return False
        # Channel must be in same company
        if channel.company_id != user.company_id:
            return False
        return True

    @staticmethod
    def can_invite_to_meeting(user: User, meeting: Meeting, target_user: User) -> bool:
        """Check if user can invite others to meetings across org boundaries"""
        # Must be in same company
        if user.company_id != target_user.company_id:
            return False
        # Meeting must be in same company
        if meeting.company_id != user.company_id:
            return False
        return True

# Dependency functions for FastAPI

def require_superadmin(current_user: User = Depends(get_current_user)):
    """Require SUPERADMIN role"""
    if not RBACService.check_superadmin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )
    return current_user

def require_company_admin(current_user: User = Depends(get_current_user)):
    """Require COMPANY_ADMIN role"""
    if not RBACService.check_company_admin(current_user, current_user.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company admin access required"
        )
    return current_user

def require_department_admin(current_user: User = Depends(get_current_user)):
    """Require DEPARTMENT_ADMIN role"""
    if not RBACService.check_department_admin(current_user, current_user.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Department admin access required"
        )
    return current_user

def require_team_lead(current_user: User = Depends(get_current_user)):
    """Require TEAM_LEAD role"""
    if not RBACService.check_team_lead(current_user, current_user.team_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team lead access required"
        )
    return current_user

def require_employee(current_user: User = Depends(get_current_user)):
    """Require EMPLOYEE role or higher"""
    if current_user.role == UserRole.EMPLOYEE:
        return current_user
    # Higher roles also have employee permissions
    return current_user

def require_company_access(company_id: int, current_user: User = Depends(get_current_user)):
    """Require access to specific company"""
    if not RBACService.can_access_company(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    return current_user

def require_channel_access(channel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Require access to specific channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    if not RBACService.can_join_channel(current_user, channel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this channel"
        )
    return current_user

def require_meeting_access(meeting_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Require access to specific meeting"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )
    if not RBACService.can_join_meeting(current_user, meeting):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this meeting"
        )
    return current_user
