from sqlalchemy.orm import Session
from app import models, crud
from app.db import SessionLocal
from app.auth import hash_password

def seed():
    db: Session = SessionLocal()

    # Ensure test admin user exists
    user = crud.get_user_by_email(db, email="admin@example.com")
    if not user:
        user = models.User(
            email="admin@example.com",
            hashed_password=hash_password("password123"),
            full_name="Test Admin",
            role="SuperAdmin",
            company_id=1,  # Assuming default company exists
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✅ Created test admin user")

    # Ensure at least one employee exists
    employee = db.query(models.EmployeeProfile).first()
    if not employee:
        # Create employee profile
        employee = models.EmployeeProfile(
            user_id=user.id,
            company_id=1,  # Assuming default company exists
            department="Engineering",
            position="Software Engineer",
            hire_date="2023-01-01",
            phone="555-123-4567",
            is_active=True
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        print("✅ Created test employee profile")

if __name__ == "__main__":
    seed()
