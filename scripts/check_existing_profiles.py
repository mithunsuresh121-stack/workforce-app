import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_profiles():
    db = SessionLocal()
    try:
        from backend.app.models.employee_profile import EmployeeProfile
        profiles = db.query(EmployeeProfile).all()
        print("Existing employee profiles:")
        for profile in profiles:
            print(f"ID: {profile.id}, User ID: {profile.user_id}, Company ID: {profile.company_id}, Department: {profile.department}")
    finally:
        db.close()

if __name__ == "__main__":
    check_profiles()
