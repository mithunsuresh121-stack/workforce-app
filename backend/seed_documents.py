#!/usr/bin/env python3
"""
Seed documents and announcements
"""

import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.document import Document, DocumentType
from app.models.announcement import Announcement
from app.models.swap_request import SwapRequest  # to fix mapper issue
from app.db import SessionLocal

def seed_documents_and_announcements():
    db: Session = SessionLocal()

    try:
        # Assume company id 78 from previous seed
        company_id = 78
        manager_id = 320  # from previous

        # Create example documents (3 examples)
        example_docs = [
            {"file_path": f"uploads/{company_id}/{manager_id}/Policy.pdf", "type": DocumentType.POLICY, "access_role": "EMPLOYEE"},
            {"file_path": f"uploads/{company_id}/{manager_id}/Payslip.pdf", "type": DocumentType.PAYSLIP, "access_role": "EMPLOYEE"},
            {"file_path": f"uploads/{company_id}/{manager_id}/Notice.txt", "type": DocumentType.NOTICE, "access_role": "MANAGER"}
        ]
        for doc_data in example_docs:
            existing_doc = db.query(Document).filter(Document.file_path == doc_data["file_path"]).first()
            if not existing_doc:
                doc = Document(
                    company_id=company_id,
                    user_id=manager_id,
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
                    company_id=company_id,
                    created_by=manager_id,
                    title=ann_data["title"],
                    message=ann_data["message"]
                )
                db.add(ann)
                db.commit()
                db.refresh(ann)
                print(f"✅ Created example announcement: {ann.id}")

        print("✅ Documents and announcements seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_documents_and_announcements()
