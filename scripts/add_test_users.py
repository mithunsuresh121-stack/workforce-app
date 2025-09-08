import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_test_users():
    db = SessionLocal()
    try:
        from backend.app.crud import create_user, create_company

        from backend.app.crud import get_company_by_name

        # Get or create company for test@company.com
        company1 = get_company_by_name(db, "Test Company Inc")
        if not company1:
            company1 = create_company(
                db,
                name="Test Company Inc",
                domain="companyinc.com",
                contact_email="contact@companyinc.com",
                contact_phone="+1234567890",
                address="123 Test St",
                city="Test City",
                state="Test State",
                country="Test Country",
                postal_code="12345"
            )

        # Get or create company for admin@techcorp.com
        company2 = get_company_by_name(db, "TechCorp Inc")
        if not company2:
            company2 = create_company(
                db,
                name="TechCorp Inc",
                domain="techcorpinc.com",
                contact_email="admin@techcorpinc.com",
                contact_phone="+1234567890",
                address="456 Tech St",
                city="Tech City",
                state="Tech State",
                country="Tech Country",
                postal_code="67890"
            )

        from backend.app.crud import get_user_by_email_only

        # Create employee user if not exists
        if not get_user_by_email_only(db, "test@company.com"):
            create_user(db, "test@company.com", "password123", "Test Employee", "Employee", company1.id)

        # Create admin user if not exists
        if not get_user_by_email_only(db, "admin@techcorp.com"):
            create_user(db, "admin@techcorp.com", "password123", "Admin User", "CompanyAdmin", company2.id)

        print("Test users created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_test_users()
