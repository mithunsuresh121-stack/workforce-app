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
    company_data = CompanyCreate(name="Test Company")
    company = create_company(db, obj_in=company_data)
    db.commit()
    db.refresh(company)
    return company


@pytest.fixture(scope="function")
def test_user(db, test_company):
    user_data = UserCreate(
        email="test@example.com",
        full_name="Test User",
        company_id=test_company.id,
        role="EMPLOYEE",
        password="testpass"
    )
    user = create_user(db, obj_in=user_data)
    db.commit()
    db.refresh(user)
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
