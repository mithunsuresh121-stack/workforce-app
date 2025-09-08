#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db import SessionLocal
from app.models.user import User
from app.auth import hash_password

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_user:
            print(f"User admin@example.com already exists with ID: {existing_user.id}")
            return

        # Create the test user
        hashed_password = hash_password("password123")
        test_user = User(
            email="admin@example.com",
            hashed_password=hashed_password,
            full_name="Test Admin",
            role="SuperAdmin",
            company_id=None,  # SuperAdmin doesn't need company_id
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print(f"Created test user: {test_user.email} with ID: {test_user.id}")

    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
