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
import random

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
from app.models.chat import ChatMessage
from app.models.task import Task
from app.models.shift import Shift
from app.models.attendance import Attendance
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

        # Create 8-10 leaves with variety (mix approved/pending/rejected)
        leave_types = ["ANNUAL", "SICK", "PERSONAL", "MATERNITY", "PATERNITY"]
        leave_statuses = ["Approved", "Pending", "Rejected"]
        departments = ["Engineering", "HR", "Finance", "Marketing", "Operations"]

        for i in range(10):  # 10 leaves
            start_date = datetime.now() + timedelta(days=random.randint(-30, 60))
            end_date = start_date + timedelta(days=random.randint(1, 14))
            status = "Approved" if i < 4 else "Pending" if i < 7 else "Rejected"
            leave = Leave(
                company_id=company.id,
                tenant_id=str(company.id),
                employee_id=employee.id if i % 2 == 0 else manager.id,
                type=random.choice(leave_types),
                start_at=start_date,
                end_at=end_date,
                status=status
            )
            db.add(leave)
        db.commit()
        print("✅ Created 10 sample leaves with status variety")

        # Create 8-10 shifts with variety (day/night/remote patterns)
        shift_times = [
            ("09:00", "17:00"), ("08:00", "16:00"), ("10:00", "18:00"),  # Day shifts
            ("14:00", "22:00"), ("22:00", "06:00"), ("06:00", "14:00")  # Night/Other
        ]
        locations = ["Office A", "Office B", "Remote", "Client Site", "Home Office"]

        for i in range(10):  # 10 shifts
            start_time_str, end_time_str = random.choice(shift_times)
            shift_date = datetime.now() + timedelta(days=random.randint(-15, 45))
            location = "Remote" if i % 3 == 0 else random.choice(locations)
            status = "Pending" if i < 5 else "Completed"
            shift = Shift(
                company_id=company.id,
                employee_id=employee.id if i % 2 != 0 else manager.id,
                start_at=f"{shift_date.date()} {start_time_str}",
                end_at=f"{shift_date.date()} {end_time_str}",
                location=location,
                status=status
            )
            db.add(shift)
        db.commit()
        print("✅ Created 10 sample shifts with pattern variety")

        # Create 8-10 tasks with variety (different statuses)
        task_titles = [
            "Complete project documentation", "Review code changes", "Update database schema",
            "Prepare quarterly report", "Conduct team meeting", "Process payroll",
            "Handle customer inquiry", "Maintain server infrastructure", "Design new feature",
            "Test application functionality"
        ]
        task_priorities = ["LOW", "MEDIUM", "HIGH"]
        task_statuses = ["Pending", "In Progress", "Completed", "Cancelled"]

        for i in range(10):  # 10 tasks
            status = "PENDING" if i < 3 else "IN_PROGRESS" if i < 6 else "COMPLETED" if i < 8 else "OVERDUE"
            task = Task(
                company_id=company.id,
                assignee_id=employee.id if i % 2 == 0 else manager.id,
                assigned_by=manager.id,
                title=random.choice(task_titles),
                description=f"Detailed description for task {i+1}",
                priority=random.choice(task_priorities),
                status=status,
                due_at=datetime.now() + timedelta(days=random.randint(1, 30))
            )
            db.add(task)
        db.commit()
        print("✅ Created 10 sample tasks with status variety")

        # Create 8-10 documents with variety (company and personal-level)
        doc_types = ["POLICY", "PAYSLIP", "NOTICE", "OTHER"]
        access_roles = ["EMPLOYEE", "MANAGER", "ADMIN"]

        for i in range(10):  # 10 documents
            user_id = manager.id if i < 5 else employee.id  # Mix company (manager) and personal (employee)
            access_role = "ADMIN" if i < 3 else "MANAGER" if i < 6 else "EMPLOYEE"
            doc_type = "POLICY" if i < 4 else random.choice(doc_types)  # More policies for company
            doc = Document(
                company_id=company.id,
                user_id=user_id,
                file_path=f"uploads/{company.id}/{user_id}/document_{i+1}.pdf",
                type=doc_type,
                access_role=access_role
            )
            db.add(doc)
        db.commit()
        print("✅ Created 10 sample documents with ownership variety")

        # Create 8-10 notifications with variety (system-generated and user-triggered)
        notification_types = ["LEAVE_APPROVED", "LEAVE_REJECTED", "TASK_ASSIGNED", "SHIFT_SCHEDULED", "SHIFT_SWAP_REQUESTED", "SYSTEM_MESSAGE", "ADMIN_MESSAGE"]
        notification_titles = {
            "LEAVE_APPROVED": "Leave Approved",
            "LEAVE_REJECTED": "Leave Rejected",
            "TASK_ASSIGNED": "New Task Assigned",
            "SHIFT_REMINDER": "Shift Reminder",
            "ANNOUNCEMENT": "New Announcement",
            "MESSAGE_RECEIVED": "New Message Received",
            "SHIFT_SCHEDULED": "Shift Scheduled",
            "SYSTEM_MESSAGE": "System Message",
            "ADMIN_MESSAGE": "Admin Message"
        }

        for i in range(10):  # 10 notifications
            notif_type = "LEAVE_APPROVED" if i < 2 else "TASK_ASSIGNED" if i < 4 else "SHIFT_SCHEDULED" if i < 6 else "SYSTEM_MESSAGE" if i < 8 else "ADMIN_MESSAGE"
            user_id = employee.id if i % 2 == 0 else manager.id
            status = "UNREAD" if i < 5 else "READ"
            notification = Notification(
                user_id=user_id,
                company_id=company.id,
                title=notification_titles[notif_type],
                message=f"Notification message {i+1} for {notif_type}",
                type=notif_type,
                status=status
            )
            db.add(notification)
        db.commit()
        print("✅ Created 10 sample notifications with type variety")

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

        # Create example chat messages (10+ examples for better testing)
        example_messages = [
            {"sender_id": manager.id, "receiver_id": employee.id, "message": "Hello, how is the project going?", "is_read": True},
            {"sender_id": employee.id, "receiver_id": manager.id, "message": "It's going well, thanks for asking!", "is_read": False},
            {"sender_id": manager.id, "receiver_id": None, "message": "Company meeting at 3 PM today.", "is_read": False},  # Company-wide
            {"sender_id": employee.id, "receiver_id": manager.id, "message": "I need to discuss my leave request.", "is_read": True},
            {"sender_id": manager.id, "receiver_id": employee.id, "message": "Sure, let's schedule a call tomorrow.", "is_read": False},
            {"sender_id": manager.id, "receiver_id": None, "message": "Reminder: Submit timesheets by EOD Friday.", "is_read": False},  # Company-wide
            {"sender_id": employee.id, "receiver_id": manager.id, "message": "Timesheet submitted. Thanks!", "is_read": True},
            {"sender_id": manager.id, "receiver_id": employee.id, "message": "Great, I'll review it shortly.", "is_read": False},
            {"sender_id": manager.id, "receiver_id": None, "message": "Office will be closed for maintenance next Monday.", "is_read": False},  # Company-wide
            {"sender_id": employee.id, "receiver_id": manager.id, "message": "Noted. Any remote work options?", "is_read": False},
        ]
        for msg_data in example_messages:
            existing_msg = db.query(ChatMessage).filter(
                ChatMessage.sender_id == msg_data["sender_id"],
                ChatMessage.receiver_id == msg_data["receiver_id"],
                ChatMessage.message == msg_data["message"]
            ).first()
            if not existing_msg:
                msg = ChatMessage(
                    company_id=company.id,
                    sender_id=msg_data["sender_id"],
                    receiver_id=msg_data["receiver_id"],
                    message=msg_data["message"],
                    is_read=msg_data["is_read"]
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)
                print(f"✅ Created example chat message: {msg.id}")

        print("✅ Approval flow seed data created successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_approval_data()
