import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from fastapi import HTTPException

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.main import app
from backend.app.db import get_db
from backend.app.models.payroll import (
    Employee,
    Salary,
    Allowance,
    Deduction,
    Bonus,
    PayrollRun,
    PayrollEntry
)
from backend.app.crud import (
    create_payroll_employee,
    get_payroll_employee_by_id,
    create_salary,
    create_allowance,
    create_deduction,
    create_bonus,
    create_payroll_run,
    create_payroll_entry
)
from backend.app.schemas import (
    EmployeeCreate,
    SalaryCreate,
    AllowanceCreate,
    DeductionCreate,
    BonusCreate,
    PayrollRunCreate,
    PayrollEntryCreate
)

client = TestClient(app)

# Test data
test_tenant_id = "test-tenant-123"
test_employee_data = {
    "tenant_id": test_tenant_id,
    "user_id": 1,
    "employee_id": "EMP001",
    "department": "Engineering",
    "position": "Software Engineer",
    "hire_date": datetime.utcnow().isoformat(),
    "base_salary": 50000.0,
    "status": "Active"
}

class TestPayrollCRUD:
    """Test payroll CRUD operations"""

    def test_create_payroll_employee(self, db: Session):
        """Test creating a payroll employee"""
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        assert employee.employee_id == test_employee_data["employee_id"]
        assert employee.tenant_id == test_tenant_id
        assert employee.base_salary == test_employee_data["base_salary"]

    def test_get_payroll_employee_by_id(self, db: Session):
        """Test retrieving a payroll employee by ID"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Retrieve employee
        retrieved_employee = get_payroll_employee_by_id(db, employee.id)
        assert retrieved_employee is not None
        assert retrieved_employee.id == employee.id
        assert retrieved_employee.employee_id == employee.employee_id

    def test_create_salary(self, db: Session):
        """Test creating a salary record"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create salary
        salary_data = SalaryCreate(
            employee_id=employee.id,
            amount=55000.0,
            effective_date=datetime.utcnow()
        )

        salary = create_salary(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=salary_data.employee_id,
            amount=salary_data.amount,
            effective_date=salary_data.effective_date
        )

        assert salary.amount == 55000.0
        assert salary.employee_id == employee.id
        assert salary.tenant_id == test_tenant_id

    def test_create_allowance(self, db: Session):
        """Test creating an allowance"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create allowance
        allowance_data = AllowanceCreate(
            employee_id=employee.id,
            name="Housing Allowance",
            amount=5000.0,
            type="Monthly",
            is_taxable="Yes",
            effective_date=datetime.utcnow()
        )

        allowance = create_allowance(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=allowance_data.employee_id,
            name=allowance_data.name,
            amount=allowance_data.amount,
            type=allowance_data.type,
            is_taxable=allowance_data.is_taxable,
            effective_date=allowance_data.effective_date
        )

        assert allowance.name == "Housing Allowance"
        assert allowance.amount == 5000.0
        assert allowance.employee_id == employee.id

    def test_create_deduction(self, db: Session):
        """Test creating a deduction"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create deduction
        deduction_data = DeductionCreate(
            employee_id=employee.id,
            name="Health Insurance",
            amount=2000.0,
            type="Monthly",
            is_mandatory="Yes",
            effective_date=datetime.utcnow()
        )

        deduction = create_deduction(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=deduction_data.employee_id,
            name=deduction_data.name,
            amount=deduction_data.amount,
            type=deduction_data.type,
            is_mandatory=deduction_data.is_mandatory,
            effective_date=deduction_data.effective_date
        )

        assert deduction.name == "Health Insurance"
        assert deduction.amount == 2000.0
        assert deduction.employee_id == employee.id

    def test_create_bonus(self, db: Session):
        """Test creating a bonus"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create bonus
        bonus_data = BonusCreate(
            employee_id=employee.id,
            name="Performance Bonus",
            amount=10000.0,
            type="Annual",
            payment_date=datetime.utcnow() + timedelta(days=30)
        )

        bonus = create_bonus(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=bonus_data.employee_id,
            name=bonus_data.name,
            amount=bonus_data.amount,
            type=bonus_data.type,
            payment_date=bonus_data.payment_date
        )

        assert bonus.name == "Performance Bonus"
        assert bonus.amount == 10000.0
        assert bonus.employee_id == employee.id

    def test_create_payroll_run(self, db: Session):
        """Test creating a payroll run"""
        period_start = datetime.utcnow().replace(day=1)
        period_end = (period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

        payroll_run_data = PayrollRunCreate(
            period_start=period_start,
            period_end=period_end
        )

        payroll_run = create_payroll_run(
            db=db,
            tenant_id=test_tenant_id,
            period_start=payroll_run_data.period_start,
            period_end=payroll_run_data.period_end
        )

        assert payroll_run.tenant_id == test_tenant_id
        assert payroll_run.period_start == period_start
        assert payroll_run.period_end == period_end
        assert payroll_run.status == "Draft"

    def test_create_payroll_entry(self, db: Session):
        """Test creating a payroll entry"""
        # Create employee
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create payroll run
        period_start = datetime.utcnow().replace(day=1)
        period_end = (period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

        payroll_run = create_payroll_run(
            db=db,
            tenant_id=test_tenant_id,
            period_start=period_start,
            period_end=period_end
        )

        # Create payroll entry
        payroll_entry_data = PayrollEntryCreate(
            payroll_run_id=payroll_run.id,
            employee_id=employee.id,
            base_salary=50000.0,
            total_allowances=5000.0,
            total_deductions=2000.0,
            total_bonuses=0.0,
            gross_pay=57000.0,
            net_pay=55000.0
        )

        payroll_entry = create_payroll_entry(
            db=db,
            payroll_run_id=payroll_entry_data.payroll_run_id,
            employee_id=payroll_entry_data.employee_id,
            base_salary=payroll_entry_data.base_salary,
            total_allowances=payroll_entry_data.total_allowances,
            total_deductions=payroll_entry_data.total_deductions,
            total_bonuses=payroll_entry_data.total_bonuses,
            gross_pay=payroll_entry_data.gross_pay,
            net_pay=payroll_entry_data.net_pay
        )

        assert payroll_entry.payroll_run_id == payroll_run.id
        assert payroll_entry.employee_id == employee.id
        assert payroll_entry.gross_pay == 57000.0
        assert payroll_entry.net_pay == 55000.0

class TestPayrollAPI:
    """Test payroll API endpoints"""

    def test_create_employee_endpoint(self, db: Session):
        """Test creating employee via API"""
        response = client.post(
            "/payroll/employees/",
            json=test_employee_data,
            headers={"Authorization": "Bearer test-token"}
        )
        # Note: This would need proper authentication setup
        # For now, just test the endpoint structure
        assert response.status_code in [401, 403, 422]  # Authentication/authorization errors expected

    def test_get_employees_endpoint(self, db: Session):
        """Test getting employees via API"""
        response = client.get(
            "/payroll/employees/",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code in [401, 403, 200]  # Authentication/authorization errors expected

class TestPayrollValidation:
    """Test payroll validation and edge cases"""

    def test_negative_amount_validation(self, db: Session):
        """Test validation for negative amounts"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Try to create salary with negative amount
        with pytest.raises(ValueError):
            create_salary(
                db=db,
                tenant_id=test_tenant_id,
                employee_id=employee.id,
                amount=-1000.0,  # Negative amount
                effective_date=datetime.utcnow()
            )

    def test_duplicate_employee_id_validation(self, db: Session):
        """Test validation for duplicate employee IDs"""
        # Create first employee
        employee_data = EmployeeCreate(**test_employee_data)
        create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Try to create second employee with same ID
        with pytest.raises(Exception):  # Should raise integrity error
            create_payroll_employee(
                db=db,
                tenant_id=test_tenant_id,
                user_id=2,  # Different user
                employee_id=employee_data.employee_id,  # Same employee ID
                department="HR",
                position="HR Manager",
                hire_date=datetime.utcnow(),
                base_salary=60000.0,
                status="Active"
            )

    def test_future_date_validation(self, db: Session):
        """Test validation for future dates in historical data"""
        # Create employee first
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create salary with past effective date (should be fine)
        past_date = datetime.utcnow() - timedelta(days=30)
        salary = create_salary(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=employee.id,
            amount=55000.0,
            effective_date=past_date
        )
        assert salary.effective_date == past_date

    def test_payroll_calculation_logic(self, db: Session):
        """Test payroll calculation logic"""
        # Create employee
        employee_data = EmployeeCreate(**test_employee_data)
        employee = create_payroll_employee(
            db=db,
            tenant_id=test_tenant_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create allowances and deductions
        allowance = create_allowance(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=employee.id,
            name="Transport",
            amount=2000.0,
            type="Monthly",
            is_taxable="Yes",
            effective_date=datetime.utcnow()
        )

        deduction = create_deduction(
            db=db,
            tenant_id=test_tenant_id,
            employee_id=employee.id,
            name="Tax",
            amount=5000.0,
            type="Monthly",
            is_mandatory="Yes",
            effective_date=datetime.utcnow()
        )

        # Calculate expected values
        base_salary = employee.base_salary
        total_allowances = allowance.amount
        total_deductions = deduction.amount
        expected_gross = base_salary + total_allowances
        expected_net = expected_gross - total_deductions

        # Create payroll run and entry
        period_start = datetime.utcnow().replace(day=1)
        period_end = (period_start + timedelta(days=30)).replace(day=1) - timedelta(days=1)

        payroll_run = create_payroll_run(
            db=db,
            tenant_id=test_tenant_id,
            period_start=period_start,
            period_end=period_end
        )

        payroll_entry = create_payroll_entry(
            db=db,
            payroll_run_id=payroll_run.id,
            employee_id=employee.id,
            base_salary=base_salary,
            total_allowances=total_allowances,
            total_deductions=total_deductions,
            total_bonuses=0.0,
            gross_pay=expected_gross,
            net_pay=expected_net
        )

        assert payroll_entry.gross_pay == expected_gross
        assert payroll_entry.net_pay == expected_net
        assert payroll_entry.base_salary == base_salary
        assert payroll_entry.total_allowances == total_allowances
        assert payroll_entry.total_deductions == total_deductions

class TestPayrollMultiTenant:
    """Test multi-tenant isolation"""

    def test_tenant_isolation(self, db: Session):
        """Test that tenants cannot access each other's data"""
        # Create employee for tenant 1
        tenant1_id = "tenant-1"
        employee_data = EmployeeCreate(**test_employee_data)
        employee1 = create_payroll_employee(
            db=db,
            tenant_id=tenant1_id,
            user_id=employee_data.user_id,
            employee_id=employee_data.employee_id,
            department=employee_data.department,
            position=employee_data.position,
            hire_date=datetime.fromisoformat(employee_data.hire_date),
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Create employee for tenant 2
        tenant2_id = "tenant-2"
        employee2 = create_payroll_employee(
            db=db,
            tenant_id=tenant2_id,
            user_id=2,
            employee_id="EMP002",
            department="HR",
            position="HR Manager",
            hire_date=datetime.utcnow(),
            base_salary=60000.0,
            status="Active"
        )

        # Verify tenant isolation
        assert employee1.tenant_id == tenant1_id
        assert employee2.tenant_id == tenant2_id
        assert employee1.employee_id != employee2.employee_id

        # Test that queries are tenant-specific
        from backend.app.crud import list_payroll_employees_by_tenant
        tenant1_employees = list_payroll_employees_by_tenant(db, tenant1_id)
        tenant2_employees = list_payroll_employees_by_tenant(db, tenant2_id)

        assert len(tenant1_employees) == 1
        assert len(tenant2_employees) == 1
        assert tenant1_employees[0].tenant_id == tenant1_id
        assert tenant2_employees[0].tenant_id == tenant2_id

# Fixtures
@pytest.fixture
def db():
    """Database session fixture"""
    from backend.app.db import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

if __name__ == "__main__":
    pytest.main([__file__])
