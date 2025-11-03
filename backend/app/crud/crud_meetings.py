import structlog
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models.meetings import Meeting, MeetingStatus
from app.models.meeting_participants import MeetingParticipant, ParticipantRole
from app.models.user import User
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam

logger = structlog.get_logger(__name__)

def create_meeting(db: Session, title: str, organizer_id: int, company_id: int, start_time: datetime, end_time: datetime, department_id: Optional[int] = None, team_id: Optional[int] = None) -> Meeting:
    """Create a new meeting"""
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise ValueError("Company not found")

    db_user = db.query(User).filter(User.id == organizer_id).first()
    if not db_user:
        raise ValueError("Organizer not found")

    if department_id:
        db_dept = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
        if not db_dept or db_dept.company_id != company_id:
            raise ValueError("Invalid department")

    if team_id:
        db_team = db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()
        if not db_team:
            raise ValueError("Invalid team")
        db_dept = db.query(CompanyDepartment).filter(CompanyDepartment.id == db_team.department_id).first()
        if not db_dept or db_dept.company_id != company_id:
            raise ValueError("Invalid team")

    meeting = Meeting(
        title=title,
        organizer_id=organizer_id,
        company_id=company_id,
        start_time=start_time,
        end_time=end_time,
        status=MeetingStatus.SCHEDULED,
        department_id=department_id,
        team_id=team_id
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    logger.info("Meeting created", meeting_id=meeting.id, organizer_id=organizer_id, company_id=company_id)
    return meeting

def get_meeting(db: Session, meeting_id: int, company_id: int) -> Optional[Meeting]:
    """Get a meeting by ID"""
    return db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.company_id == company_id
    ).first()

def get_meetings_for_company(db: Session, company_id: int) -> List[Meeting]:
    """Get all meetings for a company"""
    return db.query(Meeting).filter(
        Meeting.company_id == company_id
    ).order_by(Meeting.start_time.desc()).all()

def update_meeting_status(db: Session, meeting_id: int, status: MeetingStatus) -> Meeting:
    """Update meeting status"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise ValueError("Meeting not found")
    
    meeting.status = status
    db.commit()
    db.refresh(meeting)
    logger.info("Meeting status updated", meeting_id=meeting_id, status=status.value)
    return meeting

def add_participant_to_meeting(db: Session, meeting_id: int, user_id: int, role: ParticipantRole) -> MeetingParticipant:
    """Add participant to meeting"""
    participant = MeetingParticipant(
        meeting_id=meeting_id,
        user_id=user_id,
        role=role
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    logger.info("Participant added to meeting", meeting_id=meeting_id, user_id=user_id, role=role.value)
    return participant

def update_participant_join_time(db: Session, meeting_id: int, user_id: int, join_time: datetime) -> MeetingParticipant:
    """Update participant's join time"""
    participant = db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id,
        MeetingParticipant.user_id == user_id
    ).first()
    if not participant:
        raise ValueError("Participant not found")
    
    participant.join_time = join_time
    db.commit()
    db.refresh(participant)
    return participant

def update_participant_leave_time(db: Session, meeting_id: int, user_id: int, leave_time: datetime) -> MeetingParticipant:
    """Update participant's leave time"""
    participant = db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id,
        MeetingParticipant.user_id == user_id
    ).first()
    if not participant:
        raise ValueError("Participant not found")
    
    participant.leave_time = leave_time
    db.commit()
    db.refresh(participant)
    return participant

def get_meeting_participants(db: Session, meeting_id: int) -> List[MeetingParticipant]:
    """Get all participants for a meeting"""
    return db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id
    ).all()

def is_user_participant(db: Session, meeting_id: int, user_id: int) -> bool:
    """Check if user is a participant in the meeting"""
    participant = db.query(MeetingParticipant).filter(
        MeetingParticipant.meeting_id == meeting_id,
        MeetingParticipant.user_id == user_id
    ).first()
    return bool(participant)
