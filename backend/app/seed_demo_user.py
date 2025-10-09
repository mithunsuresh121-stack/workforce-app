from sqlalchemy.orm import Session
from passlib.context import CryptContext
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.crud import create_user, get_company_by_id, get_company_by_name, create_company
from app.models.user import User
from app.models.company import Company

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a direct database connection to localhost
DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_demo_user(db: Session):
    # Create Super Admin user
    super_admin_email = "admin@app.com"
    super_admin_password = "supersecure123"
    
    # Check if Super Admin already exists
    existing_super_admin = db.query(User).filter_by(email=super_admin_email).first()
    if existing_super_admin:
        print("Super Admin user already exists.")
    else:
        # Create Super Admin user (no company_id needed)
        create_user(db, super_admin_email, super_admin_password,
                   full_name="Super Administrator", role="SUPERADMIN", company_id=None)
        print("Super Admin user created successfully.")
    
    # Create demo company and user (optional, for backward compatibility)
    demo_company_name = "Demo Company"
    company = get_company_by_name(db, demo_company_name)
    if not company:
        print("Creating demo company...")
        company = create_company(
            db, 
            name=demo_company_name, 
            domain="demo.com", 
            contact_email="demo@company.com",
            contact_phone="+1234567890",
            address="123 Demo Street",
            city="Demo City",
            state="Demo State",
            country="Demo Country",
            postal_code="12345"
        )
        print("Demo company created successfully.")

    demo_email = "demo@company.com"
    demo_password = "password123"
    existing_user = db.query(User).filter_by(email=demo_email, company_id=company.id).first()
    if existing_user:
        print("Demo user already exists.")
        # Fix role if invalid
        if existing_user.role not in ["SUPERADMIN", "COMPANYADMIN", "MANAGER", "EMPLOYEE"]:
            existing_user.role = "EMPLOYEE"
            db.commit()
            print("Fixed demo user role to EMPLOYEE.")
    else:
        create_user(db, demo_email, demo_password, full_name="Demo User", role="EMPLOYEE", company_id=company.id)
        print("Demo user created successfully.")

if __name__ == "__main__":
    db = next(get_db())
    seed_demo_user(db)
