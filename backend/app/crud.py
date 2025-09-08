from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
import logging
from .models.user import User
from .models.company import Company
from .models.task import Task, TaskStatus, TaskPriority
from .models.leave import Leave
from .models.shift import Shift
from .models.employee_profile import EmployeeProfile
from .models.payroll import (
    Employee,
    Salary,
    Allowance,
    Deduction,
    Bonus,
    PayrollRun,
    PayrollEntry
)
from .models.attendance import Attendance, Break
from .auth import hash_password, verify_password
from typing import Optional, List

# Company operations
def get_company_by_id(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()

def get_company_by_name(db: Session, name: str) -> Optional[Company]:
    return db.query(Company).filter(Company.name == name).first()

def create_company(db: Session, name: str, domain: Optional[str], contact_email: str, 
                  contact_phone: Optional[str], address: Optional[str], city: Optional[str],
                  state: Optional[str], country: Optional[str], postal_code: Optional[str]) -> Company:
    company = Company(
        name=name,
        domain=domain,
        contact_email=contact_email,
        contact_phone=contact_phone,
        address=address,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def list_companies(db: Session) -> List[Company]:
    return db.query(Company).filter(Company.is_active == True).all()

def delete_company(db: Session, company_id: int) -> bool:
    company = get_company_by_id(db, company_id)
    if not company:
        return False
    
    # Soft delete - set is_active to False
    company.is_active = False
    db.commit()
    db.refresh(company)
    return True

# User operations
def get_user_by_email(db: Session, email: str, company_id: int) -> Optional[User]:
    stmt = select(User).where(User.email == email, User.company_id == company_id)
    return db.scalar(stmt)

def get_users_by_email(db: Session, email: str) -> List[User]:
    """Find all users with the given email across all companies"""
    return db.query(User).filter(User.email == email, User.is_active == True).all()

def get_user_by_email_only(db: Session, email: str) -> Optional[User]:
    """Find a user by email (first match if multiple exist)"""
    users = get_users_by_email(db, email)
    if len(users) == 1:
        return users[0]
    elif len(users) > 1:
        # Return None to indicate ambiguous login
        return None
    return None

def create_user(db: Session, email: str, password: str, full_name: str, role: str, company_id: Optional[int] = None) -> User:
    user = User(
        email=email, 
        hashed_password=hash_password(password), 
        full_name=full_name, 
        role=role, 
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str, company_id: int) -> Optional[User]:
    user = get_user_by_email(db, email, company_id)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def authenticate_user_by_email(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user by email only (without company_id)"""
    user = get_user_by_email_only(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def list_users_by_company(db: Session, company_id: int) -> List[User]:
    return db.query(User).filter(User.company_id == company_id, User.is_active == True).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, email: Optional[str] = None, password: Optional[str] = None, full_name: Optional[str] = None, role: Optional[str] = None, company_id: Optional[int] = None) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if email is not None:
        user.email = email
    if password is not None:
        user.hashed_password = hash_password(password)
    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if company_id is not None:
        user.company_id = company_id
    user.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    # Soft delete - set is_active to False
    user.is_active = False
    db.commit()
    return True

# Task operations
def list_tasks(db: Session, company_id: int) -> List[Task]:
    tasks = db.query(Task).filter(Task.company_id == company_id).all()
    return tasks

def create_task(db: Session, assigning_user: User, title: str, description: str, status: str, priority: str, due_at: Optional[datetime], assignee_id: Optional[int] = None, company_id: Optional[int] = None) -> Task:
    # Use provided company_id or fall back to assigning_user's company_id
    company_id = company_id or assigning_user.company_id

    # Validate assignee company matches assigning user's company unless superadmin
    if assignee_id:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise ValueError("Assignee user not found")
        if assigning_user.role != "SuperAdmin" and assignee.company_id != company_id:
            raise ValueError("Cannot assign task to user outside your company")

    # Normalize status and priority to actual enum members, not strings
    status_map = {
        "pending": TaskStatus.PENDING,
        "in progress": TaskStatus.IN_PROGRESS,
        "completed": TaskStatus.COMPLETED,
        "overdue": TaskStatus.OVERDUE,
        "PENDING": TaskStatus.PENDING,
        "IN_PROGRESS": TaskStatus.IN_PROGRESS,
        "COMPLETED": TaskStatus.COMPLETED,
        "OVERDUE": TaskStatus.OVERDUE,
        "Pending": TaskStatus.PENDING,
        "In Progress": TaskStatus.IN_PROGRESS,
        "Completed": TaskStatus.COMPLETED,
        "Overdue": TaskStatus.OVERDUE
    }
    priority_map = {
        "low": TaskPriority.LOW,
        "medium": TaskPriority.MEDIUM,
        "high": TaskPriority.HIGH,
        "LOW": TaskPriority.LOW,
        "MEDIUM": TaskPriority.MEDIUM,
        "HIGH": TaskPriority.HIGH,
        "Low": TaskPriority.LOW,
        "Medium": TaskPriority.MEDIUM,
        "High": TaskPriority.HIGH
    }

    # Handle both string and enum inputs
    if hasattr(status, 'value'):
        status_value = status.value
    else:
        status_value = str(status)

    if hasattr(priority, 'value'):
        priority_value = priority.value
    else:
        priority_value = str(priority)

    if status_value not in status_map:
        raise ValueError(f"Invalid task status: {status_value}")
    if priority_value not in priority_map:
        raise ValueError(f"Invalid task priority: {priority_value}")

    task = Task(
        company_id=company_id,
        title=title,
        description=description,
        status=status_map[status_value],
        priority=priority_map[priority_value],
        due_at=due_at,
        assignee_id=assignee_id,
        assigned_by=assigning_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task_by_id(db: Session, task_id: int, company_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id, Task.company_id == company_id).first()

def update_task(db: Session, updating_user: User, task_id: int, title: Optional[str] = None, description: Optional[str] = None,
                status: Optional[str] = None, priority: Optional[str] = None, due_at: Optional[datetime] = None,
                assignee_id: Optional[int] = None) -> Optional[Task]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    # Enforce role-based permissions
    if updating_user.role == "Employee" and task.assignee_id != updating_user.id:
        raise PermissionError("Employees can only update their own tasks")
    if updating_user.role == "Manager" and task.company_id != updating_user.company_id:
        raise PermissionError("Managers can only update tasks within their company")

    # Validate assignee company matches updating user's company unless superadmin
    if assignee_id:
        assignee = db.query(User).filter(User.id == assignee_id).first()
        if not assignee:
            raise ValueError("Assignee user not found")
        if updating_user.role != "SuperAdmin" and assignee.company_id != updating_user.company_id:
            raise ValueError("Cannot assign task to user outside your company")

    # Normalize status and priority to actual enum members, not strings
    status_map = {
        "Pending": TaskStatus.PENDING,
        "PENDING": TaskStatus.PENDING,
        "In Progress": TaskStatus.IN_PROGRESS,
        "IN_PROGRESS": TaskStatus.IN_PROGRESS,
        "Completed": TaskStatus.COMPLETED,
        "COMPLETED": TaskStatus.COMPLETED,
        "Overdue": TaskStatus.OVERDUE,
        "OVERDUE": TaskStatus.OVERDUE
    }
    priority_map = {
        "Low": TaskPriority.LOW,
        "LOW": TaskPriority.LOW,
        "Medium": TaskPriority.MEDIUM,
        "MEDIUM": TaskPriority.MEDIUM,
        "High": TaskPriority.HIGH,
        "HIGH": TaskPriority.HIGH
    }
    normalized_status = status_map.get(status, None) if status else None
    normalized_priority = priority_map.get(priority, None) if priority else None

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if normalized_status is not None:
        task.status = normalized_status
    if normalized_priority is not None:
        task.priority = normalized_priority
    if due_at is not None:
        task.due_at = due_at
    if assignee_id is not None:
        task.assignee_id = assignee_id
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True

# Leave operations
def create_leave(db: Session, tenant_id: str, employee_id: int, type: str, 
                start_at: datetime, end_at: datetime, status: str = "Pending") -> Leave:
    leave = Leave(
        tenant_id=tenant_id,
        employee_id=employee_id,
        type=type,
        start_at=start_at,
        end_at=end_at,
        status=status
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

def get_leave_by_id(db: Session, leave_id: int) -> Optional[Leave]:
    return db.query(Leave).filter(Leave.id == leave_id).first()

def list_leaves_by_employee(db: Session, employee_id: int) -> List[Leave]:
    return db.query(Leave).filter(Leave.employee_id == employee_id).all()

def list_leaves_by_tenant(db: Session, tenant_id: str) -> List[Leave]:
    return db.query(Leave).filter(Leave.tenant_id == tenant_id).all()

def update_leave_status(db: Session, leave_id: int, status: str) -> Optional[Leave]:
    leave = get_leave_by_id(db, leave_id)
    if not leave:
        return None
    leave.status = status
    db.commit()
    db.refresh(leave)
    return leave

def delete_leave(db: Session, leave_id: int) -> bool:
    leave = get_leave_by_id(db, leave_id)
    if not leave:
        return False
    db.delete(leave)
    db.commit()
    return True

# Shift operations
def create_shift(db: Session, tenant_id: str, employee_id: int, 
                start_at: datetime, end_at: datetime, location: Optional[str] = None) -> Shift:
    shift = Shift(
        tenant_id=tenant_id,
        employee_id=employee_id,
        start_at=start_at,
        end_at=end_at,
        location=location
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

def get_shift_by_id(db: Session, shift_id: int) -> Optional[Shift]:
    return db.query(Shift).filter(Shift.id == shift_id).first()

def list_shifts_by_employee(db: Session, employee_id: int) -> List[Shift]:
    return db.query(Shift).filter(Shift.employee_id == employee_id).all()

def list_shifts_by_tenant(db: Session, tenant_id: str) -> List[Shift]:
    return db.query(Shift).filter(Shift.tenant_id == tenant_id).all()

def update_shift(db: Session, shift_id: int, start_at: datetime, 
                end_at: datetime, location: Optional[str] = None) -> Optional[Shift]:
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        return None
    shift.start_at = start_at
    shift.end_at = end_at
    shift.location = location
    db.commit()
    db.refresh(shift)
    return shift

def delete_shift(db: Session, shift_id: int) -> bool:
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        return False
    db.delete(shift)
    db.commit()
    return True

# EmployeeProfile operations
def get_employee_profile_by_user_id(db: Session, user_id: int, company_id: int) -> Optional[EmployeeProfile]:
    return db.query(EmployeeProfile).filter(
        EmployeeProfile.user_id == user_id,
        EmployeeProfile.company_id == company_id,
        EmployeeProfile.is_active == True
    ).first()

def list_employee_profiles_by_company(db: Session, company_id: int) -> List[EmployeeProfile]:
    return db.query(EmployeeProfile).filter(
        EmployeeProfile.company_id == company_id,
        EmployeeProfile.is_active == True
    ).all()

def create_employee_profile(db: Session, user_id: int, company_id: int, department: str = None, position: str = None,
                            phone: str = None, hire_date = None, manager_id: int = None) -> EmployeeProfile:
    profile = EmployeeProfile(
        user_id=user_id,
        company_id=company_id,
        department=department,
        position=position,
        phone=phone,
        hire_date=hire_date,
        manager_id=manager_id
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_employee_profile(db: Session, user_id: int, company_id: int, department: str = None, position: str = None,
                            phone: str = None, hire_date = None, manager_id: int = None, is_active: bool = None) -> Optional[EmployeeProfile]:
    profile = get_employee_profile_by_user_id(db, user_id, company_id)
    if not profile:
        return None
    if department is not None:
        profile.department = department
    if position is not None:
        profile.position = position
    if phone is not None:
        profile.phone = phone
    if hire_date is not None:
        profile.hire_date = hire_date
    if manager_id is not None:
        profile.manager_id = manager_id
    if is_active is not None:
        profile.is_active = is_active
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile

def delete_employee_profile(db: Session, user_id: int, company_id: int) -> bool:
    profile = get_employee_profile_by_user_id(db, user_id, company_id)
    if not profile:
        return False
    profile.is_active = False
    db.commit()
    return True

# Payroll Employee operations
def create_payroll_employee(db: Session, tenant_id: str, user_id: int, employee_id: str,
                           department: str = None, position: str = None, hire_date = None,
                           base_salary: float = 0.0, status: str = "Active") -> Employee:
    employee = Employee(
        tenant_id=tenant_id,
        user_id=user_id,
        employee_id=employee_id,
        department=department,
        position=position,
        hire_date=hire_date,
        base_salary=base_salary,
        status=status
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

def get_payroll_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_payroll_employee_by_employee_id(db: Session, employee_id: str, tenant_id: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.employee_id == employee_id, Employee.tenant_id == tenant_id).first()

def list_payroll_employees_by_tenant(db: Session, tenant_id: str) -> List[Employee]:
    return db.query(Employee).filter(Employee.tenant_id == tenant_id).all()

def update_payroll_employee(db: Session, employee_id: int, department: str = None, position: str = None,
                           hire_date = None, base_salary: float = None, status: str = None) -> Optional[Employee]:
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        return None
    if department is not None:
        employee.department = department
    if position is not None:
        employee.position = position
    if hire_date is not None:
        employee.hire_date = hire_date
    if base_salary is not None:
        employee.base_salary = base_salary
    if status is not None:
        employee.status = status
    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)
    return employee

def delete_payroll_employee(db: Session, employee_id: int) -> bool:
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        return False
    db.delete(employee)
    db.commit()
    return True

# Salary operations
def create_salary(db: Session, tenant_id: str, employee_id: int, amount: float,
                 effective_date: datetime, end_date = None) -> Salary:
    salary = Salary(
        tenant_id=tenant_id,
        employee_id=employee_id,
        amount=amount,
        effective_date=effective_date,
        end_date=end_date
    )
    db.add(salary)
    db.commit()
    db.refresh(salary)
    return salary

def get_salary_by_id(db: Session, salary_id: int) -> Optional[Salary]:
    return db.query(Salary).filter(Salary.id == salary_id).first()

def list_salaries_by_employee(db: Session, employee_id: int) -> List[Salary]:
    return db.query(Salary).filter(Salary.employee_id == employee_id).order_by(Salary.effective_date.desc()).all()

def update_salary(db: Session, salary_id: int, amount: float = None, effective_date: datetime = None,
                 end_date = None) -> Optional[Salary]:
    salary = get_salary_by_id(db, salary_id)
    if not salary:
        return None
    if amount is not None:
        salary.amount = amount
    if effective_date is not None:
        salary.effective_date = effective_date
    if end_date is not None:
        salary.end_date = end_date
    salary.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(salary)
    return salary

def delete_salary(db: Session, salary_id: int) -> bool:
    salary = get_salary_by_id(db, salary_id)
    if not salary:
        return False
    db.delete(salary)
    db.commit()
    return True

# Allowance operations
def create_allowance(db: Session, tenant_id: str, employee_id: int, name: str, amount: float,
                    type: str, is_taxable: str = "Yes", effective_date: datetime = None,
                    end_date = None) -> Allowance:
    allowance = Allowance(
        tenant_id=tenant_id,
        employee_id=employee_id,
        name=name,
        amount=amount,
        type=type,
        is_taxable=is_taxable,
        effective_date=effective_date,
        end_date=end_date
    )
    db.add(allowance)
    db.commit()
    db.refresh(allowance)
    return allowance

def get_allowance_by_id(db: Session, allowance_id: int) -> Optional[Allowance]:
    return db.query(Allowance).filter(Allowance.id == allowance_id).first()

def list_allowances_by_employee(db: Session, employee_id: int) -> List[Allowance]:
    return db.query(Allowance).filter(Allowance.employee_id == employee_id).all()

def update_allowance(db: Session, allowance_id: int, name: str = None, amount: float = None,
                    type: str = None, is_taxable: str = None, effective_date: datetime = None,
                    end_date = None) -> Optional[Allowance]:
    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        return None
    if name is not None:
        allowance.name = name
    if amount is not None:
        allowance.amount = amount
    if type is not None:
        allowance.type = type
    if is_taxable is not None:
        allowance.is_taxable = is_taxable
    if effective_date is not None:
        allowance.effective_date = effective_date
    if end_date is not None:
        allowance.end_date = end_date
    allowance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(allowance)
    return allowance

def delete_allowance(db: Session, allowance_id: int) -> bool:
    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        return False
    db.delete(allowance)
    db.commit()
    return True

# Deduction operations
def create_deduction(db: Session, tenant_id: str, employee_id: int, name: str, amount: float,
                    type: str, is_mandatory: str = "Yes", effective_date: datetime = None,
                    end_date = None) -> Deduction:
    deduction = Deduction(
        tenant_id=tenant_id,
        employee_id=employee_id,
        name=name,
        amount=amount,
        type=type,
        is_mandatory=is_mandatory,
        effective_date=effective_date,
        end_date=end_date
    )
    db.add(deduction)
    db.commit()
    db.refresh(deduction)
    return deduction

def get_deduction_by_id(db: Session, deduction_id: int) -> Optional[Deduction]:
    return db.query(Deduction).filter(Deduction.id == deduction_id).first()

def list_deductions_by_employee(db: Session, employee_id: int) -> List[Deduction]:
    return db.query(Deduction).filter(Deduction.employee_id == employee_id).all()

def update_deduction(db: Session, deduction_id: int, name: str = None, amount: float = None,
                    type: str = None, is_mandatory: str = None, effective_date: datetime = None,
                    end_date = None) -> Optional[Deduction]:
    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        return None
    if name is not None:
        deduction.name = name
    if amount is not None:
        deduction.amount = amount
    if type is not None:
        deduction.type = type
    if is_mandatory is not None:
        deduction.is_mandatory = is_mandatory
    if effective_date is not None:
        deduction.effective_date = effective_date
    if end_date is not None:
        deduction.end_date = end_date
    deduction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deduction)
    return deduction

def delete_deduction(db: Session, deduction_id: int) -> bool:
    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        return False
    db.delete(deduction)
    db.commit()
    return True

# Bonus operations
def create_bonus(db: Session, tenant_id: str, employee_id: int, name: str, amount: float,
                type: str, payment_date: datetime, status: str = "Pending") -> Bonus:
    bonus = Bonus(
        tenant_id=tenant_id,
        employee_id=employee_id,
        name=name,
        amount=amount,
        type=type,
        payment_date=payment_date,
        status=status
    )
    db.add(bonus)
    db.commit()
    db.refresh(bonus)
    return bonus

def get_bonus_by_id(db: Session, bonus_id: int) -> Optional[Bonus]:
    return db.query(Bonus).filter(Bonus.id == bonus_id).first()

def list_bonuses_by_employee(db: Session, employee_id: int) -> List[Bonus]:
    return db.query(Bonus).filter(Bonus.employee_id == employee_id).order_by(Bonus.payment_date.desc()).all()

def update_bonus(db: Session, bonus_id: int, name: str = None, amount: float = None,
                type: str = None, payment_date: datetime = None, status: str = None) -> Optional[Bonus]:
    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        return None
    if name is not None:
        bonus.name = name
    if amount is not None:
        bonus.amount = amount
    if type is not None:
        bonus.type = type
    if payment_date is not None:
        bonus.payment_date = payment_date
    if status is not None:
        bonus.status = status
    bonus.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bonus)
    return bonus

def delete_bonus(db: Session, bonus_id: int) -> bool:
    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        return False
    db.delete(bonus)
    db.commit()
    return True

# Payroll Run operations
def create_payroll_run(db: Session, tenant_id: str, period_start: datetime, period_end: datetime,
                      status: str = "Draft", processed_by: int = None) -> PayrollRun:
    payroll_run = PayrollRun(
        tenant_id=tenant_id,
        period_start=period_start,
        period_end=period_end,
        status=status,
        processed_by=processed_by
    )
    db.add(payroll_run)
    db.commit()
    db.refresh(payroll_run)
    return payroll_run

def get_payroll_run_by_id(db: Session, payroll_run_id: int) -> Optional[PayrollRun]:
    return db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()

def list_payroll_runs_by_tenant(db: Session, tenant_id: str) -> List[PayrollRun]:
    return db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id).order_by(PayrollRun.created_at.desc()).all()

def update_payroll_run(db: Session, payroll_run_id: int, status: str = None, total_gross: float = None,
                      total_deductions: float = None, total_net: float = None,
                      processed_by: int = None, processed_at: datetime = None) -> Optional[PayrollRun]:
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        return None
    if status is not None:
        payroll_run.status = status
    if total_gross is not None:
        payroll_run.total_gross = total_gross
    if total_deductions is not None:
        payroll_run.total_deductions = total_deductions
    if total_net is not None:
        payroll_run.total_net = total_net
    if processed_by is not None:
        payroll_run.processed_by = processed_by
    if processed_at is not None:
        payroll_run.processed_at = processed_at
    payroll_run.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payroll_run)
    return payroll_run

def delete_payroll_run(db: Session, payroll_run_id: int) -> bool:
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        return False
    db.delete(payroll_run)
    db.commit()
    return True

# Payroll Entry operations
def create_payroll_entry(db: Session, payroll_run_id: int, employee_id: int, base_salary: float = 0.0,
                        total_allowances: float = 0.0, total_deductions: float = 0.0,
                        total_bonuses: float = 0.0, gross_pay: float = 0.0, net_pay: float = 0.0,
                        status: str = "Pending", notes: str = None) -> PayrollEntry:
    payroll_entry = PayrollEntry(
        payroll_run_id=payroll_run_id,
        employee_id=employee_id,
        base_salary=base_salary,
        total_allowances=total_allowances,
        total_deductions=total_deductions,
        total_bonuses=total_bonuses,
        gross_pay=gross_pay,
        net_pay=net_pay,
        status=status,
        notes=notes
    )
    db.add(payroll_entry)
    db.commit()
    db.refresh(payroll_entry)
    return payroll_entry

def get_payroll_entry_by_id(db: Session, payroll_entry_id: int) -> Optional[PayrollEntry]:
    return db.query(PayrollEntry).filter(PayrollEntry.id == payroll_entry_id).first()

def list_payroll_entries_by_run(db: Session, payroll_run_id: int) -> List[PayrollEntry]:
    return db.query(PayrollEntry).filter(PayrollEntry.payroll_run_id == payroll_run_id).all()

def list_payroll_entries_by_employee(db: Session, employee_id: int) -> List[PayrollEntry]:
    return db.query(PayrollEntry).filter(PayrollEntry.employee_id == employee_id).order_by(PayrollEntry.created_at.desc()).all()

def update_payroll_entry(db: Session, payroll_entry_id: int, base_salary: float = None,
                        total_allowances: float = None, total_deductions: float = None,
                        total_bonuses: float = None, gross_pay: float = None, net_pay: float = None,
                        status: str = None, notes: str = None) -> Optional[PayrollEntry]:
    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        return None
    if base_salary is not None:
        payroll_entry.base_salary = base_salary
    if total_allowances is not None:
        payroll_entry.total_allowances = total_allowances
    if total_deductions is not None:
        payroll_entry.total_deductions = total_deductions
    if total_bonuses is not None:
        payroll_entry.total_bonuses = total_bonuses
    if gross_pay is not None:
        payroll_entry.gross_pay = gross_pay
    if net_pay is not None:
        payroll_entry.net_pay = net_pay
    if status is not None:
        payroll_entry.status = status
    if notes is not None:
        payroll_entry.notes = notes
    payroll_entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(payroll_entry)
    return payroll_entry

def delete_payroll_entry(db: Session, payroll_entry_id: int) -> bool:
    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        return False
    db.delete(payroll_entry)
    db.commit()
    return True

# Attendance operations
def create_attendance(db: Session, employee_id: int, clock_in_time: datetime,
                     notes: Optional[str] = None) -> Attendance:
    attendance = Attendance(
        employee_id=employee_id,
        clock_in_time=clock_in_time,
        notes=notes
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

def get_attendance_by_id(db: Session, attendance_id: int) -> Optional[Attendance]:
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_active_attendance_by_employee(db: Session, employee_id: int) -> Optional[Attendance]:
    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.status == "active"
    ).first()

def list_attendance_by_employee(db: Session, employee_id: int, limit: int = 50) -> List[Attendance]:
    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id
    ).order_by(Attendance.clock_in_time.desc()).limit(limit).all()

def update_attendance(db: Session, attendance_id: int, clock_out_time: Optional[datetime] = None,
                     total_hours: Optional[float] = None, overtime_hours: Optional[float] = None,
                     status: Optional[str] = None, notes: Optional[str] = None) -> Optional[Attendance]:
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance:
        return None

    if clock_out_time is not None:
        attendance.clock_out_time = clock_out_time
        # Calculate total hours if both times are present
        if attendance.clock_in_time:
            time_diff = clock_out_time - attendance.clock_in_time
            attendance.total_hours = time_diff.total_seconds() / 3600  # Convert to hours

    if total_hours is not None:
        attendance.total_hours = total_hours
    if overtime_hours is not None:
        attendance.overtime_hours = overtime_hours
    if status is not None:
        attendance.status = status
    if notes is not None:
        attendance.notes = notes

    attendance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(attendance)
    return attendance

def clock_out_attendance(db: Session, attendance_id: int, notes: Optional[str] = None) -> Optional[Attendance]:
    logging.info(f"Clocking out attendance id {attendance_id}")
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance:
        logging.error(f"Attendance id {attendance_id} not found")
        return None
    if attendance.clock_in_time.tzinfo is None:
        logging.warning(f"Attendance clock_in_time is naive, converting to UTC")
        clock_in_aware = attendance.clock_in_time.replace(tzinfo=timezone.utc)
    else:
        clock_in_aware = attendance.clock_in_time
    now = datetime.now(timezone.utc)
    total_duration = now - clock_in_aware
    total_hours = total_duration.total_seconds() / 3600.0
    updated_attendance = update_attendance(
        db=db,
        attendance_id=attendance_id,
        clock_out_time=now,
        status="completed",
        notes=notes,
        total_hours=total_hours
    )
    logging.info(f"Clocked out attendance id {attendance_id} with total hours {total_hours}")
    return updated_attendance

def delete_attendance(db: Session, attendance_id: int) -> bool:
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance:
        return False
    db.delete(attendance)
    db.commit()
    return True

# Break operations
def create_break(db: Session, attendance_id: int, break_start: datetime,
                break_type: str = "lunch") -> Break:
    break_record = Break(
        attendance_id=attendance_id,
        break_start=break_start,
        break_type=break_type
    )
    db.add(break_record)
    db.commit()
    db.refresh(break_record)
    return break_record

def get_break_by_id(db: Session, break_id: int) -> Optional[Break]:
    return db.query(Break).filter(Break.id == break_id).first()

def list_breaks_by_attendance(db: Session, attendance_id: int) -> List[Break]:
    return db.query(Break).filter(Break.attendance_id == attendance_id).order_by(Break.break_start.desc()).all()

def update_break(db: Session, break_id: int, break_end: Optional[datetime] = None,
                break_type: Optional[str] = None, duration_minutes: Optional[int] = None) -> Optional[Break]:
    break_record = get_break_by_id(db, break_id)
    if not break_record:
        return None

    if break_end is not None:
        break_record.break_end = break_end
        # Calculate duration if both times are present
        if break_record.break_start:
            time_diff = break_end - break_record.break_start
            break_record.duration_minutes = int(time_diff.total_seconds() / 60)  # Convert to minutes

    if break_type is not None:
        break_record.break_type = break_type
    if duration_minutes is not None:
        break_record.duration_minutes = duration_minutes

    db.commit()
    db.refresh(break_record)
    return break_record

def end_break(db: Session, break_id: int) -> Optional[Break]:
    return update_break(
        db=db,
        break_id=break_id,
        break_end=datetime.now(timezone.utc)
    )

def delete_break(db: Session, break_id: int) -> bool:
    break_record = get_break_by_id(db, break_id)
    if not break_record:
        return False
    db.delete(break_record)
    db.commit()
    return True
