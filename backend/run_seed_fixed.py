#!/usr/bin/env python3
"""
Script to run the seed demo user function with proper database permissions.
This script connects directly to the database to create employee profiles.
"""

import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

# Import with absolute paths
from crud import (create_company, create_employee_profile, create_user,
                  get_company_by_id, get_company_by_name)
from models.company import Company
from models.employee_profile import EmployeeProfile
from models.user import User

# Create a direct database connection with superuser privileges
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_demo_user(db):
    print("Starting seed process...")

    # Create Super Admin user
    super_admin_email = "admin@app.com"
    super_admin_password = "supersecure123"

    # Check if Super Admin already exists
    existing_super_admin = db.query(User).filter_by(email=super_admin_email).first()
    if existing_super_admin:
        print("Super Admin user already exists.")
    else:
        # Create Super Admin user (no company_id needed)
        create_user(
            db,
            super_admin_email,
            super_admin_password,
            full_name="Super Administrator",
            role="SuperAdmin",
            company_id=None,
        )
        print("Super Admin user created successfully.")

    # Create demo company and user (optional, for backward compatibility)
    demo_company_name = "Demo Company"
    company = get_company_by_name(db, demo_company_name)
    if not company:
        print("Creating demo company...")
        company = create_company(
            db,
            name=demo_company_name,
            domain="demo.com",
            contact_email="demo@company.com",
            contact_phone="+1234567890",
            address="123 Demo Street",
            city="Demo City",
            state="Demo State",
            country="Demo Country",
            postal_code="12345",
        )
        print("Demo company created successfully.")

    demo_email = "demo@company.com"
    demo_password = "password123"
    existing_user = (
        db.query(User).filter_by(email=demo_email, company_id=company.id).first()
    )
    if existing_user:
        print("Demo user already exists.")
        # Fix role if invalid
        if existing_user.role not in [
            "SuperAdmin",
            "CompanyAdmin",
            "Manager",
            "Employee",
        ]:
            existing_user.role = "Employee"
            db.commit()
            print("Fixed demo user role to Employee.")
    else:
        create_user(
            db,
            demo_email,
            demo_password,
            full_name="Demo User",
            role="Employee",
            company_id=company.id,
        )
        print("Demo user created successfully.")

    # Create employee profiles for demo users
    print("Creating employee profiles for demo users...")

    # Create profile for Super Admin
    super_admin = db.query(User).filter_by(email=super_admin_email).first()
    if super_admin:
        # Check if profile already exists
        existing_profile = (
            db.query(EmployeeProfile).filter_by(user_id=super_admin.id).first()
        )
        if not existing_profile:
            create_employee_profile(
                db=db,
                user_id=super_admin.id,
                company_id=company.id if company else None,
                department="IT",
                position="System Administrator",
                phone="+1234567890",
                hire_date="2023-01-01",
                manager_id=None,
            )
            print("Created employee profile for Super Admin")

    # Create profile for demo user
    demo_user = (
        db.query(User).filter_by(email=demo_email, company_id=company.id).first()
    )
    if demo_user:
        # Check if profile already exists
        existing_profile = (
            db.query(EmployeeProfile).filter_by(user_id=demo_user.id).first()
        )
        if not existing_profile:
            create_employee_profile(
                db=db,
                user_id=demo_user.id,
                company_id=company.id,
                department="Engineering",
                position="Software Engineer",
                phone="+1234567891",
                hire_date="2023-06-01",
                manager_id=None,
            )
            print("Created employee profile for Demo User")

    print("Seed process completed successfully!")


if __name__ == "__main__":
    db = next(get_db())
    seed_demo_user(db)
