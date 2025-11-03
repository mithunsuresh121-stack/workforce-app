from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_db
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.user import User, UserRole
from app.core.rbac import RBACService, require_company_admin, require_department_admin, require_team_lead
from app.deps import get_current_user

router = APIRouter(prefix="/api/org", tags=["organization"])

# Pydantic schemas
class DepartmentCreate(BaseModel):
    name: str
    company_id: int

class DepartmentResponse(BaseModel):
    id: int
    name: str
    company_id: int

    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    name: str
    department_id: int

class TeamResponse(BaseModel):
    id: int
    name: str
    department_id: int

    class Config:
        from_attributes = True

class UserOrgAssign(BaseModel):
    user_id: int
    department_id: Optional[int] = None
    team_id: Optional[int] = None

class OrgTreeResponse(BaseModel):
    departments: List[dict]
    teams: List[dict]
    users: List[dict]

# Department endpoints
@router.post("/department", response_model=DepartmentResponse)
def create_department(
    dept: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin)
):
    """Create a new department (Company Admin only)"""
    if not RBACService.can_manage_department(current_user, dept.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create departments in this company"
        )

    # Verify company exists and belongs to user
    if current_user.company_id != dept.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create departments in your own company"
        )

    department = CompanyDepartment(
        name=dept.name,
        company_id=dept.company_id
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.get("/department/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get department details"""
    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    if not RBACService.can_access_company(current_user, department.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return department

@router.get("/departments", response_model=List[DepartmentResponse])
def get_company_departments(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all departments for a company"""
    if not RBACService.can_access_company(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    departments = db.query(CompanyDepartment).filter(CompanyDepartment.company_id == company_id).all()
    return departments

# Team endpoints
@router.post("/team", response_model=TeamResponse)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin)
):
    """Create a new team (Company Admin or Department Admin)"""
    # Check if department exists and user can manage it
    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == team.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    if not RBACService.can_manage_department(current_user, department.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create teams in this department"
        )

    team_obj = CompanyTeam(
        name=team.name,
        department_id=team.department_id
    )
    db.add(team_obj)
    db.commit()
    db.refresh(team_obj)
    return team_obj

@router.get("/team/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get team details"""
    team = db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == team.department_id).first()
    if not RBACService.can_access_company(current_user, department.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return team

@router.get("/teams", response_model=List[TeamResponse])
def get_department_teams(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all teams for a department"""
    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    if not RBACService.can_access_company(current_user, department.company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    teams = db.query(CompanyTeam).filter(CompanyTeam.department_id == department_id).all()
    return teams

# User assignment endpoints
@router.patch("/users/{user_id}/assign-org")
def assign_user_org(
    user_id: int,
    assignment: UserOrgAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign user to department/team (Admin roles only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if current user can manage target user
    if not RBACService.can_manage_users(current_user, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage this user"
        )

    # Validate department and team if provided
    if assignment.department_id:
        department = db.query(CompanyDepartment).filter(CompanyDepartment.id == assignment.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        if department.company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department must belong to user's company"
            )

    if assignment.team_id:
        team = db.query(CompanyTeam).filter(CompanyTeam.id == assignment.team_id).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        if assignment.department_id and team.department_id != assignment.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team must belong to the specified department"
            )

    # Update user
    user.department_id = assignment.department_id
    user.team_id = assignment.team_id
    db.commit()

    return {"message": "User organization assignment updated successfully"}

# Organization tree endpoint
@router.get("/tree", response_model=OrgTreeResponse)
def get_org_tree(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete organization tree for a company"""
    if not RBACService.can_access_company(current_user, company_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    departments = db.query(CompanyDepartment).filter(CompanyDepartment.company_id == company_id).all()
    teams = db.query(CompanyTeam).join(CompanyDepartment).filter(CompanyDepartment.company_id == company_id).all()
    users = db.query(User).filter(User.company_id == company_id).all()

    return {
        "departments": [
            {
                "id": dept.id,
                "name": dept.name,
                "company_id": dept.company_id,
                "teams": [team.id for team in teams if team.department_id == dept.id],
                "user_count": len([u for u in users if u.department_id == dept.id])
            }
            for dept in departments
        ],
        "teams": [
            {
                "id": team.id,
                "name": team.name,
                "department_id": team.department_id,
                "user_count": len([u for u in users if u.team_id == team.id])
            }
            for team in teams
        ],
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "department_id": user.department_id,
                "team_id": user.team_id
            }
            for user in users
        ]
    }
