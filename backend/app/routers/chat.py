from typing import Any, Dict, List, Optional

import structlog
from fastapi import (APIRouter, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect)
from sqlalchemy.orm import Session

from app.core.rbac import require_channel_access
from app.crud import create_notification
from app.crud.crud_channels import (add_member_to_channel, create_channel,
                                    get_channels_for_company,
                                    is_user_member_of_channel)
from app.crud.crud_chat import (create_chat_message, get_channel_messages,
                                get_chat_history, get_unread_count,
                                mark_message_as_read)
from app.crud.crud_reactions import (add_reaction, get_reactions_for_message,
                                     remove_reaction)
from app.db import get_db
from app.deps import get_current_user
from app.models.company import Company
from app.models.notification import NotificationType
from app.models.user import User
from app.schemas.schemas import (ChannelCreate, ChannelResponse,
                                 ChatMessageCreate, ChatMessageResponse,
                                 ChatMessageUpdate, ReactionCreate)
from app.services.chat_service import chat_service
from app.services.fcm_service import fcm_service
from app.services.redis_service import redis_service

logger = structlog.get_logger(__name__)

router = APIRouter()

# WebSocket connections for real-time chat
active_connections: Dict[int, List[WebSocket]] = {}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, user_id: int, db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)

    # Set user online
    await redis_service.set_user_online(1, user_id)  # TODO: Get company_id from token

    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
            if data.get("type") == "typing":
                await chat_service.handle_typing_indicator(
                    user_id, data.get("is_typing", False)
                )
            elif data.get("type") == "message":
                # Create message and broadcast
                message_data = data.get("message")
                message = create_chat_message(
                    db=db,
                    message_create=ChatMessageCreate(**message_data),
                    sender_id=user_id,
                    company_id=1,  # TODO: Get from token
                    channel_id=message_data.get("channel_id"),
                    attachments=message_data.get("attachments"),
                )
                await broadcast_message(message, db)
    except WebSocketDisconnect:
        active_connections[user_id].remove(websocket)
        if not active_connections[user_id]:
            del active_connections[user_id]
        # Set user offline
        await redis_service.set_user_offline(1, user_id)


async def broadcast_message(message, db: Session):
    """Broadcast message to relevant users"""
    # Get recipients based on message type
    recipients = []
    if message.channel_id:
        # Channel message - get all channel members
        from app.crud.crud_channels import get_channel_members

        recipients = [m.user_id for m in get_channel_members(db, message.channel_id)]
    elif message.receiver_id:
        # Direct message
        recipients = [message.receiver_id]
    else:
        # Company-wide
        recipients = []  # TODO: Get all company users

    for recipient_id in recipients:
        if recipient_id in active_connections:
            for connection in active_connections[recipient_id]:
                await connection.send_json(
                    {
                        "type": "message",
                        "message": {
                            "id": message.id,
                            "sender_id": message.sender_id,
                            "message": message.message,
                            "attachments": message.attachments,
                            "created_at": message.created_at.isoformat(),
                        },
                    }
                )


@router.post("/messages/send", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    channel_id: Optional[int] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a chat message"""
    try:
        # Cross-org block for direct messages
        if message.receiver_id:
            receiver = db.query(User).filter(User.id == message.receiver_id).first()
            if not receiver:
                raise HTTPException(status_code=404, detail="Receiver not found")
            if not RBACService.can_send_cross_org_message(current_user, receiver):
                from app.services.audit_service import AuditService

                AuditService.log_permission_denied(
                    db=db,
                    user_id=current_user.id,
                    company_id=current_user.company_id,
                    action="send_cross_org_dm",
                    resource_type="user",
                    resource_id=message.receiver_id,
                    details={"receiver_company_id": receiver.company_id},
                )
                raise HTTPException(
                    status_code=403, detail="Cannot send messages across organizations"
                )

        # Validate channel membership if channel message
        if channel_id and not is_user_member_of_channel(
            db, channel_id, current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not a member of this channel")

        chat_message = create_chat_message(
            db=db,
            message_create=message,
            sender_id=current_user.id,
            company_id=current_user.company_id,
            channel_id=channel_id,
            attachments=attachments,
        )

        # Send FCM notification if direct message
        if message.receiver_id and message.receiver_id != current_user.id:
            fcm_service.send_chat_message(
                db, current_user.id, message.receiver_id, message.message
            )

        # Create in-app notification
        if message.receiver_id:
            create_notification(
                db=db,
                user_id=message.receiver_id,
                company_id=current_user.company_id,
                title=f"New message from {current_user.first_name}",
                message=(
                    message.message[:100] + "..."
                    if len(message.message) > 100
                    else message.message
                ),
                type=NotificationType.CHAT_MESSAGE,
            )

        logger.info(
            "Message sent", message_id=chat_message.id, sender_id=current_user.id
        )
        return ChatMessageResponse.from_orm(chat_message)
    except Exception as e:
        logger.error("Failed to send message", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/messages/history", response_model=List[ChatMessageResponse])
def get_message_history(
    receiver_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat message history"""
    try:
        messages = get_chat_history(
            db=db,
            sender_id=current_user.id,
            receiver_id=receiver_id,
            company_id=current_user.company_id,
            channel_id=channel_id,
            limit=limit,
        )
        return [ChatMessageResponse.from_orm(msg) for msg in messages]
    except Exception as e:
        logger.error(
            "Failed to get message history", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to get message history")


@router.post("/messages/{message_id}/read")
def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark message as read"""
    try:
        message = mark_message_as_read(db, message_id, current_user.id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return {"status": "success"}
    except Exception as e:
        logger.error(
            "Failed to mark message as read", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to mark message as read")


@router.get("/messages/unread/count")
def get_unread_message_count(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get unread message count"""
    try:
        count = get_unread_count(db, current_user.id, current_user.company_id)
        return {"unread_count": count}
    except Exception as e:
        logger.error(
            "Failed to get unread count", error=str(e), user_id=current_user.id
        )
        raise HTTPException(status_code=500, detail="Failed to get unread count")


@router.post("/channels/create", response_model=ChannelResponse)
def create_new_channel(
    channel: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new channel"""
    try:
        db_channel = create_channel(
            db=db,
            name=channel.name,
            type=channel.type,
            company_id=current_user.company_id,
            created_by=current_user.id,
        )

        # Add creator as member
        add_member_to_channel(db, db_channel.id, current_user.id)

        logger.info(
            "Channel created", channel_id=db_channel.id, creator_id=current_user.id
        )
        return ChannelResponse.from_orm(db_channel)
    except Exception as e:
        logger.error("Failed to create channel", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to create channel")


@router.get("/channels", response_model=List[ChannelResponse])
def get_channels(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get channels for company"""
    try:
        channels = get_channels_for_company(
            db, current_user.company_id, current_user.id
        )
        return [ChannelResponse.from_orm(ch) for ch in channels]
    except Exception as e:
        logger.error("Failed to get channels", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to get channels")


@router.post("/channels/{channel_id}/join")
def join_channel(
    channel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a channel"""
    try:
        # Check RBAC access
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        if not RBACService.can_join_channel(current_user, channel):
            from app.services.audit_service import AuditService

            AuditService.log_permission_denied(
                db=db,
                user_id=current_user.id,
                company_id=current_user.company_id,
                action="join_channel",
                resource_type="channel",
                resource_id=channel_id,
                details={"channel_company_id": channel.company_id},
            )
            raise HTTPException(status_code=403, detail="Access denied to this channel")

        add_member_to_channel(db, channel_id, current_user.id)
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to join channel", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to join channel")


@router.post("/messages/{message_id}/reactions", response_model=dict)
def add_message_reaction(
    message_id: int,
    reaction: ReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add reaction to message"""
    try:
        db_reaction = add_reaction(db, message_id, current_user.id, reaction.emoji)
        return {"status": "success", "reaction_id": db_reaction.id}
    except Exception as e:
        logger.error("Failed to add reaction", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to add reaction")


@router.delete("/messages/{message_id}/reactions/{emoji}")
def remove_message_reaction(
    message_id: int,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove reaction from message"""
    try:
        success = remove_reaction(db, message_id, current_user.id, emoji)
        if not success:
            raise HTTPException(status_code=404, detail="Reaction not found")
        return {"status": "success"}
    except Exception as e:
        logger.error("Failed to remove reaction", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to remove reaction")


@router.get("/messages/{message_id}/reactions")
def get_message_reactions(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get reactions for message"""
    try:
        reactions = get_reactions_for_message(db, message_id)
        return {
            "reactions": [{"emoji": r.emoji, "user_id": r.user_id} for r in reactions]
        }
    except Exception as e:
        logger.error("Failed to get reactions", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to get reactions")


@router.put("/messages/{message_id}", response_model=ChatMessageResponse)
def update_message(
    message_id: int,
    message_update: ChatMessageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a chat message"""
    try:
        from app.crud.crud_chat import update_message as crud_update_message

        updated_message = crud_update_message(
            db, message_id, current_user.id, message_update.message
        )
        if not updated_message:
            raise HTTPException(
                status_code=404, detail="Message not found or not authorized to edit"
            )
        return ChatMessageResponse.from_orm(updated_message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update message", error=str(e), user_id=current_user.id)
        raise HTTPException(status_code=500, detail="Failed to update message")
