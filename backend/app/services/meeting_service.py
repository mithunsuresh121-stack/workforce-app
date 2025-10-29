import structlog
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..models.meetings import Meeting, MeetingStatus
from ..models.meeting_participants import MeetingParticipant, ParticipantRole
from ..crud.crud_meetings import create_meeting, add_participant_to_meeting, update_participant_join_time
from ..services.fcm_service import fcm_service
from ..crud_notifications import create_notification
from ..models.notification import NotificationType
from ..services.redis_service import redis_service

logger = structlog.get_logger(__name__)

class MeetingService:
    def __init__(self):
        pass

    def create_meeting(self, db: Session, title: str, organizer_id: int, company_id: int, start_time: datetime, end_time: datetime, participant_ids: List[int]) -> Meeting:
        """Create a new meeting and invite participants"""
        meeting = create_meeting(db, title, organizer_id, company_id, start_time, end_time)

        # Add organizer as participant
        add_participant_to_meeting(db, meeting.id, organizer_id, ParticipantRole.ORGANIZER)

        # Add other participants
        for participant_id in participant_ids:
            add_participant_to_meeting(db, meeting.id, participant_id, ParticipantRole.PARTICIPANT)
            # Send FCM notification
            self._send_meeting_invite(db, meeting, participant_id)

        logger.info("Meeting created", meeting_id=meeting.id, company_id=company_id, participant_count=len(participant_ids) + 1)
        return meeting

    def join_meeting(self, db: Session, meeting_id: int, user_id: int) -> MeetingParticipant:
        """User joins the meeting"""
        participant = update_participant_join_time(db, meeting_id, user_id, datetime.utcnow())

        # Update meeting status if needed
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting and meeting.status == MeetingStatus.SCHEDULED and meeting.start_time <= datetime.utcnow():
            meeting.status = MeetingStatus.ACTIVE
            db.commit()

        # Mark user as online in Redis for presence
        import asyncio
        asyncio.create_task(redis_service.set_user_online(meeting.company_id, user_id))

        logger.info("User joined meeting", meeting_id=meeting_id, user_id=user_id)
        return participant

    def end_meeting(self, db: Session, meeting_id: int, user_id: int):
        """End the meeting (organizer only)"""
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting or meeting.organizer_id != user_id:
            raise ValueError("Only organizer can end the meeting")

        meeting.status = MeetingStatus.ENDED
        meeting.end_time = datetime.utcnow()

        # Update leave times for all participants
        db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.leave_time.is_(None)
        ).update({"leave_time": datetime.utcnow()})

        db.commit()
        logger.info("Meeting ended", meeting_id=meeting_id, organizer_id=user_id)

    def get_meetings_for_user(self, db: Session, user_id: int, company_id: int) -> List[Meeting]:
        """Get all meetings for a user"""
        meetings = db.query(Meeting).join(MeetingParticipant).filter(
            Meeting.company_id == company_id,
            MeetingParticipant.user_id == user_id
        ).order_by(Meeting.start_time.desc()).all()
        return meetings

    def get_meeting_participants(self, db: Session, meeting_id: int) -> List[MeetingParticipant]:
        """Get participants for a meeting"""
        participants = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id
        ).all()
        return participants

    async def get_online_participants(self, meeting_id: int, company_id: int) -> List[int]:
        """Get online participants for a meeting"""
        # Filter online users who are participants in this meeting
        online_users = await redis_service.get_online_users(company_id)
        # In production, cross-reference with meeting participants
        # For now, return all online users in company (simplified)
        return online_users

    async def leave_meeting(self, db: Session, meeting_id: int, user_id: int):
        """User leaves the meeting"""
        participant = db.query(MeetingParticipant).filter(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.user_id == user_id
        ).first()
        if participant and not participant.leave_time:
            participant.leave_time = datetime.utcnow()
            db.commit()

            # Mark user offline in Redis
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                await redis_service.set_user_offline(meeting.company_id, user_id)

                # Publish leave event
                await redis_service.publish_event(f"meeting:{meeting_id}", {
                    "type": "user_left",
                    "user_id": user_id,
                    "meeting_id": meeting_id
                })

            logger.info("User left meeting", meeting_id=meeting_id, user_id=user_id)
            return True
        return False

    def _send_meeting_invite(self, db: Session, meeting: Meeting, user_id: int):
        """Send meeting invite notification"""
        create_notification(
            db=db,
            user_id=user_id,
            company_id=meeting.company_id,
            title=f"Meeting invitation: {meeting.title}",
            message=f"You're invited to a meeting on {meeting.start_time.strftime('%Y-%m-%d %H:%M')}",
            type=NotificationType.MEETING_INVITE
        )

        # Send FCM push notification with deep link
        fcm_service.send_meeting_invite(db, user_id, meeting.id, meeting.title)

# Global meeting service instance
meeting_service = MeetingService()
