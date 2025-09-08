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
            hire_date=employee_data.hire_date,
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
            hire_date=employee_data.hire_date,
            base_salary=employee_data.base_salary,
            status=employee_data.status
        )

        # Retrieve employee
        retrieved_employee = get_payroll_employee_by_id(db, employee.id)
        assert retrieved_employee is not None
        assert retrieved_employee.id == employee.id
        assert retrieved_employee.employee_id == employee.employee_id

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
