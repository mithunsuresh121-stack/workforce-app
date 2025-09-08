import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_users():
    db = SessionLocal()
    try:
        from backend.app.crud import create_user
        # Create test users for role-based testing
        create_user(db, "test_superadmin@example.com", "password123", "Test SuperAdmin", "SuperAdmin", None)
        create_user(db, "test_companyadmin@example.com", "password123", "Test CompanyAdmin", "CompanyAdmin", 1)
        create_user(db, "test_manager@example.com", "password123", "Test Manager", "Manager", 1)
        create_user(db, "test_employee@example.com", "password123", "Test Employee", "Employee", 1)
        print("Test users created successfully.")
    except Exception as e:
        print(f"Error creating test users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
