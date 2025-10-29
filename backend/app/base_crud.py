import json
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from .models.user import User
from .models.company import Company
from .models.employee_profile import EmployeeProfile
from .models.profile_update_request import ProfileUpdateRequest, RequestStatus
from .models.task import Task
from .models.leave import Leave
from .models.shift import Shift
from .models.refresh_token import RefreshToken
from .schemas import EmployeeProfileUpdate
from passlib.context import CryptContext
import structlog

logger = structlog.get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str, company_id: Optional[int] = None) -> Optional[User]:
    query = db.query(User).filter(User.email == email)
    if company_id is not None:
        query = query.filter(User.company_id == company_id)
    return query.first()

def get_user_by_email_only(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_company_by_id(db: Session, company_id: int) -> Optional[Company]:
    return db.query(Company).filter(Company.id == company_id).first()

def list_users_by_company(db: Session, company_id: int):
    return db.query(User).filter(User.company_id == company_id).all()

def get_users_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).all()

def create_user(db: Session, email: str, password: str, full_name: str, role: str, company_id: Optional[int] = None):
    hashed_password = pwd_context.hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user

def authenticate_user_by_email(db: Session, email: str, password: str) -> Optional[User]:
    return authenticate_user(db, email, password)

def update_user(db: Session, user_id: int, email: Optional[str] = None, password: Optional[str] = None, full_name: Optional[str] = None, role: Optional[str] = None, company_id: Optional[int] = None):
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    if email is not None:
        user.email = email
    if password is not None:
        user.hashed_password = pwd_context.hash(password)
    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if company_id is not None:
        user.company_id = company_id
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def create_employee_profile(db: Session, user_id: int, company_id: int, department: str = None, position: str = None, phone: str = None, hire_date = None, manager_id: int = None, address: str = None, city: str = None, emergency_contact: str = None, employee_id: str = None, profile_picture_url: str = None):
    profile = EmployeeProfile(
        user_id=user_id,
        company_id=company_id,
        department=department,
        position=position,
        phone=phone,
        hire_date=hire_date,
        manager_id=manager_id,
        # gender removed as per request
        # gender=gender,
        address=address,
        city=city,
        emergency_contact=emergency_contact,
        employee_id=employee_id,
        profile_picture_url=profile_picture_url
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def list_employee_profiles_by_company(db: Session, company_id: int):
    return db.query(EmployeeProfile).filter(EmployeeProfile.company_id == company_id).all()

def get_employee_profile_by_user_id(db: Session, user_id: int, company_id: int):
    return db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id, EmployeeProfile.company_id == company_id).first()

def update_employee_profile(db: Session, user_id: int, company_id: int, **kwargs):
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id, EmployeeProfile.company_id == company_id).first()
    if not profile:
        return None
    # Remove gender from kwargs if present
    if 'gender' in kwargs:
        kwargs.pop('gender')
    for key, value in kwargs.items():
        if hasattr(profile, key) and value is not None:
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile

def delete_employee_profile(db: Session, user_id: int, company_id: int):
    profile = db.query(EmployeeProfile).filter(EmployeeProfile.user_id == user_id, EmployeeProfile.company_id == company_id).first()
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    return True

def create_profile_update_request(db: Session, user_id: int, requested_by_id: int, request_type: str, payload: dict = None):
    payload_json = json.dumps(payload) if payload else None
    request = ProfileUpdateRequest(
        user_id=user_id,
        requested_by_id=requested_by_id,
        request_type=request_type,
        payload=payload_json,
        status=RequestStatus.PENDING.value
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def get_profile_update_request_by_id(db: Session, request_id: int):
    return db.query(ProfileUpdateRequest).filter(ProfileUpdateRequest.id == request_id).first()

def list_profile_update_requests(db: Session):
    return db.query(ProfileUpdateRequest).all()

def list_profile_update_requests_by_user(db: Session, user_id: int):
    return db.query(ProfileUpdateRequest).filter(ProfileUpdateRequest.user_id == user_id).all()

def update_profile_update_request_status(db: Session, request_id: int, status: str, reviewed_by_id: int, review_comment: str = None):
    request = get_profile_update_request_by_id(db, request_id)
    if not request:
        return None
    request.status = status
    request.reviewed_by_id = reviewed_by_id
    request.review_comment = review_comment
    request.reviewed_at = func.now()
    db.commit()
    db.refresh(request)
    return request

def delete_profile_update_request(db: Session, request_id: int):
    request = get_profile_update_request_by_id(db, request_id)
    if not request:
        return False
    db.delete(request)
    db.commit()
    return True

# Task CRUD functions
def list_tasks(db: Session, company_id: int):
    return db.query(Task).filter(Task.company_id == company_id).all()

def create_task(db: Session, company_id: int, title: str, description: str = None, assignee_id: int = None, assigned_by: int = None, status: str = "Pending", priority: str = "Medium", due_at = None):
    task = Task(
        company_id=company_id,
        title=title,
        description=description,
        assignee_id=assignee_id,
        assigned_by=assigned_by,
        status=status,
        priority=priority,
        due_at=due_at
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

def update_task(db: Session, task_id: int, **kwargs):
    task = get_task_by_id(db, task_id)
    if not task:
        return None
    for key, value in kwargs.items():
        if hasattr(task, key) and value is not None:
            setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = get_task_by_id(db, task_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True

# Attachment CRUD functions
from .models.attachment import Attachment

def create_attachment(db: Session, task_id: int, file_path: str, file_type: str, file_size: float, uploaded_by: int):
    attachment = Attachment(
        task_id=task_id,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        uploaded_by=uploaded_by
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def get_attachment_by_id(db: Session, attachment_id: int):
    return db.query(Attachment).filter(Attachment.id == attachment_id).first()

def list_attachments_by_task(db: Session, task_id: int):
    return db.query(Attachment).filter(Attachment.task_id == task_id).all()

def delete_attachment(db: Session, attachment_id: int):
    attachment = get_attachment_by_id(db, attachment_id)
    if not attachment:
        return False
    db.delete(attachment)
    db.commit()
    return True

# Company CRUD functions
def create_company(db: Session, name: str, domain: str = None, contact_email: str = None, contact_phone: str = None, address: str = None, city: str = None, state: str = None, country: str = None, postal_code: str = None):
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

def list_companies(db: Session):
    return db.query(Company).all()

def get_company_by_name(db: Session, name: str):
    return db.query(Company).filter(Company.name == name).first()

def delete_company(db: Session, company_id: int):
    company = get_company_by_id(db, company_id)
    if not company:
        return False
    db.delete(company)
    db.commit()
    return True

# Refresh Token CRUD functions
def create_refresh_token(db: Session, user_id: int, token: str, expires_at):
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    logger.info("Refresh token created", user_id=user_id)
    return refresh_token

def get_refresh_token_by_token(db: Session, token: str) -> Optional[RefreshToken]:
    return db.query(RefreshToken).filter(RefreshToken.token == token, RefreshToken.revoked == False).first()

def revoke_refresh_token(db: Session, token: str):
    refresh_token = get_refresh_token_by_token(db, token)
    if refresh_token:
        refresh_token.revoked = True
        db.commit()
        logger.info("Refresh token revoked", user_id=refresh_token.user_id)
        return True
    return False

def revoke_all_user_refresh_tokens(db: Session, user_id: int):
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False).update({"revoked": True})
    db.commit()
    logger.info("All refresh tokens revoked for user", user_id=user_id)

# Leave CRUD functions
def create_leave(db: Session, tenant_id: str, employee_id: int, type: str, start_at, end_at, status: str = "Pending"):
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

def get_leave_by_id(db: Session, leave_id: int):
    return db.query(Leave).filter(Leave.id == leave_id).first()

def list_leaves_by_employee(db: Session, employee_id: int):
    return db.query(Leave).filter(Leave.employee_id == employee_id).all()

def update_leave_status(db: Session, leave_id: int, status: str):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        return None
    leave.status = status
    db.commit()
    db.refresh(leave)
    return leave

def delete_leave(db: Session, leave_id: int):
    leave = db.query(Leave).filter(Leave.id == leave_id).first()
    if not leave:
        return False
    db.delete(leave)
    db.commit()
    return True

def list_leaves_by_tenant(db: Session, tenant_id: str):
    return db.query(Leave).filter(Leave.tenant_id == tenant_id).all()

# Shift CRUD functions
def create_shift(db: Session, company_id: int, employee_id: int, start_at, end_at, location: str = None):
    shift = Shift(
        company_id=company_id,
        employee_id=employee_id,
        start_at=start_at,
        end_at=end_at,
        location=location
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

def get_shift_by_id(db: Session, shift_id: int):
    return db.query(Shift).filter(Shift.id == shift_id).first()

def list_shifts_by_employee(db: Session, employee_id: int):
    return db.query(Shift).filter(Shift.employee_id == employee_id).all()

def update_shift(db: Session, shift_id: int, **kwargs):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        return None
    for key, value in kwargs.items():
        if hasattr(shift, key) and value is not None:
            setattr(shift, key, value)
    db.commit()
    db.refresh(shift)
    return shift

def delete_shift(db: Session, shift_id: int):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        return False
    db.delete(shift)
    db.commit()
    return True

def list_shifts_by_company(db: Session, company_id: int):
    return db.query(Shift).filter(Shift.company_id == company_id).all()
from .models.payroll import Employee as PayrollEmployee, Salary, Allowance, Deduction, Bonus, PayrollRun, PayrollEntry
from .models.attendance import Attendance, Break

# Payroll CRUD functions
def create_payroll_employee(db: Session, tenant_id: str, user_id: int, employee_id: str, department: str = None, position: str = None, hire_date = None, base_salary: float = 0.0, status: str = "Active"):
    employee = PayrollEmployee(
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

def get_payroll_employee_by_id(db: Session, employee_id: int):
    return db.query(PayrollEmployee).filter(PayrollEmployee.id == employee_id).first()

def get_payroll_employee_by_employee_id(db: Session, employee_id: str, tenant_id: str):
    return db.query(PayrollEmployee).filter(PayrollEmployee.employee_id == employee_id, PayrollEmployee.tenant_id == tenant_id).first()

def list_payroll_employees_by_tenant(db: Session, tenant_id: str):
    return db.query(PayrollEmployee).filter(PayrollEmployee.tenant_id == tenant_id).all()

def update_payroll_employee(db: Session, employee_id: int, **kwargs):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        return None
    for key, value in kwargs.items():
        if hasattr(employee, key) and value is not None:
            setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee

def delete_payroll_employee(db: Session, employee_id: int):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        return False
    db.delete(employee)
    db.commit()
    return True

def create_salary(db: Session, tenant_id: str, employee_id: int, amount: float, effective_date, end_date = None):
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

def get_salary_by_id(db: Session, salary_id: int):
    return db.query(Salary).filter(Salary.id == salary_id).first()

def list_salaries_by_employee(db: Session, employee_id: int):
    return db.query(Salary).filter(Salary.employee_id == employee_id).all()

def update_salary(db: Session, salary_id: int, **kwargs):
    salary = get_salary_by_id(db, salary_id)
    if not salary:
        return None
    for key, value in kwargs.items():
        if hasattr(salary, key) and value is not None:
            setattr(salary, key, value)
    db.commit()
    db.refresh(salary)
    return salary

def delete_salary(db: Session, salary_id: int):
    salary = get_salary_by_id(db, salary_id)
    if not salary:
        return False
    db.delete(salary)
    db.commit()
    return True

def create_allowance(db: Session, tenant_id: str, employee_id: int, name: str, amount: float, type: str, is_taxable: str = "Yes", effective_date = None, end_date = None):
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

def get_allowance_by_id(db: Session, allowance_id: int):
    return db.query(Allowance).filter(Allowance.id == allowance_id).first()

def list_allowances_by_employee(db: Session, employee_id: int):
    return db.query(Allowance).filter(Allowance.employee_id == employee_id).all()

def update_allowance(db: Session, allowance_id: int, **kwargs):
    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        return None
    for key, value in kwargs.items():
        if hasattr(allowance, key) and value is not None:
            setattr(allowance, key, value)
    db.commit()
    db.refresh(allowance)
    return allowance

def delete_allowance(db: Session, allowance_id: int):
    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        return False
    db.delete(allowance)
    db.commit()
    return True

def create_deduction(db: Session, tenant_id: str, employee_id: int, name: str, amount: float, type: str, is_mandatory: str = "Yes", effective_date = None, end_date = None):
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

def get_deduction_by_id(db: Session, deduction_id: int):
    return db.query(Deduction).filter(Deduction.id == deduction_id).first()

def list_deductions_by_employee(db: Session, employee_id: int):
    return db.query(Deduction).filter(Deduction.employee_id == employee_id).all()

def update_deduction(db: Session, deduction_id: int, **kwargs):
    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        return None
    for key, value in kwargs.items():
        if hasattr(deduction, key) and value is not None:
            setattr(deduction, key, value)
    db.commit()
    db.refresh(deduction)
    return deduction

def delete_deduction(db: Session, deduction_id: int):
    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        return False
    db.delete(deduction)
    db.commit()
    return True

def create_bonus(db: Session, tenant_id: str, employee_id: int, name: str, amount: float, type: str, payment_date, status: str = "Pending"):
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

def get_bonus_by_id(db: Session, bonus_id: int):
    return db.query(Bonus).filter(Bonus.id == bonus_id).first()

def list_bonuses_by_employee(db: Session, employee_id: int):
    return db.query(Bonus).filter(Bonus.employee_id == employee_id).all()

def update_bonus(db: Session, bonus_id: int, **kwargs):
    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        return None
    for key, value in kwargs.items():
        if hasattr(bonus, key) and value is not None:
            setattr(bonus, key, value)
    db.commit()
    db.refresh(bonus)
    return bonus

def delete_bonus(db: Session, bonus_id: int):
    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        return False
    db.delete(bonus)
    db.commit()
    return True

def create_payroll_run(db: Session, tenant_id: str, period_start, period_end, status: str = "Draft", processed_by: int = None):
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

def get_payroll_run_by_id(db: Session, payroll_run_id: int):
    return db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()

def list_payroll_runs_by_tenant(db: Session, tenant_id: str):
    return db.query(PayrollRun).filter(PayrollRun.tenant_id == tenant_id).all()

def update_payroll_run(db: Session, payroll_run_id: int, **kwargs):
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        return None
    for key, value in kwargs.items():
        if hasattr(payroll_run, key) and value is not None:
            setattr(payroll_run, key, value)
    db.commit()
    db.refresh(payroll_run)
    return payroll_run

def delete_payroll_run(db: Session, payroll_run_id: int):
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        return False
    db.delete(payroll_run)
    db.commit()
    return True

def create_payroll_entry(db: Session, payroll_run_id: int, employee_id: int, base_salary: float = 0.0, total_allowances: float = 0.0, total_deductions: float = 0.0, total_bonuses: float = 0.0, gross_pay: float = 0.0, net_pay: float = 0.0, status: str = "Pending", notes: str = None):
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

def get_payroll_entry_by_id(db: Session, payroll_entry_id: int):
    return db.query(PayrollEntry).filter(PayrollEntry.id == payroll_entry_id).first()

def list_payroll_entries_by_run(db: Session, payroll_run_id: int):
    return db.query(PayrollEntry).filter(PayrollEntry.payroll_run_id == payroll_run_id).all()

def list_payroll_entries_by_employee(db: Session, employee_id: int):
    return db.query(PayrollEntry).filter(PayrollEntry.employee_id == employee_id).all()

def update_payroll_entry(db: Session, payroll_entry_id: int, **kwargs):
    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        return None
    for key, value in kwargs.items():
        if hasattr(payroll_entry, key) and value is not None:
            setattr(payroll_entry, key, value)
    db.commit()
    db.refresh(payroll_entry)
    return payroll_entry

def delete_payroll_entry(db: Session, payroll_entry_id: int):
    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        return False
    db.delete(payroll_entry)
    db.commit()
    return True

# Attendance CRUD functions
def create_attendance(db: Session, company_id: int, employee_id: int, clock_in_time, notes: str = None):
    attendance = Attendance(
        company_id=company_id,
        employee_id=employee_id,
        clock_in_time=clock_in_time,
        notes=notes
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance

def get_attendance_by_id(db: Session, attendance_id: int):
    return db.query(Attendance).filter(Attendance.id == attendance_id).first()

def get_active_attendance_by_employee(db: Session, employee_id: int):
    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.clock_out_time.is_(None)
    ).first()

def list_attendance_by_employee(db: Session, employee_id: int, limit: int = 50):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.created_at.desc()).limit(limit).all()

def get_attendance_records(db: Session, user_id: int, company_id: int, start_date=None, end_date=None):
    query = db.query(Attendance).filter(
        Attendance.employee_id == user_id,
        Attendance.company_id == company_id
    )

    if start_date:
        query = query.filter(Attendance.clock_in_time >= start_date)
    if end_date:
        query = query.filter(Attendance.clock_in_time <= end_date)

    return query.order_by(Attendance.clock_in_time.desc()).all()

def clock_out_attendance(db: Session, attendance_id: int, notes: str = None):
    attendance = get_attendance_by_id(db, attendance_id)
    if not attendance:
        return None
    from datetime import datetime, timezone
    attendance.clock_out_time = datetime.now(timezone.utc)
    if notes:
        attendance.notes = notes
    attendance.status = "completed"
    # Calculate total hours
    if attendance.clock_in_time and attendance.clock_out_time:
        duration = attendance.clock_out_time - attendance.clock_in_time
        attendance.total_hours = duration.total_seconds() / 3600
    db.commit()
    db.refresh(attendance)
    return attendance

def create_break(db: Session, attendance_id: int, break_start, break_type: str = "lunch"):
    break_record = Break(
        attendance_id=attendance_id,
        break_start=break_start,
        break_type=break_type
    )
    db.add(break_record)
    db.commit()
    db.refresh(break_record)
    return break_record

def get_break_by_id(db: Session, break_id: int):
    return db.query(Break).filter(Break.id == break_id).first()

def list_breaks_by_attendance(db: Session, attendance_id: int):
    return db.query(Break).filter(Break.attendance_id == attendance_id).all()

def end_break(db: Session, break_id: int):
    break_record = get_break_by_id(db, break_id)
    if not break_record:
        return None
    from datetime import datetime, timezone
    break_record.break_end = datetime.now(timezone.utc)
    if break_record.break_start and break_record.break_end:
        duration = break_record.break_end - break_record.break_start
        break_record.duration_minutes = int(duration.total_seconds() / 60)
    db.commit()
    db.refresh(break_record)
    return break_record

# Reports CRUD functions
from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy import func, extract, and_, or_, distinct

def get_attendance_heatmap(db: Session, company_id: int, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Get attendance heatmap data: daily present/absent counts with intensity.
    """
    total_employees = db.query(func.count(User.id)).filter(User.company_id == company_id).scalar()

    # Daily attendance counts
    daily_data = db.query(
        func.date(Attendance.clock_in_time).label('date'),
        func.count(distinct(Attendance.employee_id)).label('present')
    ).filter(
        Attendance.company_id == company_id,
        Attendance.clock_in_time >= start_date,
        Attendance.clock_in_time <= end_date,
        Attendance.status == "active"
    ).group_by(func.date(Attendance.clock_in_time)).all()

    # Convert to dict for easy lookup
    data_dict = {row.date: row.present for row in daily_data}
    result = []

    current_date = start_date
    while current_date <= end_date:
        present = data_dict.get(current_date, 0)
        absent = total_employees - present
        intensity = int((present / total_employees) * 100) if total_employees > 0 else 0
        result.append({
            "date": current_date.isoformat(),
            "present": present,
            "absent": absent,
            "heatmap_intensity": intensity
        })
        current_date += timedelta(days=1)

    return result

def get_payroll_by_dept(db: Session, company_id: int, period: str) -> List[Dict[str, Any]]:
    """
    Get payroll projections by department.
    """
    from .models.payroll import Employee as PayrollEmployee

    # Assume 22 working days per month
    working_days = 22

    # Get current month for attendance factor
    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Aggregate by department
    dept_data = db.query(
        EmployeeProfile.department.label('dept'),
        func.count(distinct(PayrollEmployee.id)).label('employees'),
        func.avg(PayrollEmployee.base_salary).label('avg_salary')
    ).outerjoin(
        PayrollEmployee, PayrollEmployee.user_id == EmployeeProfile.user_id
    ).filter(
        EmployeeProfile.company_id == company_id,
        PayrollEmployee.tenant_id == str(company_id)
    ).group_by(EmployeeProfile.department).all()

    result = []
    for row in dept_data:
        dept = row.dept or "Unknown"
        employees = row.employees or 0
        avg_salary = row.avg_salary or 0

        # Calculate attendance factor (simplified: assume 80% attendance)
        attendance_factor = 0.8
        projected_cost = avg_salary * employees * attendance_factor

        # Forecast next month (assume 5% increase)
        forecast_next = projected_cost * 1.05

        result.append({
            "dept": dept,
            "projected_cost": round(projected_cost, 2),
            "employees": employees,
            "forecast_next_month": round(forecast_next, 2)
        })

    return result

def get_overtime_trend(db: Session, company_id: int, period: str, dept_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get overtime trends over time by department.
    """
    from datetime import datetime
    now = datetime.now()

    if period == "weekly":
        # Last 12 weeks
        start_date = now - timedelta(weeks=12)
        group_expr = extract('week', Attendance.clock_in_time)
        label_expr = func.concat(extract('year', Attendance.clock_in_time), '-', func.lpad(extract('week', Attendance.clock_in_time), 2, '0'))
    else:
        # Last 12 months
        start_date = now - timedelta(days=365)
        group_expr = extract('month', Attendance.clock_in_time)
        label_expr = func.concat(extract('year', Attendance.clock_in_time), '-', func.lpad(extract('month', Attendance.clock_in_time), 2, '0'))

    query = db.query(
        label_expr.label('period'),
        EmployeeProfile.department.label('dept'),
        func.sum(Attendance.overtime_hours).label('hours')
    ).outerjoin(
        EmployeeProfile, EmployeeProfile.user_id == Attendance.employee_id
    ).filter(
        Attendance.company_id == company_id,
        Attendance.clock_in_time >= start_date,
        Attendance.overtime_hours > 0
    ).group_by(label_expr, EmployeeProfile.department)

    if dept_filter:
        query = query.filter(EmployeeProfile.department == dept_filter)

    overtime_data = query.all()

    result = []
    for row in overtime_data:
        result.append({
            "period": row.period,
            "dept": row.dept or "Unknown",
            "hours": row.hours or 0.0
        })

    return result
