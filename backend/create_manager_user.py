#!/usr/bin/env python3
"""
Script to create a Manager user for testing role-based task management.
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

# Create a direct database connection
DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_manager_user(db):
    """Create a Manager user for testing"""

    # Get the demo company
    company = db.query(Company).filter_by(name="Demo Company").first()
    if not company:
        print("Demo company not found. Please run the seed script first.")
        return

    manager_email = "manager@company.com"
    manager_password = "manager123"

    # Check if Manager already exists
    existing_manager = db.query(User).filter_by(email=manager_email).first()
    if existing_manager:
        print("Manager user already exists.")
        return existing_manager

    # Create Manager user
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(manager_password)

    manager = User(
        email=manager_email,
        hashed_password=hashed_password,
        full_name="Test Manager",
        role="Manager",
        company_id=company.id,
        is_active=True
    )

    db.add(manager)
    db.commit()
    db.refresh(manager)

    # Create employee profile for Manager
    profile = EmployeeProfile(
        user_id=manager.id,
        company_id=company.id,
        department="Engineering",
        position="Engineering Manager",
        phone="+1234567892",
        hire_date="2023-03-01",
        manager_id=None,
        is_active=True
    )
    db.add(profile)
    db.commit()

    print(f"Manager user created successfully!")
    print(f"Email: {manager_email}")
    print(f"Password: {manager_password}")
    print(f"Role: Manager")

    return manager

if __name__ == "__main__":
    db = next(get_db())
    try:
        create_manager_user(db)
    finally:
        db.close()
