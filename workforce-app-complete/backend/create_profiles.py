#!/usr/bin/env python3
"""
Simple script to create employee profiles for existing demo users.
This script connects directly to the database and creates the missing profiles.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import models directly
from models.user import User
from models.company import Company
from models.employee_profile import EmployeeProfile

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

def create_employee_profile(db, user_id, company_id, department=None, position=None, phone=None, hire_date=None, manager_id=None):
    """Create an employee profile for a user"""
    profile = EmployeeProfile(
        user_id=user_id,
        company_id=company_id,
        department=department,
        position=position,
        phone=phone,
        hire_date=hire_date,
        manager_id=manager_id,
        is_active=True
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def main():
    print("Creating employee profiles for demo users...")

    db = next(get_db())

    try:
        # Get existing users
        super_admin = db.query(User).filter_by(email="admin@app.com").first()
        demo_user = db.query(User).filter_by(email="demo@company.com").first()
        company = db.query(Company).filter_by(name="Demo Company").first()

        if not company:
            print("Demo company not found!")
            return

        # Create profile for Super Admin
        if super_admin:
            existing_profile = db.query(EmployeeProfile).filter_by(user_id=super_admin.id).first()
            if not existing_profile:
                create_employee_profile(
                    db=db,
                    user_id=super_admin.id,
                    company_id=company.id,
                    department="IT",
                    position="System Administrator",
                    phone="+1234567890",
                    hire_date="2023-01-01",
                    manager_id=None
                )
                print("Created employee profile for Super Admin")

        # Create profile for demo user
        if demo_user:
            existing_profile = db.query(EmployeeProfile).filter_by(user_id=demo_user.id).first()
            if not existing_profile:
                create_employee_profile(
                    db=db,
                    user_id=demo_user.id,
                    company_id=company.id,
                    department="Engineering",
                    position="Software Engineer",
                    phone="+1234567891",
                    hire_date="2023-06-01",
                    manager_id=None
                )
                print("Created employee profile for Demo User")

        print("Employee profiles created successfully!")

    except Exception as e:
        print(f"Error creating profiles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
