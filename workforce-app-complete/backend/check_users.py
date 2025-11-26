#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db import SessionLocal
from app.models import User
from app.auth import verify_password

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Company ID: {user.company_id}")
            print(f"  Role: {user.role}")
            print(f"  Active: {user.is_active}")
            print(f"  Hashed Password: {user.hashed_password[:20]}...")
            print()

            # Test password verification
            test_password = "password123"
            is_valid = verify_password(test_password, user.hashed_password)
            print(f"  Password 'password123' valid: {is_valid}")

            if user.email == "demo@company.com":
                test_password = "password123"
                is_valid = verify_password(test_password, user.hashed_password)
                print(f"  Demo user password valid: {is_valid}")

            print("-" * 50)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
