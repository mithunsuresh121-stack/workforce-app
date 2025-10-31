import sys
from pathlib import Path
import os

# Fix for module discovery when running from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app
from app.models.user import User
from app.models.company import Company
from app.crud import create_user, create_company
from app.schemas.schemas import UserCreate, CompanyCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create a new database for each test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_company(db):
    company = create_company(db, name="Test Company")
    return company


@pytest.fixture(scope="function")
def test_user(db, test_company):
    user = create_user(
        db=db,
        email="test@example.com",
        password="testpass",
        full_name="Test User",
        role="EMPLOYEE",
        company_id=test_company.id
    )
    return user

@pytest.fixture(scope="function")
def test_user2(db, test_company):
    user = create_user(
        db=db,
        email="test2@example.com",
        password="testpass",
        full_name="Test User 2",
        role="EMPLOYEE",
        company_id=test_company.id
    )
    return user


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with app.test_client() as client:
        yield client
    app.dependency_overrides.clear()
