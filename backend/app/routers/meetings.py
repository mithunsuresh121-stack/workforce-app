from datetime import datetime
from typing import List, Optional

import structlog
from fastapi import (APIRouter, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect)
from sqlalchemy.orm import Session

from app.core.rbac import RBACService, require_meeting_access
from app.crud.crud_meetings import (add_participant_to_meeting, create_meeting,
                                    get_meeting, get_meeting_participants,
                                    get_meetings_for_company,
                                    is_user_participant)
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.schemas import (MeetingCreate, MeetingParticipantResponse,
                                 MeetingResponse)
from app.services.meeting_service import meeting_service
from app.services.redis_service import redis_service

logger = structlog.get_logger(__name__)

router = APIRouter()

# WebRTC signaling connections
meeting_connections: dict = {}  # meeting_id -> {user_id: websocket}


@router.websocket("/ws/{meeting_id}/{user_id}")
async def meeting_websocket_endpoint(
    websocket: WebSocket, meeting_id: int, user_id: int, db: Session = Depends(get_db)
):
    """WebRTC signaling WebSocket for meetings"""
    await websocket.accept()

    if meeting_id not in meeting_connections:
        meeting_connections[meeting_id] = {}
    meeting_connections[meeting_id][user_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            # Handle WebRTC signaling
            if data.get("type") in ["offer", "answer", "ice-candidate"]:
                # Forward to other participants
                for participant_id, conn in meeting_connections[meeting_id].items():
                    if participant_id != user_id:
                        await conn.send_json(
                            {
                                "type": data["type"],
                                "from": user_id,
                                "data": data.get("data"),
                            }
                        )
    except WebSocketDisconnect:
        if (
            meeting_id in meeting_connections
            and user_id in meeting_connections[meeting_id]
        ):
            del meeting_connections[meeting_id][user_id]
            if not meeting_connections[meeting_id]:
                del meeting_connections[meeting_id]


@router.post("/create", response_model=MeetingResponse)
def create_new_meeting(
    meeting: MeetingCreate,
    team_id: Optional[int] = None,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new meeting"""
    try:
        # Check RBAC permissions for creating meeting
        if not RBACService.can_create_meeting(current_user, team_id, department_id):
            from app.services.audit_service import AuditService

            AuditService.log_permission_denied(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id,
                action="create_meeting",
                resource_type="meeting",
                details={"team_id": team_id, "department_id": department_id},
            )
            raise HTTPException(
                status_code=403,
                detail="Not authorized to create meetings in this scope",
            )

        # Cross-org block for participants
        if meeting.participant_ids:
            for participant_id in meeting.participant_ids:
                participant = db.query(User).filter(User.id == participant_id).first()
                if participant and not RBACService.can_invite_to_meeting(
                    current_user, None, participant
                ):
                    from app.services.audit_service import AuditService

                    AuditService.log_permission_denied(
                        db=db,
                        user_id=current_user.id,
                        company_id=current_user.company_id,
                        action="invite_cross_org_participant",
                        resource_type="meeting",
                        details={
                            "participant_id": participant_id,
                            "participant_company_id": participant.company_id,
                        },
                    )
                    raise HTTPException(
                        status_code=403,
                        detail="Cannot invite participants from other organizations",
                    )

        db_meeting = meeting_service.create_meeting(
            db=db,
            title=meeting.title,
            organizer_id=current_user.id,
            company_id=current_user.company_id,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            participant_ids=meeting.participant_ids,
            team_id=team_id,
            department_id=department_id,
        )

        # Audit log invites
        if meeting.participant_ids:
            from app.services.audit_service import AuditService

            for participant_id in meeting.participant_ids:
                AuditService.log_user_invited(
                    db=db,
                    user_id=current_user.id,
                    target_user_id=participant_id,
                    company_id=current_user.company_id,
                    resource_type="meeting",
                    resource_id=db_meeting.id,
                )

        logger.info(
            "Meeting created via API",
            meeting_id=db_meeting.id,
            organizer_id=current_user.id,
        )
        return MeetingResponse.from_orm(db_meeting)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create meeting", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to create meeting")


@router.get("/", response_model=List[MeetingResponse])
def get_user_meetings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get meetings for current user"""
    try:
        meetings = meeting_service.get_meetings_for_user(
            current_user.id, current_user.company_id, db
        )
        return [MeetingResponse.from_orm(m) for m in meetings]
    except Exception as e:
        logger.error("Failed to get meetings", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to get meetings")


@router.post("/{meeting_id}/join")
def join_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a meeting"""
    try:
        # Check RBAC access
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        if not RBACService.can_join_meeting(current_user, meeting):
            from app.services.audit_service import AuditService

            AuditService.log_permission_denied(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id,
                action="join_meeting",
                resource_type="meeting",
                resource_id=meeting_id,
                details={"meeting_company_id": meeting.company_id},
            )
            raise HTTPException(status_code=403, detail="Access denied to this meeting")

        if not is_user_participant(db, meeting_id, current_user.id):
            raise HTTPException(status_code=403, detail="Not invited to this meeting")

        participant = meeting_service.join_meeting(db, meeting_id, current_user.id)
        return {"status": "success", "participant_id": participant.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to join meeting", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to join meeting")


@router.post("/{meeting_id}/end")
def end_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End a meeting (organizer only)"""
    try:
        meeting_service.end_meeting(db, meeting_id, current_user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error("Failed to end meeting", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to end meeting")


@router.get(
    "/{meeting_id}/participants", response_model=List[MeetingParticipantResponse]
)
def get_meeting_participants_list(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get participants for a meeting"""
    try:
        if not is_user_participant(db, meeting_id, current_user.id):
            raise HTTPException(
                status_code=403, detail="Not a participant in this meeting"
            )

        participants = meeting_service.get_meeting_participants(db, meeting_id)
        return [MeetingParticipantResponse.from_orm(p) for p in participants]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get participants", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to get participants")


@router.get("/{meeting_id}/online")
async def get_online_participants(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get online participants for a meeting"""
    try:
        if not is_user_participant(db, meeting_id, current_user.id):
            raise HTTPException(
                status_code=403, detail="Not a participant in this meeting"
            )

        online_users = await meeting_service.get_online_participants(
            meeting_id, current_user.company_id
        )
        return {"online_participants": online_users}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get online participants", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to get online participants")
