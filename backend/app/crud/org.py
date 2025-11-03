import structlog
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam
from app.models.company import Company
from app.models.user import User

logger = structlog.get_logger(__name__)

def create_department(db: Session, company_id: int, name: str) -> CompanyDepartment:
    """Create a new department"""
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise ValueError("Company not found")

    department = CompanyDepartment(
        name=name,
        company_id=company_id
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    logger.info("Department created", department_id=department.id, company_id=company_id)
    return department

def get_department(db: Session, department_id: int) -> Optional[CompanyDepartment]:
    """Get a department by ID"""
    return db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()

def get_departments_by_company(db: Session, company_id: int) -> List[CompanyDepartment]:
    """Get all departments for a company"""
    return db.query(CompanyDepartment).filter(CompanyDepartment.company_id == company_id).all()

def update_department(db: Session, department_id: int, name: Optional[str] = None) -> CompanyDepartment:
    """Update department name"""
    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
    if not department:
        raise ValueError("Department not found")
    
    if name:
        department.name = name
    
    db.commit()
    db.refresh(department)
    logger.info("Department updated", department_id=department_id)
    return department

def delete_department(db: Session, department_id: int) -> bool:
    """Delete a department"""
    department = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
    if not department:
        return False
    
    db.delete(department)
    db.commit()
    logger.info("Department deleted", department_id=department_id)
    return True

def create_team(db: Session, department_id: int, name: str) -> CompanyTeam:
    """Create a new team"""
    db_department = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
    if not db_department:
        raise ValueError("Department not found")

    team = CompanyTeam(
        name=name,
        department_id=department_id
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    logger.info("Team created", team_id=team.id, department_id=department_id)
    return team

def get_team(db: Session, team_id: int) -> Optional[CompanyTeam]:
    """Get a team by ID"""
    return db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()

def get_teams_by_department(db: Session, department_id: int) -> List[CompanyTeam]:
    """Get all teams for a department"""
    return db.query(CompanyTeam).filter(CompanyTeam.department_id == department_id).all()

def update_team(db: Session, team_id: int, name: Optional[str] = None) -> CompanyTeam:
    """Update team name"""
    team = db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()
    if not team:
        raise ValueError("Team not found")
    
    if name:
        team.name = name
    
    db.commit()
    db.refresh(team)
    logger.info("Team updated", team_id=team_id)
    return team

def delete_team(db: Session, team_id: int) -> bool:
    """Delete a team"""
    team = db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()
    if not team:
        return False
    
    db.delete(team)
    db.commit()
    logger.info("Team deleted", team_id=team_id)
    return True
