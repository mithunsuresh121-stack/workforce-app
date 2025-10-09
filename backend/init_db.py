#!/usr/bin/env python3
"""
Database initialization script for Workforce Management App
Creates initial companies and a super admin user for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.company import Company
from app.models.user import User
from app.models import *  # Import all models to ensure tables are created
from app.auth import hash_password

def init_database():
    """Initialize the database with sample data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if companies already exist
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            print("Database already initialized with companies.")
            # Still create tables if missing
            Base.metadata.create_all(bind=engine)
            return
        
        # Create sample companies
        company1 = Company(
            name="TechCorp Inc.",
            domain="techcorp.com",
            contact_email="admin@techcorp.com",
            contact_phone="+1-555-0123",
            address="123 Tech Street",
            city="San Francisco",
            state="CA",
            country="USA",
            postal_code="94105"
        )
        
        company2 = Company(
            name="Global Services Ltd.",
            domain="globalservices.com",
            contact_email="info@globalservices.com",
            contact_phone="+1-555-0456",
            address="456 Business Ave",
            city="New York",
            state="NY",
            country="USA",
            postal_code="10001"
        )
        
        db.add(company1)
        db.add(company2)
        db.commit()
        db.refresh(company1)
        db.refresh(company2)
        
        # Create super admin user for TechCorp
        super_admin = User(
            email="admin@techcorp.com",
            hashed_password=hash_password("admin123"),
            full_name="System Administrator",
            role="SuperAdmin",
            company_id=company1.id
        )
        
        # Create regular user for Global Services
        regular_user = User(
            email="user@globalservices.com",
            hashed_password=hash_password("user123"),
            full_name="John Doe",
            role="Employee",
            company_id=company2.id
        )
        
        db.add(super_admin)
        db.add(regular_user)
        db.commit()
        
        print("Database initialized successfully!")
        print(f"Created companies: {company1.name}, {company2.name}")
        print(f"Created users: {super_admin.email}, {regular_user.email}")
        print("\nTest credentials:")
        print("Super Admin - Email: admin@techcorp.com, Password: admin123, Company ID: 1")
        print("Regular User - Email: user@globalservices.com, Password: user123, Company ID: 2")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
