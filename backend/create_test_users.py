from app.db import SessionLocal
from app.models.user import User
from app.auth import hash_password

def create_test_users():
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).filter(User.email.in_([
            "superadmin@test.com",
            "manager@test.com",
            "employee@test.com"
        ])).all()
        if existing_users:
            print("Test users already exist.")
            return

        # Create SuperAdmin
        superadmin = User(
            email="superadmin@test.com",
            hashed_password=hash_password("SuperAdminPass123"),
            full_name="Super Admin",
            role="SuperAdmin",
            is_active=True,
            company_id=None
        )
        db.add(superadmin)

        # Create Manager
        manager = User(
            email="manager@test.com",
            hashed_password=hash_password("ManagerPass123"),
            full_name="Manager User",
            role="Manager",
            is_active=True,
            company_id=1  # Assuming company with ID 1 exists
        )
        db.add(manager)

        # Create Employee
        employee = User(
            email="employee@test.com",
            hashed_password=hash_password("EmployeePass123"),
            full_name="Employee User",
            role="Employee",
            is_active=True,
            company_id=1
        )
        db.add(employee)

        db.commit()
        print("Test users created successfully.")
    except Exception as e:
        print(f"Error creating test users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
