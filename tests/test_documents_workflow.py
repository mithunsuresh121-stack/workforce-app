import pytest
from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.user import User
from app.models.company import Company
from app.crud import create_document, get_documents_by_company

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
def test_users(db_session: Session, test_company: Company):
    # Create admin user
    admin = User(
        email="admin@test.com",
        hashed_password="hashedpass",
        full_name="Test Admin",
        role="COMPANYADMIN",
        company_id=test_company.id
    )
    db_session.add(admin)

    # Create employee user
    employee = User(
        email="employee@test.com",
        hashed_password="hashedpass",
        full_name="Test Employee",
        role="EMPLOYEE",
        company_id=test_company.id
    )
    db_session.add(employee)

    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(employee)
    return admin, employee

def test_create_document(db_session: Session, test_users):
    admin, employee = test_users

    document_data = {
        "file_path": "/uploads/policies/hr_policy.pdf",
        "type": "POLICY",
        "access_role": "EMPLOYEE",
        "company_id": admin.company_id,
        "user_id": admin.id
    }

    document = create_document(db_session, document_data)

    assert document.file_path == "/uploads/policies/hr_policy.pdf"
    assert document.type.value == "POLICY"
    assert document.access_role == "EMPLOYEE"
    assert document.company_id == admin.company_id
    assert document.user_id == admin.id

def test_get_documents_by_company(db_session: Session, test_users):
    admin, employee = test_users

    # Create multiple documents
    documents_data = [
        {
            "file_path": "/uploads/policies/hr_policy.pdf",
            "type": "POLICY",
            "access_role": "EMPLOYEE",
            "company_id": admin.company_id,
            "user_id": admin.id
        },
        {
            "file_path": "/uploads/payslips/january_payslip.pdf",
            "type": "PAYSLIP",
            "access_role": "EMPLOYEE",
            "company_id": admin.company_id,
            "user_id": admin.id
        },
        {
            "file_path": "/uploads/notices/company_meeting.pdf",
            "type": "NOTICE",
            "access_role": "EMPLOYEE",
            "company_id": admin.company_id,
            "user_id": admin.id
        }
    ]

    for data in documents_data:
        create_document(db_session, data)

    # Retrieve documents
    documents = get_documents_by_company(db_session, admin.company_id)

    assert len(documents) >= 3
    types = [d.type.value for d in documents]
    assert "POLICY" in types
    assert "PAYSLIP" in types
    assert "NOTICE" in types

def test_document_access_control(db_session: Session, test_users):
    admin, employee = test_users

    # Create documents with different access roles
    documents_data = [
        {
            "file_path": "/uploads/policies/hr_policy.pdf",
            "type": "POLICY",
            "access_role": "EMPLOYEE",
            "company_id": admin.company_id,
            "user_id": admin.id
        },
        {
            "file_path": "/uploads/management/management_report.pdf",
            "type": "OTHER",
            "access_role": "MANAGER",
            "company_id": admin.company_id,
            "user_id": admin.id
        },
        {
            "file_path": "/uploads/admin/audit_report.pdf",
            "type": "OTHER",
            "access_role": "ADMIN",
            "company_id": admin.company_id,
            "user_id": admin.id
        }
    ]

    for data in documents_data:
        create_document(db_session, data)

    # Employee should see only EMPLOYEE level documents
    employee_docs = get_documents_by_company(db_session, admin.company_id, access_role="EMPLOYEE")
    employee_access_roles = [d.access_role for d in employee_docs]
    assert "EMPLOYEE" in employee_access_roles
    assert "MANAGER" not in employee_access_roles
    assert "ADMIN" not in employee_access_roles

    # Admin should see all documents
    admin_docs = get_documents_by_company(db_session, admin.company_id, access_role="ADMIN")
    admin_access_roles = [d.access_role for d in admin_docs]
    assert "EMPLOYEE" in admin_access_roles
    assert "MANAGER" in admin_access_roles
    assert "ADMIN" in admin_access_roles

def test_document_types(db_session: Session, test_users):
    admin, employee = test_users

    # Test all document types
    document_types = ["POLICY", "PAYSLIP", "NOTICE", "OTHER"]

    for doc_type in document_types:
        document_data = {
            "file_path": f"/uploads/{doc_type.lower()}/test_{doc_type.lower()}.pdf",
            "type": doc_type,
            "access_role": "EMPLOYEE",
            "company_id": admin.company_id,
            "user_id": admin.id
        }
        document = create_document(db_session, document_data)
        assert document.type.value == doc_type

def test_document_company_isolation(db_session: Session):
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

    # Create document for company 1
    doc1 = create_document(db_session, {
        "file_path": "/uploads/policies/company1_policy.pdf",
        "type": "POLICY",
        "access_role": "EMPLOYEE",
        "company_id": company1.id,
        "user_id": admin1.id
    })

    # Create document for company 2
    doc2 = create_document(db_session, {
        "file_path": "/uploads/policies/company2_policy.pdf",
        "type": "POLICY",
        "access_role": "EMPLOYEE",
        "company_id": company2.id,
        "user_id": admin2.id
    })

    # Verify isolation
    docs1 = get_documents_by_company(db_session, company1.id)
    docs2 = get_documents_by_company(db_session, company2.id)

    assert len(docs1) >= 1
    assert len(docs2) >= 1

    # Company 1 should only see its own documents
    company1_paths = [d.file_path for d in docs1]
    assert "/uploads/policies/company1_policy.pdf" in company1_paths
    assert "/uploads/policies/company2_policy.pdf" not in company1_paths

    # Company 2 should only see its own documents
    company2_paths = [d.file_path for d in docs2]
    assert "/uploads/policies/company2_policy.pdf" in company2_paths
    assert "/uploads/policies/company1_policy.pdf" not in company2_paths
