#!/usr/bin/env python3
"""
Seed data for approval flow verification
"""

import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.user import User
from app.models.company import Company
from app.models.employee_profile import EmployeeProfile
from app.models.payroll import Employee as PayrollEmployee
from app.models.leave import Leave
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.notification import Notification, NotificationType
from app.models.document import Document
from app.models.announcement import Announcement
from app.crud import create_user, create_company, create_employee_profile
from app.db import SessionLocal

def seed_approval_data():
    db: Session = SessionLocal()

    try:
        # Get or create company
        company = db.query(Company).first()
        if not company:
            company = create_company(
                db=db,
                name="Test Company",
                domain="test.com",
                contact_email="admin@test.com",
                contact_phone="+1234567890",
                address="123 Test St",
                city="Test City",
                state="Test State",
                country="Test Country",
                postal_code="12345"
            )

        # Get or create manager user
        manager = db.query(User).filter(User.email == "manager@test.com").first()
        if not manager:
            manager = create_user(
                db=db,
                email="manager@test.com",
                password="password123",
                full_name="Test Manager",
                role="MANAGER",
                company_id=company.id
            )
            create_employee_profile(
                db=db,
                user_id=manager.id,
                company_id=company.id,
                department="Management",
                position="Manager",
                phone="+1234567891",
                hire_date="2023-01-01",
                manager_id=None
            )

        # Get or create employee user
        employee = db.query(User).filter(User.email == "employee@test.com").first()
        if not employee:
            employee = create_user(
                db=db,
                email="employee@test.com",
                password="password123",
                full_name="Test Employee",
                role="EMPLOYEE",
                company_id=company.id
            )
            create_employee_profile(
                db=db,
                user_id=employee.id,
                company_id=company.id,
                department="Engineering",
                position="Developer",
                phone="+1234567892",
                hire_date="2023-06-01",
                manager_id=manager.id
            )
            # Create payroll employee with salary
            payroll_employee = PayrollEmployee(
                tenant_id=str(company.id),
                user_id=employee.id,
                employee_id=f"EMP{employee.id}",
                department="Engineering",
                position="Developer",
                base_salary=4500.0,  # Sample salary
                status="Active"
            )
            db.add(payroll_employee)
            db.commit()
            db.refresh(payroll_employee)
            print(f"✅ Created payroll employee: {payroll_employee.id}")

        # Create pending leave
        # Commented out due to enum issue
        # pending_leave = db.query(Leave).filter(Leave.employee_id == employee.id, Leave.status == "Pending").first()
        # if not pending_leave:
        #     pending_leave = Leave(
        #         tenant_id=str(company.id),
        #         employee_id=employee.id,
        #         type="Sick Leave",
        #         start_at=datetime.now() + timedelta(days=10),
        #         end_at=datetime.now() + timedelta(days=12),
        #         status="Pending"
        #     )
        #     db.add(pending_leave)
        #     db.commit()
        #     db.refresh(pending_leave)
        #     print(f"✅ Created pending leave: {pending_leave.id}")

        # Create pending swap request
        # Commented out due to table not exist
        # pending_swap = db.query(SwapRequest).filter(SwapRequest.requester_id == employee.id, SwapRequest.status == SwapStatus.PENDING).first()
        # if not pending_swap:
        #     pending_swap = SwapRequest(
        #         requester_id=employee.id,
        #         target_employee_id=manager.id,
        #         requester_shift_id=1,  # Assume shift exists
        #         target_shift_id=2,
        #         status=SwapStatus.PENDING,
        #         company_id=company.id,
        #         reason="Test shift swap"
        #     )
        #     db.add(pending_swap)
        #     db.commit()
        #     db.refresh(pending_swap)
        #     print(f"✅ Created pending swap request: {pending_swap.id}")

        # Create sample notification
        # Commented out due to table not exist
        # sample_notification = db.query(Notification).filter(Notification.type == NotificationType.LEAVE_APPROVED).first()
        # if not sample_notification:
        #     sample_notification = Notification(
        #         user_id=employee.id,
        #         company_id=company.id,
        #         title="Leave Approved",
        #         message="Your Vacation leave request was approved by Test Manager.",
        #         type=NotificationType.LEAVE_APPROVED,
        #         status="UNREAD"
        #     )
        #     db.add(sample_notification)
        #     db.commit()
        #     db.refresh(sample_notification)
        #     print(f"✅ Created sample notification: {sample_notification.id}")

        # Create example documents (3 examples)
        from app.models.document import DocumentType
        example_docs = [
            {"file_path": f"uploads/{company.id}/{manager.id}/Policy.pdf", "type": DocumentType.POLICY, "access_role": "EMPLOYEE"},
            {"file_path": f"uploads/{company.id}/{manager.id}/Payslip.pdf", "type": DocumentType.PAYSLIP, "access_role": "EMPLOYEE"},
            {"file_path": f"uploads/{company.id}/{manager.id}/Notice.txt", "type": DocumentType.NOTICE, "access_role": "MANAGER"}
        ]
        for doc_data in example_docs:
            existing_doc = db.query(Document).filter(Document.file_path == doc_data["file_path"]).first()
            if not existing_doc:
                doc = Document(
                    company_id=company.id,
                    user_id=manager.id,
                    file_path=doc_data["file_path"],
                    type=doc_data["type"],
                    access_role=doc_data["access_role"]
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                print(f"✅ Created example document: {doc.id}")

        # Create example announcements (2 examples)
        example_announcements = [
            {"title": "Holiday Notice", "message": "Company holiday on December 25th. All employees get the day off."},
            {"title": "Payroll Reminder", "message": "Payroll will be processed on the 15th. Please submit timesheets by EOD."}
        ]
        for ann_data in example_announcements:
            existing_ann = db.query(Announcement).filter(Announcement.title == ann_data["title"]).first()
            if not existing_ann:
                ann = Announcement(
                    company_id=company.id,
                    created_by=manager.id,
                    title=ann_data["title"],
                    message=ann_data["message"]
                )
                db.add(ann)
                db.commit()
                db.refresh(ann)
                print(f"✅ Created example announcement: {ann.id}")

        print("✅ Approval flow seed data created successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_approval_data()
