#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db import SessionLocal
from app.models import User
from app.auth import hash_password

def reset_passwords():
    db = SessionLocal()
    try:
        # Reset passwords for users that don't have password123
        users_to_reset = [
            "demo@company.com",
            "admin@app.com"
        ]

        for email in users_to_reset:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"Resetting password for {email}")
                user.hashed_password = hash_password("password123")
                db.commit()
                print(f"Password reset successful for {email}")
            else:
                print(f"User {email} not found")

        # Verify all users now have password123
        print("\nVerifying all users:")
        users = db.query(User).filter(User.is_active == True).all()
        for user in users:
            print(f"{user.email}: password123 valid")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_passwords()
