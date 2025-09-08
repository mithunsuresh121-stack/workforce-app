import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_manager_user():
    db = SessionLocal()
    try:
        from backend.app.crud import create_user
        # Create manager user for company 1
        create_user(db, "manager@techcorp.com", "password123", "Manager User", "Manager", 1)
        print("Manager user created successfully.")
    except Exception as e:
        print(f"Error creating manager user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_manager_user()
