import pytest
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from app.models.attendance import Attendance
from app.models.user import User
from app.models.company import Company
from app.crud import create_attendance, get_attendance_records

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
def test_user(db_session: Session, test_company: Company):
    user = User(
        email="employee@test.com",
        hashed_password="hashedpass",
        full_name="Test Employee",
        role="EMPLOYEE",
        company_id=test_company.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_create_attendance_record(db_session: Session, test_user: User):
    check_in_time = datetime.combine(date.today(), time(9, 0))
    check_out_time = datetime.combine(date.today(), time(17, 0))

    attendance = create_attendance(
        db=db_session,
        user_id=test_user.id,
        check_in=check_in_time,
        check_out=check_out_time,
        company_id=test_user.company_id
    )

    assert attendance.user_id == test_user.id
    assert attendance.check_in == check_in_time
    assert attendance.check_out == check_out_time
    assert attendance.company_id == test_user.company_id

def test_get_attendance_records(db_session: Session, test_user: User):
    # Create multiple attendance records
    dates = [date.today(), date.today().replace(day=date.today().day - 1)]
    for attendance_date in dates:
        check_in_time = datetime.combine(attendance_date, time(9, 0))
        check_out_time = datetime.combine(attendance_date, time(17, 0))
        create_attendance(
            db=db_session,
            user_id=test_user.id,
            check_in=check_in_time,
            check_out=check_out_time,
            company_id=test_user.company_id
        )

    # Retrieve records
    records = get_attendance_records(
        db=db_session,
        user_id=test_user.id,
        company_id=test_user.company_id,
        start_date=dates[1],
        end_date=dates[0]
    )

    assert len(records) == 2
    assert all(record.user_id == test_user.id for record in records)

def test_calculate_work_hours(db_session: Session, test_user: User):
    check_in_time = datetime.combine(date.today(), time(9, 0))
    check_out_time = datetime.combine(date.today(), time(17, 30))  # 8.5 hours

    attendance = create_attendance(
        db=db_session,
        user_id=test_user.id,
        check_in=check_in_time,
        check_out=check_out_time,
        company_id=test_user.company_id
    )

    # Calculate hours worked
    hours_worked = (attendance.check_out - attendance.check_in).total_seconds() / 3600
    assert hours_worked == 8.5

def test_attendance_validation(db_session: Session, test_user: User):
    # Test invalid check-out before check-in
    check_in_time = datetime.combine(date.today(), time(17, 0))
    check_out_time = datetime.combine(date.today(), time(9, 0))

    with pytest.raises(ValueError):
        create_attendance(
            db=db_session,
            user_id=test_user.id,
            check_in=check_in_time,
            check_out=check_out_time,
            company_id=test_user.company_id
        )

def test_bulk_attendance_creation(db_session: Session, test_user: User):
    # Create attendance for a week
    import random
    records_created = 0

    for i in range(7):
        attendance_date = date.today().replace(day=date.today().day - i)
        # Random check-in between 8-10 AM
        check_in_hour = random.randint(8, 10)
        check_in_time = datetime.combine(attendance_date, time(check_in_hour, 0))

        # Random check-out between 4-6 PM
        check_out_hour = random.randint(16, 18)
        check_out_time = datetime.combine(attendance_date, time(check_out_hour, 0))

        create_attendance(
            db=db_session,
            user_id=test_user.id,
            check_in=check_in_time,
            check_out=check_out_time,
            company_id=test_user.company_id
        )
        records_created += 1

    # Verify all records were created
    records = get_attendance_records(
        db=db_session,
        user_id=test_user.id,
        company_id=test_user.company_id,
        start_date=date.today().replace(day=date.today().day - 7),
        end_date=date.today()
    )

    assert len(records) == records_created
