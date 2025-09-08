#!/usr/bin/env python3
"""
Script to create a test employee for payroll testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from app.models.company import Company
from app.auth import hash_password

def create_test_employee():
    db = SessionLocal()
    try:
        # Check if test employee already exists
        existing_employee = db.query(User).filter(User.email == "employee@example.com").first()
        if existing_employee:
            print(f"Test employee already exists: {existing_employee.email} with ID: {existing_employee.id}")
            return

        # Check if test company exists, create if not
        test_company = db.query(Company).filter(Company.name == "Test Company").first()
        if not test_company:
            test_company = Company(
                name="Test Company",
                domain="testcompany.com",
                contact_email="admin@testcompany.com",
                contact_phone="123-456-7890",
                address="123 Test St",
                city="Test City",
                state="Test State",
                country="Test Country",
                postal_code="12345",
                is_active=True
            )
            db.add(test_company)
            db.commit()
            db.refresh(test_company)
            print(f"Created test company: {test_company.name} with ID: {test_company.id}")
        else:
            print(f"Test company already exists: {test_company.name} with ID: {test_company.id}")

        # Create test employee user
        hashed_password = hash_password("password123")
        test_employee = User(
            email="employee@example.com",
            full_name="John Doe",
            hashed_password=hashed_password,
            role="Employee",
            company_id=test_company.id,
            is_active=True
        )

        db.add(test_employee)
        db.commit()
        db.refresh(test_employee)

        # Create employee profile
        from datetime import datetime
        employee_profile = EmployeeProfile(
            user_id=test_employee.id,
            company_id=test_company.id,
            department="Engineering",
            position="Software Engineer",
            hire_date=datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
            phone="555-123-4567",
            is_active=True
        )

        db.add(employee_profile)
        db.commit()

        print(f"Created test employee: {test_employee.email} with ID: {test_employee.id}")
        print(f"Employee Profile ID: {employee_profile.id}")

    except Exception as e:
        print(f"Error creating test employee: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_employee()
