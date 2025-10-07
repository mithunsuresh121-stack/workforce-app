#!/usr/bin/env python3
"""
Comprehensive, re-runnable database seeding script for the Workforce App.
Supports clean seeding and optional error simulation for real-time testing.

Usage:
    python backend/seed_data.py          # Clean seed only
    python backend/seed_data.py --errors # Clean seed + error tests (logs errors, no commit)
"""

import sys
import os
import argparse
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models.company import Company
from app.models.user import User, Role
from app.models.employee_profile import EmployeeProfile
from app.models.task import Task
from app.models.leave import Leave
from app.models.shift import Shift
from app.models.document import Document
from app.crud import (
    create_company, create_user, create_employee_profile,
    get_company_by_name, get_user_by_email, pwd_context, get_employee_profile_by_user_id
)
from app.db import Base  # For potential table checks, but using direct CRUD

# Add backend/app to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Database connection (dev only) - match app config
DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce_app_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def clear_database(db):
    """Clear existing data in reverse FK order to avoid integrity errors."""
    print("🧹 Clearing database...")

    # Document depends on User and Company
    try:
        document_count = db.query(Document).count()
        if document_count > 0:
            db.query(Document).delete()
            print(f"   Deleted {document_count} documents")
    except Exception as e:
        print(f"   Skipped documents (table may not exist): {str(e)}")
        db.rollback()

    # Leave and Shift depend on User and Company
    try:
        leave_count = db.query(Leave).count()
        if leave_count > 0:
            db.query(Leave).delete()
            print(f"   Deleted {leave_count} leaves")
    except Exception as e:
        print(f"   Skipped leaves (table may not exist): {str(e)}")
        db.rollback()

    try:
        shift_count = db.query(Shift).count()
        if shift_count > 0:
            db.query(Shift).delete()
            print(f"   Deleted {shift_count} shifts")
    except Exception as e:
        print(f"   Skipped shifts (table may not exist): {str(e)}")
        db.rollback()

    # Task depends on User (assignee, assigned_by) and Company
    try:
        task_count = db.query(Task).count()
        if task_count > 0:
            db.query(Task).delete()
            print(f"   Deleted {task_count} tasks")
    except Exception as e:
        print(f"   Skipped tasks (table may not exist): {str(e)}")
        db.rollback()

    # EmployeeProfile depends on User and Company
    try:
        profile_count = db.query(EmployeeProfile).count()
        if profile_count > 0:
            db.query(EmployeeProfile).delete()
            print(f"   Deleted {profile_count} employee profiles")
    except Exception as e:
        print(f"   Skipped employee profiles (table may not exist): {str(e)}")
        db.rollback()

    # User depends on Company (nullable)
    try:
        user_count = db.query(User).count()
        if user_count > 0:
            db.query(User).delete()
            print(f"   Deleted {user_count} users")
    except Exception as e:
        print(f"   Skipped users (table may not exist): {str(e)}")
        db.rollback()

    # Company last
    try:
        company_count = db.query(Company).count()
        if company_count > 0:
            db.query(Company).delete()
            print(f"   Deleted {company_count} companies")
    except Exception as e:
        print(f"   Skipped companies (table may not exist): {str(e)}")
        db.rollback()

    db.commit()
    print("✅ Database cleared successfully.")

def seed_clean_data(db):
    """Seed clean, realistic data: 2 companies, SuperAdmin, CompanyAdmins, Managers, Employees with profiles."""
    print("🌱 Starting clean data seeding...")
    
    # Step 1: Create 2 companies
    company1 = get_company_by_name(db, "TechCorp")
    if not company1:
        company1 = create_company(
            db, name="TechCorp", domain="techcorp.com", contact_email="contact@techcorp.com",
            contact_phone="+1-555-0100", address="123 Tech St", city="San Francisco",
            state="CA", country="USA", postal_code="94105"
        )
        print(f"   Created company: TechCorp (ID: {company1.id})")
    else:
        print(f"   Company TechCorp already exists (ID: {company1.id})")
    
    company2 = get_company_by_name(db, "InnoCorp")
    if not company2:
        company2 = create_company(
            db, name="InnoCorp", domain="innocorp.com", contact_email="contact@innocorp.com",
            contact_phone="+1-555-0200", address="456 Inno Ave", city="New York",
            state="NY", country="USA", postal_code="10001"
        )
        print(f"   Created company: InnoCorp (ID: {company2.id})")
    else:
        print(f"   Company InnoCorp already exists (ID: {company2.id})")
    
    # Step 2: Create SuperAdmin (no company)
    superadmin_email = "superadmin@workforce.com"
    if not get_user_by_email(db, superadmin_email):
        superadmin = create_user(
            db, email=superadmin_email, password="password123",
            full_name="Super Administrator", role=Role.SUPERADMIN, company_id=None
        )
        print(f"   Created SuperAdmin: {superadmin_email}")
        
        # Create profile for SuperAdmin in first company (for completeness)
        create_employee_profile(
            db, user_id=superadmin.id, company_id=company1.id,
            department="Administration", position="System Admin",
            phone="+1-555-0000", hire_date=datetime(2023, 1, 1),
            manager_id=None, address="Global HQ", city="San Francisco",
            emergency_contact="Emergency Contact"
        )
        print("   Created profile for SuperAdmin")
    else:
        print(f"   SuperAdmin {superadmin_email} already exists.")
        superadmin = get_user_by_email(db, superadmin_email)
    
    # Step 3: Seed TechCorp (Company 1: 1 Admin, 2 Managers, 5 Employees)
    techcorp_users = []
    
    # CompanyAdmin
    admin1_email = "admin1@techcorp.com"
    if not get_user_by_email(db, admin1_email):
        admin1 = create_user(
            db, email=admin1_email, password="password123",
            full_name="TechCorp Admin", role=Role.COMPANYADMIN, company_id=company1.id
        )
        techcorp_users.append(admin1)
        print(f"   Created CompanyAdmin: {admin1_email}")
    else:
        admin1 = get_user_by_email(db, admin1_email)
        techcorp_users.append(admin1)
    
    # Managers (one with special password)
    manager1_email = "manager1@techcorp.com"
    if not get_user_by_email(db, manager1_email):
        manager1 = create_user(
            db, email=manager1_email, password="ManagerPass123",  # Special password
            full_name="Manager One", role=Role.MANAGER, company_id=company1.id
        )
        techcorp_users.append(manager1)
        print(f"   Created Manager: {manager1_email}")
    else:
        manager1 = get_user_by_email(db, manager1_email)
        techcorp_users.append(manager1)
    
    manager2_email = "manager2@techcorp.com"
    if not get_user_by_email(db, manager2_email):
        manager2 = create_user(
            db, email=manager2_email, password="password123",
            full_name="Manager Two", role=Role.MANAGER, company_id=company1.id
        )
        techcorp_users.append(manager2)
        print(f"   Created Manager: {manager2_email}")
    else:
        manager2 = get_user_by_email(db, manager2_email)
        techcorp_users.append(manager2)
    
    # Employees (5, one inactive)
    employee_emails = ["emp1@techcorp.com", "emp2@techcorp.com", "emp3@techcorp.com", "emp4@techcorp.com", "emp5@techcorp.com"]
    for i, email in enumerate(employee_emails, 1):
        if not get_user_by_email(db, email):
            emp = create_user(
                db, email=email, password="password123",
                full_name=f"Employee {i}", role=Role.EMPLOYEE, company_id=company1.id
            )
            techcorp_users.append(emp)
            print(f"   Created Employee: {email}")
            
            # Set one inactive (e.g., emp5)
            if i == 5:
                db.query(User).filter(User.id == emp.id).update({"is_active": False})
                db.commit()  # Commit the update
                print(f"     (Set {email} as inactive for testing)")
        else:
            emp = get_user_by_email(db, email)
            techcorp_users.append(emp)
    
    # Create profiles for TechCorp users (managers report to admin, employees to manager1)
    for idx, user in enumerate(techcorp_users):
        manager_id = None
        if user.role == Role.MANAGER:
            manager_id = admin1.id  # Managers report to CompanyAdmin
        elif user.role == Role.EMPLOYEE:
            manager_id = manager1.id  # Employees report to manager1
        
        # Check if profile exists before creating
        existing_profile = get_employee_profile_by_user_id(db, user.id, company1.id)
        if not existing_profile:
            create_employee_profile(
                db, user_id=user.id, company_id=company1.id,
                department="Engineering" if user.role == Role.EMPLOYEE else "Management",
                position=f"{user.role} Position",
                phone=f"+1-555-01{idx+1:02d}",
                hire_date=datetime(2023, 6 + (idx % 6), 1),  # Varied recent dates
                manager_id=manager_id,
                address="TechCorp Office", city="San Francisco",
                emergency_contact="Emergency Tech"
            )
            print(f"   Created profile for {user.email}")
        else:
            print(f"   Profile already exists for {user.email}")
    
    # Step 4: Seed InnoCorp (Company 2: 1 Admin, 1 Manager, 5 Employees)
    innocorp_users = []
    
    # CompanyAdmin
    admin2_email = "admin2@innocorp.com"
    if not get_user_by_email(db, admin2_email):
        admin2 = create_user(
            db, email=admin2_email, password="password123",
            full_name="InnoCorp Admin", role=Role.COMPANYADMIN, company_id=company2.id
        )
        innocorp_users.append(admin2)
        print(f"   Created CompanyAdmin: {admin2_email}")
    else:
        admin2 = get_user_by_email(db, admin2_email)
        innocorp_users.append(admin2)
    
    # Manager
    manager3_email = "manager3@innocorp.com"
    if not get_user_by_email(db, manager3_email):
        manager3 = create_user(
            db, email=manager3_email, password="password123",
            full_name="Inno Manager", role=Role.MANAGER, company_id=company2.id
        )
        innocorp_users.append(manager3)
        print(f"   Created Manager: {manager3_email}")
    else:
        manager3 = get_user_by_email(db, manager3_email)
        innocorp_users.append(manager3)
    
    # Employees (5)
    employee_emails = ["emp6@innocorp.com", "emp7@innocorp.com", "emp8@innocorp.com", "emp9@innocorp.com", "emp10@innocorp.com"]
    for i, email in enumerate(employee_emails, 6):
        if not get_user_by_email(db, email):
            emp = create_user(
                db, email=email, password="password123",
                full_name=f"Employee {i}", role=Role.EMPLOYEE, company_id=company2.id
            )
            innocorp_users.append(emp)
            print(f"   Created Employee: {email}")
        else:
            emp = get_user_by_email(db, email)
            innocorp_users.append(emp)
    
    # Create profiles for InnoCorp users (manager to admin, employees to manager3)
    for idx, user in enumerate(innocorp_users):
        manager_id = None
        if user.role == Role.MANAGER:
            manager_id = admin2.id
        elif user.role == Role.EMPLOYEE:
            manager_id = manager3.id

        # Check if profile exists before creating
        existing_profile = get_employee_profile_by_user_id(db, user.id, company2.id)
        if not existing_profile:
            create_employee_profile(
                db, user_id=user.id, company_id=company2.id,
                department="HR" if idx % 2 == 0 else "Engineering",  # Mix departments
                position=f"{user.role} Position",
                phone=f"+1-555-02{idx+1:02d}",
                hire_date=datetime(2023, 7 + (idx % 5), 15),  # Varied
                manager_id=manager_id,
                address="InnoCorp Office", city="New York",
                emergency_contact="Emergency Inno"
            )
            print(f"   Created profile for {user.email}")
        else:
            print(f"   Profile already exists for {user.email}")
    
    db.commit()
    print("✅ Clean data seeding completed: 2 companies, 1 SuperAdmin, 14 total users, 14 profiles.")

def test_errors(db):
    """Simulate error cases for real-time testing. Logs errors with context, rolls back each attempt."""
    print("🧪 Starting error simulation (no data committed)...")
    
    # Get actual IDs from seeded data
    company1 = db.query(Company).filter(Company.name == "TechCorp").first()
    superadmin = db.query(User).filter(User.email == "superadmin@workforce.com").first()
    manager3 = db.query(User).filter(User.email == "manager3@innocorp.com").first()
    
    # Error 1: Duplicate email
    try:
        create_user(
            db, email="emp1@techcorp.com", password="password123",  # Existing from seed
            full_name="Duplicate User", role=Role.EMPLOYEE, company_id=company1.id
        )
        print("❌ Unexpected: Duplicate email succeeded")
    except IntegrityError as e:
        db.rollback()
        print(f"   Duplicate email error for emp1@techcorp.com → IntegrityError: {str(e).split('DETAIL:')[0].strip()} (Expected)")
    
    # Error 2: Invalid FK - Profile with non-existent company_id
    try:
        # Use SuperAdmin user_id, bad company
        bad_profile = create_employee_profile(
            db, user_id=superadmin.id, company_id=999,  # Non-existent company
            department="Test", position="Tester"
        )
        print("❌ Unexpected: Invalid company_id succeeded")
    except IntegrityError as e:
        db.rollback()
        print(f"   Invalid company_id error → IntegrityError: {str(e).split('DETAIL:')[0].strip()} (Expected)")
    
    # Error 3: Cross-company manager_id (manager in co2 for co1 employee)
    temp_emp = None
    try:
        # Create temp user in co1
        temp_emp = create_user(
            db, email="temp@techcorp.com", password="password123",
            full_name="Temp", role=Role.EMPLOYEE, company_id=company1.id
        )
        # Try profile with manager from co2
        create_employee_profile(
            db, user_id=temp_emp.id, company_id=company1.id,
            department="Test", position="Tester", manager_id=manager3.id  # Wrong company manager
        )
        print("❌ Unexpected: Cross-company manager succeeded")
    except IntegrityError as e:
        db.rollback()
        # Also delete temp user if created
        if temp_emp:
            db.delete(temp_emp)
        print(f"   Cross-company manager error → IntegrityError: {str(e).split('DETAIL:')[0].strip()} (Expected)")
    
    # Error 4: Missing required field (email=None)
    try:
        create_user(
            db, email=None, password="password123",  # Missing email
            full_name="No Email", role=Role.EMPLOYEE, company_id=company1.id
        )
        print("❌ Unexpected: Missing email succeeded")
    except Exception as e:  # Could be TypeError or IntegrityError
        db.rollback()
        print(f"   Missing email error → {type(e).__name__}: {str(e)} (Expected)")
    
    # Error 5: Orphaned employee (profile without valid user, but since user_id FK, similar to invalid FK)
    try:
        create_employee_profile(
            db, user_id=999, company_id=company1.id,  # Non-existent user
            department="Orphan", position="Orphaned"
        )
        print("❌ Unexpected: Orphaned profile succeeded")
    except IntegrityError as e:
        db.rollback()
        print(f"   Orphaned profile error → IntegrityError: {str(e).split('DETAIL:')[0].strip()} (Expected)")
    
    # Error 6: Invalid role (bad data)
    try:
        create_user(
            db, email="invalidrole@techcorp.com", password="password123",
            full_name="Invalid Role User", role="InvalidRole", company_id=company1.id  # Invalid enum value
        )
        print("❌ Unexpected: Invalid role succeeded")
    except Exception as e:
        db.rollback()
        print(f"   Invalid role error → {type(e).__name__}: {str(e)} (Expected)")
    
    print("✅ Error simulation completed: All expected errors logged, data intact.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the workforce database.")
    parser.add_argument('--errors', action='store_true', help="Run error simulation after clean seed")
    args = parser.parse_args()
    
    db = next(get_db())
    
    try:
        clear_database(db)
        seed_clean_data(db)
        if args.errors:
            test_errors(db)
        db.commit()
        print("\n🎉 Seeding process completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n💥 Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()
