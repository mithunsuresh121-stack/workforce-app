from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.crud import create_task
from app.models.task import TaskStatus
from app.models.user import User
from app.models.company import Company

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

def create_sample_tasks(db: Session):
    # Get the demo user
    demo_user = db.query(User).filter_by(email="demo@company.com").first()
    if not demo_user:
        print("Demo user not found. Please run the seed script first.")
        return

    # Get the demo company
    company = db.query(Company).filter_by(name="Demo Company").first()
    if not company:
        print("Demo company not found.")
        return

    print(f"Creating sample tasks for user: {demo_user.full_name} (ID: {demo_user.id})")

    # Sample tasks with different statuses
    tasks_data = [
        {
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the new feature",
            "status": TaskStatus.COMPLETED,
            "assignee_id": demo_user.id,
            "company_id": company.id,
            "created_at": datetime.now() - timedelta(days=7)
        },
        {
            "title": "Review pull request #123",
            "description": "Review and approve the latest code changes",
            "status": TaskStatus.IN_PROGRESS,
            "assignee_id": demo_user.id,
            "company_id": company.id,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "title": "Update user interface design",
            "description": "Implement the new UI mockups from the design team",
            "status": TaskStatus.PENDING,
            "assignee_id": demo_user.id,
            "company_id": company.id,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "title": "Fix database performance issue",
            "description": "Optimize slow queries in the reporting module",
            "status": TaskStatus.OVERDUE,
            "assignee_id": demo_user.id,
            "company_id": company.id,
            "created_at": datetime.now() - timedelta(days=10)
        },
        {
            "title": "Prepare quarterly report",
            "description": "Compile Q4 metrics and prepare presentation",
            "status": TaskStatus.COMPLETED,
            "assignee_id": demo_user.id,
            "company_id": company.id,
            "created_at": datetime.now() - timedelta(days=5)
        }
    ]

    created_count = 0
    for task_data in tasks_data:
        try:
            # Check if task already exists
            existing_task = db.query(db.model.task).filter_by(
                title=task_data["title"],
                assignee_id=task_data["assignee_id"]
            ).first()

            if not existing_task:
                create_task(
                    db=db,
                    title=task_data["title"],
                    description=task_data["description"],
                    status=task_data["status"],
                    assignee_id=task_data["assignee_id"],
                    company_id=task_data["company_id"],
                    created_at=task_data["created_at"]
                )
                created_count += 1
                print(f"✓ Created task: {task_data['title']} ({task_data['status'].value})")
            else:
                print(f"⚠ Task already exists: {task_data['title']}")
        except Exception as e:
            print(f"✗ Error creating task '{task_data['title']}': {str(e)}")

    print(f"\nSample tasks creation completed. Created {created_count} new tasks.")

    # Also create some sample leave requests
    print("\nCreating sample leave requests...")
    from app.crud import create_leave_request
    from app.models.leave import LeaveRequest
    from app.schemas.schemas import LeaveStatus

    leave_data = [
        {
            "employee_id": demo_user.id,
            "type": "Annual Leave",
            "start_date": datetime.now() + timedelta(days=7),
            "end_date": datetime.now() + timedelta(days=10),
            "reason": "Family vacation",
            "status": LeaveStatus.APPROVED
        },
        {
            "employee_id": demo_user.id,
            "type": "Sick Leave",
            "start_date": datetime.now() - timedelta(days=3),
            "end_date": datetime.now() - timedelta(days=2),
            "reason": "Medical appointment",
            "status": LeaveStatus.APPROVED
        },
        {
            "employee_id": demo_user.id,
            "type": "Personal Leave",
            "start_date": datetime.now() + timedelta(days=14),
            "end_date": datetime.now() + timedelta(days=14),
            "reason": "Personal matters",
            "status": LeaveStatus.PENDING
        }
    ]

    leave_count = 0
    for leave in leave_data:
        try:
            existing_leave = db.query(LeaveRequest).filter_by(
                employee_id=leave["employee_id"],
                type=leave["type"],
                start_date=leave["start_date"]
            ).first()

            if not existing_leave:
                create_leave_request(
                    db=db,
                    employee_id=leave["employee_id"],
                    type=leave["type"],
                    start_date=leave["start_date"],
                    end_date=leave["end_date"],
                    reason=leave["reason"],
                    status=leave["status"]
                )
                leave_count += 1
                print(f"✓ Created leave request: {leave['type']} ({leave['status'].value})")
            else:
                print(f"⚠ Leave request already exists: {leave['type']}")
        except Exception as e:
            print(f"✗ Error creating leave request '{leave['type']}': {str(e)}")

    print(f"Sample leave requests creation completed. Created {leave_count} new requests.")

if __name__ == "__main__":
    db = next(get_db())
    create_sample_tasks(db)
