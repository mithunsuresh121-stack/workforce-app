import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_user_ids():
    db = SessionLocal()
    try:
        from backend.app.crud import create_user
        # Create test users with specific IDs for role-based testing
        create_user(db, "user50@example.com", "password123", "User 50", "Employee", 1)
        create_user(db, "user51@example.com", "password123", "User 51", "Employee", 1)
        create_user(db, "user52@example.com", "password123", "User 52", "Employee", 1)
        create_user(db, "user53@example.com", "password123", "User 53", "Employee", 1)
        print("Test user IDs created successfully.")
    except Exception as e:
        print(f"Error creating test user IDs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user_ids()
