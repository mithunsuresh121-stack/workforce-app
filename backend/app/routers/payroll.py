import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..db import get_db
from ..crud import (
    create_payroll_employee, get_payroll_employee_by_id, get_payroll_employee_by_employee_id,
    list_payroll_employees_by_tenant, update_payroll_employee, delete_payroll_employee,
    create_salary, get_salary_by_id, list_salaries_by_employee, update_salary, delete_salary,
    create_allowance, get_allowance_by_id, list_allowances_by_employee, update_allowance, delete_allowance,
    create_deduction, get_deduction_by_id, list_deductions_by_employee, update_deduction, delete_deduction,
    create_bonus, get_bonus_by_id, list_bonuses_by_employee, update_bonus, delete_bonus,
    create_payroll_run, get_payroll_run_by_id, list_payroll_runs_by_tenant, update_payroll_run, delete_payroll_run,
    create_payroll_entry, get_payroll_entry_by_id, list_payroll_entries_by_run, list_payroll_entries_by_employee,
    update_payroll_entry, delete_payroll_entry,
    get_user_by_id, get_company_by_id
)
from ..schemas import (
    EmployeeCreate, EmployeeOut, SalaryCreate, SalaryOut, AllowanceCreate, AllowanceOut,
    DeductionCreate, DeductionOut, BonusCreate, BonusOut, PayrollRunCreate, PayrollRunOut,
    PayrollEntryCreate, PayrollEntryOut
)
from ..deps import get_current_user

logger = structlog.get_logger(__name__)

router = APIRouter()

# Helper function to get tenant_id from user
def get_tenant_id(user_id: int, db: Session) -> str:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    company = get_company_by_id(db, user.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return str(company.id)

# Helper function to check role-based access
def check_role_access(current_user, required_roles: List[str]):
    if current_user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(required_roles)}"
        )

# Employee endpoints
@router.post("/employees/", response_model=EmployeeOut)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    # Check if employee_id already exists
    existing_employee = get_payroll_employee_by_employee_id(db, employee.employee_id, tenant_id)
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    return create_payroll_employee(
        db=db,
        tenant_id=tenant_id,
        user_id=employee.user_id,
        employee_id=employee.employee_id,
        department=employee.department,
        position=employee.position,
        hire_date=employee.hire_date,
        base_salary=employee.base_salary,
        status=employee.status
    )

@router.get("/employees/", response_model=List[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tenant_id = get_tenant_id(current_user.id, db)
    return list_payroll_employees_by_tenant(db, tenant_id)

@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return employee

@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int,
    employee_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_payroll_employee(
        db=db,
        employee_id=employee_id,
        department=employee_data.get('department'),
        position=employee_data.get('position'),
        hire_date=employee_data.get('hire_date'),
        base_salary=employee_data.get('base_salary'),
        status=employee_data.get('status')
    )

@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_payroll_employee(db, employee_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete employee")

    return {"message": "Employee deleted successfully"}

# Salary endpoints
@router.post("/salaries/", response_model=SalaryOut)
def create_employee_salary(
    salary: SalaryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, salary.employee_id)
    if not employee or employee.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    return create_salary(
        db=db,
        tenant_id=tenant_id,
        employee_id=salary.employee_id,
        amount=salary.amount,
        effective_date=salary.effective_date,
        end_date=salary.end_date
    )

@router.get("/salaries/employee/{employee_id}", response_model=List[SalaryOut])
def list_employee_salaries(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_salaries_by_employee(db, employee_id)

@router.put("/salaries/{salary_id}", response_model=SalaryOut)
def update_employee_salary(
    salary_id: int,
    salary_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    salary = get_salary_by_id(db, salary_id)
    if not salary:
        raise HTTPException(status_code=404, detail="Salary not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if salary.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_salary(
        db=db,
        salary_id=salary_id,
        amount=salary_data.get('amount'),
        effective_date=salary_data.get('effective_date'),
        end_date=salary_data.get('end_date')
    )

@router.delete("/salaries/{salary_id}")
def delete_employee_salary(
    salary_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    salary = get_salary_by_id(db, salary_id)
    if not salary:
        raise HTTPException(status_code=404, detail="Salary not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if salary.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_salary(db, salary_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete salary")

    return {"message": "Salary deleted successfully"}

# Allowance endpoints
@router.post("/allowances/", response_model=AllowanceOut)
def create_employee_allowance(
    allowance: AllowanceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, allowance.employee_id)
    if not employee or employee.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    return create_allowance(
        db=db,
        tenant_id=tenant_id,
        employee_id=allowance.employee_id,
        name=allowance.name,
        amount=allowance.amount,
        type=allowance.type,
        is_taxable=allowance.is_taxable,
        effective_date=allowance.effective_date,
        end_date=allowance.end_date
    )

@router.get("/allowances/employee/{employee_id}", response_model=List[AllowanceOut])
def list_employee_allowances(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_allowances_by_employee(db, employee_id)

@router.put("/allowances/{allowance_id}", response_model=AllowanceOut)
def update_employee_allowance(
    allowance_id: int,
    allowance_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        raise HTTPException(status_code=404, detail="Allowance not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if allowance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_allowance(
        db=db,
        allowance_id=allowance_id,
        name=allowance_data.get('name'),
        amount=allowance_data.get('amount'),
        type=allowance_data.get('type'),
        is_taxable=allowance_data.get('is_taxable'),
        effective_date=allowance_data.get('effective_date'),
        end_date=allowance_data.get('end_date')
    )

@router.delete("/allowances/{allowance_id}")
def delete_employee_allowance(
    allowance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    allowance = get_allowance_by_id(db, allowance_id)
    if not allowance:
        raise HTTPException(status_code=404, detail="Allowance not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if allowance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_allowance(db, allowance_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete allowance")

    return {"message": "Allowance deleted successfully"}

# Deduction endpoints
@router.post("/deductions/", response_model=DeductionOut)
def create_employee_deduction(
    deduction: DeductionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, deduction.employee_id)
    if not employee or employee.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    return create_deduction(
        db=db,
        tenant_id=tenant_id,
        employee_id=deduction.employee_id,
        name=deduction.name,
        amount=deduction.amount,
        type=deduction.type,
        is_mandatory=deduction.is_mandatory,
        effective_date=deduction.effective_date,
        end_date=deduction.end_date
    )

@router.get("/deductions/employee/{employee_id}", response_model=List[DeductionOut])
def list_employee_deductions(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_deductions_by_employee(db, employee_id)

@router.put("/deductions/{deduction_id}", response_model=DeductionOut)
def update_employee_deduction(
    deduction_id: int,
    deduction_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        raise HTTPException(status_code=404, detail="Deduction not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if deduction.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_deduction(
        db=db,
        deduction_id=deduction_id,
        name=deduction_data.get('name'),
        amount=deduction_data.get('amount'),
        type=deduction_data.get('type'),
        is_mandatory=deduction_data.get('is_mandatory'),
        effective_date=deduction_data.get('effective_date'),
        end_date=deduction_data.get('end_date')
    )

@router.delete("/deductions/{deduction_id}")
def delete_employee_deduction(
    deduction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    deduction = get_deduction_by_id(db, deduction_id)
    if not deduction:
        raise HTTPException(status_code=404, detail="Deduction not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if deduction.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_deduction(db, deduction_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete deduction")

    return {"message": "Deduction deleted successfully"}

# Bonus endpoints
@router.post("/bonuses/", response_model=BonusOut)
def create_employee_bonus(
    bonus: BonusCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, bonus.employee_id)
    if not employee or employee.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    return create_bonus(
        db=db,
        tenant_id=tenant_id,
        employee_id=bonus.employee_id,
        name=bonus.name,
        amount=bonus.amount,
        type=bonus.type,
        payment_date=bonus.payment_date,
        status=bonus.status
    )

@router.get("/bonuses/employee/{employee_id}", response_model=List[BonusOut])
def list_employee_bonuses(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_bonuses_by_employee(db, employee_id)

@router.put("/bonuses/{bonus_id}", response_model=BonusOut)
def update_employee_bonus(
    bonus_id: int,
    bonus_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if bonus.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_bonus(
        db=db,
        bonus_id=bonus_id,
        name=bonus_data.get('name'),
        amount=bonus_data.get('amount'),
        type=bonus_data.get('type'),
        payment_date=bonus_data.get('payment_date'),
        status=bonus_data.get('status')
    )

@router.delete("/bonuses/{bonus_id}")
def delete_employee_bonus(
    bonus_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    bonus = get_bonus_by_id(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if bonus.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_bonus(db, bonus_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete bonus")

    return {"message": "Bonus deleted successfully"}

# Payroll Run endpoints
@router.post("/payroll-runs/", response_model=PayrollRunOut)
def create_payroll_run_endpoint(
    payroll_run: PayrollRunCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])
    tenant_id = get_tenant_id(current_user.id, db)

    return create_payroll_run(
        db=db,
        tenant_id=tenant_id,
        period_start=payroll_run.period_start,
        period_end=payroll_run.period_end,
        status=payroll_run.status,
        processed_by=current_user.id
    )

@router.get("/payroll-runs/", response_model=List[PayrollRunOut])
def list_payroll_runs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    tenant_id = get_tenant_id(current_user.id, db)
    return list_payroll_runs_by_tenant(db, tenant_id)

@router.get("/payroll-runs/{payroll_run_id}", response_model=PayrollRunOut)
def get_payroll_run(
    payroll_run_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return payroll_run

@router.put("/payroll-runs/{payroll_run_id}", response_model=PayrollRunOut)
def update_payroll_run_endpoint(
    payroll_run_id: int,
    payroll_run_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_payroll_run(
        db=db,
        payroll_run_id=payroll_run_id,
        status=payroll_run_data.get('status'),
        total_gross=payroll_run_data.get('total_gross'),
        total_deductions=payroll_run_data.get('total_deductions'),
        total_net=payroll_run_data.get('total_net'),
        processed_by=current_user.id,
        processed_at=datetime.utcnow() if payroll_run_data.get('status') == 'Processed' else None
    )

@router.delete("/payroll-runs/{payroll_run_id}")
def delete_payroll_run_endpoint(
    payroll_run_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_payroll_run(db, payroll_run_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete payroll run")

    return {"message": "Payroll run deleted successfully"}

# Payroll Entry endpoints
@router.post("/payroll-entries/", response_model=PayrollEntryOut)
def create_payroll_entry_endpoint(
    payroll_entry: PayrollEntryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    # Verify payroll run belongs to tenant
    payroll_run = get_payroll_run_by_id(db, payroll_entry.payroll_run_id)
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, payroll_entry.employee_id)
    if not employee or employee.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    return create_payroll_entry(
        db=db,
        payroll_run_id=payroll_entry.payroll_run_id,
        employee_id=payroll_entry.employee_id,
        base_salary=payroll_entry.base_salary,
        total_allowances=payroll_entry.total_allowances,
        total_deductions=payroll_entry.total_deductions,
        total_bonuses=payroll_entry.total_bonuses,
        gross_pay=payroll_entry.gross_pay,
        net_pay=payroll_entry.net_pay,
        status=payroll_entry.status,
        notes=payroll_entry.notes
    )

@router.get("/payroll-entries/run/{payroll_run_id}", response_model=List[PayrollEntryOut])
def list_payroll_entries_by_run_endpoint(
    payroll_run_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify payroll run belongs to tenant
    payroll_run = get_payroll_run_by_id(db, payroll_run_id)
    if not payroll_run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_payroll_entries_by_run(db, payroll_run_id)

@router.get("/payroll-entries/employee/{employee_id}", response_model=List[PayrollEntryOut])
def list_payroll_entries_by_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Verify employee belongs to tenant
    employee = get_payroll_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    tenant_id = get_tenant_id(current_user.id, db)
    if employee.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return list_payroll_entries_by_employee(db, employee_id)

@router.put("/payroll-entries/{payroll_entry_id}", response_model=PayrollEntryOut)
def update_payroll_entry_endpoint(
    payroll_entry_id: int,
    payroll_entry_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin", "Manager"])

    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        raise HTTPException(status_code=404, detail="Payroll entry not found")

    # Verify payroll run belongs to tenant
    payroll_run = get_payroll_run_by_id(db, payroll_entry.payroll_run_id)
    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return update_payroll_entry(
        db=db,
        payroll_entry_id=payroll_entry_id,
        base_salary=payroll_entry_data.get('base_salary'),
        total_allowances=payroll_entry_data.get('total_allowances'),
        total_deductions=payroll_entry_data.get('total_deductions'),
        total_bonuses=payroll_entry_data.get('total_bonuses'),
        gross_pay=payroll_entry_data.get('gross_pay'),
        net_pay=payroll_entry_data.get('net_pay'),
        status=payroll_entry_data.get('status'),
        notes=payroll_entry_data.get('notes')
    )

@router.delete("/payroll-entries/{payroll_entry_id}")
def delete_payroll_entry_endpoint(
    payroll_entry_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    check_role_access(current_user, ["Admin"])

    payroll_entry = get_payroll_entry_by_id(db, payroll_entry_id)
    if not payroll_entry:
        raise HTTPException(status_code=404, detail="Payroll entry not found")

    # Verify payroll run belongs to tenant
    payroll_run = get_payroll_run_by_id(db, payroll_entry.payroll_run_id)
    tenant_id = get_tenant_id(current_user.id, db)
    if payroll_run.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = delete_payroll_entry(db, payroll_entry_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete payroll entry")

    return {"message": "Payroll entry deleted successfully"}
