from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    employee_id = Column(String, nullable=False, unique=True)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    hire_date = Column(DateTime, nullable=True)
    base_salary = Column(Float, nullable=False)
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Salary(Base):
    __tablename__ = "salaries"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    amount = Column(Float, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employee")

class Allowance(Base):
    __tablename__ = "allowances"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # e.g., "Housing", "Transport", "Meal"
    is_taxable = Column(String, default="Yes")
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employee")

class Deduction(Base):
    __tablename__ = "deductions"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # e.g., "Tax", "Insurance", "Loan"
    is_mandatory = Column(String, default="Yes")
    effective_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employee")

class Bonus(Base):
    __tablename__ = "bonuses"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # e.g., "Performance", "Annual", "Spot"
    payment_date = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    employee = relationship("Employee")

class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String, default="Draft")
    total_gross = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    total_net = Column(Float, default=0.0)
    processed_by = Column(Integer, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class PayrollEntry(Base):
    __tablename__ = "payroll_entries"
    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    base_salary = Column(Float, default=0.0)
    total_allowances = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    total_bonuses = Column(Float, default=0.0)
    gross_pay = Column(Float, default=0.0)
    net_pay = Column(Float, default=0.0)
    status = Column(String, default="Pending")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    payroll_run = relationship("PayrollRun")
    employee = relationship("Employee")
