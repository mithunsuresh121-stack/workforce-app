import pytest
from sqlalchemy.orm import Session
from app.models.announcement import Announcement
from app.models.user import User
from app.models.company import Company
from app.crud import create_announcement, get_announcements

@pytest.fixture
def db_session():
    from app.db import get_db
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_company(db_session: Session):
    company = Company(
        name="Test Company",
        domain="test.com",
        contact_email="admin@test.com"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture
def test_admin(db_session: Session, test_company: Company):
    admin = User(
        email="admin@test.com",
        hashed_password="hashedpass",
        full_name="Test Admin",
        role="COMPANYADMIN",
        company_id=test_company.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

def test_create_announcement(db_session: Session, test_admin: User):
    announcement_data = {
        "title": "Company Meeting",
        "message": "There will be a company meeting tomorrow at 10 AM.",
        "company_id": test_admin.company_id,
        "created_by": test_admin.id
    }

    announcement = create_announcement(db_session, announcement_data)

    assert announcement.title == "Company Meeting"
    assert announcement.message == "There will be a company meeting tomorrow at 10 AM."
    assert announcement.company_id == test_admin.company_id
    assert announcement.created_by == test_admin.id

def test_get_announcements(db_session: Session, test_admin: User):
    # Create multiple announcements
    announcements_data = [
        {
            "title": "Holiday Notice",
            "message": "Office will be closed for holiday.",
            "company_id": test_admin.company_id,
            "created_by": test_admin.id
        },
        {
            "title": "Policy Update",
            "message": "New remote work policy effective next month.",
            "company_id": test_admin.company_id,
            "created_by": test_admin.id
        }
    ]

    for data in announcements_data:
        create_announcement(db_session, data)

    # Retrieve announcements
    announcements = get_announcements(db_session, test_admin.company_id)

    assert len(announcements) >= 2  # May have more from other tests
    titles = [a.title for a in announcements]
    assert "Holiday Notice" in titles
    assert "Policy Update" in titles

def test_announcement_ordering(db_session: Session, test_admin: User):
    # Create announcements with different timestamps
    import time

    announcement1 = create_announcement(db_session, {
        "title": "First Announcement",
        "message": "First message",
        "company_id": test_admin.company_id,
        "created_by": test_admin.id
    })
    time.sleep(0.1)  # Small delay to ensure different timestamps

    announcement2 = create_announcement(db_session, {
        "title": "Second Announcement",
        "message": "Second message",
        "company_id": test_admin.company_id,
        "created_by": test_admin.id
    })

    announcements = get_announcements(db_session, test_admin.company_id, limit=2)

    # Should be ordered by creation time descending (newest first)
    assert announcements[0].title == "Second Announcement"
    assert announcements[1].title == "First Announcement"

def test_announcement_company_isolation(db_session: Session):
    # Create two companies
    company1 = Company(
        name="Company 1",
        domain="company1.com",
        contact_email="admin@company1.com"
    )
    company2 = Company(
        name="Company 2",
        domain="company2.com",
        contact_email="admin@company2.com"
    )
    db_session.add(company1)
    db_session.add(company2)
    db_session.commit()

    # Create admin for each company
    admin1 = User(
        email="admin1@test.com",
        hashed_password="hashedpass",
        full_name="Admin 1",
        role="COMPANYADMIN",
        company_id=company1.id
    )
    admin2 = User(
        email="admin2@test.com",
        hashed_password="hashedpass",
        full_name="Admin 2",
        role="COMPANYADMIN",
        company_id=company2.id
    )
    db_session.add(admin1)
    db_session.add(admin2)
    db_session.commit()

    # Create announcement for company 1
    announcement1 = create_announcement(db_session, {
        "title": "Company 1 Announcement",
        "message": "Message for company 1",
        "company_id": company1.id,
        "created_by": admin1.id
    })

    # Create announcement for company 2
    announcement2 = create_announcement(db_session, {
        "title": "Company 2 Announcement",
        "message": "Message for company 2",
        "company_id": company2.id,
        "created_by": admin2.id
    })

    # Verify isolation
    announcements1 = get_announcements(db_session, company1.id)
    announcements2 = get_announcements(db_session, company2.id)

    assert len(announcements1) >= 1
    assert len(announcements2) >= 1

    # Company 1 should only see its own announcements
    company1_titles = [a.title for a in announcements1]
    assert "Company 1 Announcement" in company1_titles
    assert "Company 2 Announcement" not in company1_titles

    # Company 2 should only see its own announcements
    company2_titles = [a.title for a in announcements2]
    assert "Company 2 Announcement" in company2_titles
    assert "Company 1 Announcement" not in company2_titles

def test_announcement_validation(db_session: Session, test_admin: User):
    # Test empty title
    with pytest.raises(ValueError):
        create_announcement(db_session, {
            "title": "",
            "message": "Valid message",
            "company_id": test_admin.company_id,
            "created_by": test_admin.id
        })

    # Test empty message
    with pytest.raises(ValueError):
        create_announcement(db_session, {
            "title": "Valid Title",
            "message": "",
            "company_id": test_admin.company_id,
            "created_by": test_admin.id
        })
