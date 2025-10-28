import structlog
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

logger = structlog.get_logger(__name__)

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
        logger.info(
            "Super Admin user already exists",
            email=super_admin_email
        )
    else:
        # Create Super Admin user (no company_id needed)
        create_user(db, super_admin_email, super_admin_password,
                   full_name="Super Administrator", role="SUPERADMIN", company_id=None)
        logger.info(
            "Super Admin user created successfully",
            email=super_admin_email
        )
    
    # Create demo company and user (optional, for backward compatibility)
    demo_company_name = "Demo Company"
    company = get_company_by_name(db, demo_company_name)
    if not company:
        logger.info(
            "Creating demo company",
            company_name=demo_company_name
        )
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
        logger.info(
            "Demo company created successfully",
            company_id=company.id,
            company_name=demo_company_name
        )

    demo_email = "demo@company.com"
    demo_password = "password123"
    existing_user = db.query(User).filter_by(email=demo_email, company_id=company.id).first()
    if existing_user:
        logger.info(
            "Demo user already exists",
            email=demo_email,
            company_id=company.id
        )
        # Fix role if invalid
        if existing_user.role not in ["SUPERADMIN", "COMPANYADMIN", "MANAGER", "EMPLOYEE"]:
            existing_user.role = "EMPLOYEE"
            db.commit()
            logger.info(
                "Fixed demo user role to EMPLOYEE",
                user_id=existing_user.id,
                email=demo_email,
                company_id=company.id
            )
    else:
        create_user(db, demo_email, demo_password, full_name="Demo User", role="EMPLOYEE", company_id=company.id)
        logger.info(
            "Demo user created successfully",
            email=demo_email,
            company_id=company.id
        )

    # Create manager user
    manager_email = "manager@company.com"
    manager_password = "password123"
    existing_manager = db.query(User).filter_by(email=manager_email, company_id=company.id).first()
    if existing_manager:
        logger.info(
            "Demo manager already exists",
            email=manager_email,
            company_id=company.id
        )
        # Fix role if invalid
        if existing_manager.role not in ["SUPERADMIN", "COMPANYADMIN", "MANAGER", "EMPLOYEE"]:
            existing_manager.role = "MANAGER"
            db.commit()
            logger.info(
                "Fixed demo manager role to MANAGER",
                user_id=existing_manager.id,
                email=manager_email,
                company_id=company.id
            )
    else:
        create_user(db, manager_email, manager_password, full_name="Demo Manager", role="MANAGER", company_id=company.id)
        logger.info(
            "Demo manager created successfully",
            email=manager_email,
            company_id=company.id
        )

if __name__ == "__main__":
    db = next(get_db())
    seed_demo_user(db)
