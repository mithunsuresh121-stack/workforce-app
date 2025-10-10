from sqlalchemy.orm import Session
from app.crud import create_user
from app.models.user import User
from app.models.company import Company
from app.db import SessionLocal

def create_manager():
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        if not company:
            print("No company found")
            return
        manager_email = "manager@company.com"
        manager_password = "password123"
        existing_manager = db.query(User).filter_by(email=manager_email, company_id=company.id).first()
        if existing_manager:
            print("Demo manager already exists.")
        else:
            create_user(db, manager_email, manager_password, full_name="Demo Manager", role="MANAGER", company_id=company.id)
            print("Demo manager created successfully.")
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_manager()
