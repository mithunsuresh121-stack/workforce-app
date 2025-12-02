from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.orm import Session

from app.models.channels import Channel
from app.models.chat import ChatMessage
from app.models.company import Company
from app.models.user import User
from app.schemas.schemas import ChatMessageCreate

logger = structlog.get_logger(__name__)


def create_chat_message(
    db: Session,
    message_create: ChatMessageCreate,
    sender_id: int,
    company_id: int,
    channel_id: Optional[int] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> ChatMessage:
    """Create a new chat message"""
    db_message = ChatMessage(
        company_id=company_id,
        sender_id=sender_id,
        receiver_id=getattr(message_create, "receiver_id", None),
        channel_id=channel_id,
        message=message_create.message,
        attachments=attachments or [],
        is_read=False,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_history(
    db: Session,
    sender_id: int,
    receiver_id: Optional[int],
    company_id: int,
    channel_id: Optional[int] = None,
    limit: int = 50,
) -> List[ChatMessage]:
    """Get chat history between two users, channel, or company-wide"""
    query = db.query(ChatMessage).filter(ChatMessage.company_id == company_id)

    if channel_id:
        # Channel messages
        query = query.filter(ChatMessage.channel_id == channel_id)
    elif receiver_id:
        # Between two users
        query = query.filter(
            (
                (ChatMessage.sender_id == sender_id)
                & (ChatMessage.receiver_id == receiver_id)
            )
            | (
                (ChatMessage.sender_id == receiver_id)
                & (ChatMessage.receiver_id == sender_id)
            )
        )
    else:
        # Company-wide messages
        query = query.filter(
            ChatMessage.receiver_id.is_(None), ChatMessage.channel_id.is_(None)
        )

    return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()


def mark_message_as_read(
    db: Session, message_id: int, user_id: int
) -> Optional[ChatMessage]:
    """Mark a chat message as read"""
    message = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id, ChatMessage.receiver_id == user_id)
        .first()
    )
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
    return message


def get_unread_count(db: Session, user_id: int, company_id: int) -> int:
    """Get unread chat messages count for user"""
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.company_id == company_id,
            ChatMessage.receiver_id == user_id,
            ChatMessage.is_read == False,
        )
        .count()
    )


def get_channel_messages(
    db: Session, channel_id: int, company_id: int, limit: int = 50
) -> List[ChatMessage]:
    """Get messages for a specific channel"""
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.company_id == company_id, ChatMessage.channel_id == channel_id
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )


def get_company_chat_messages(
    db: Session, company_id: int, limit: int = 50
) -> List[ChatMessage]:
    """Get company-wide chat messages"""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.company_id == company_id, ChatMessage.receiver_id.is_(None))
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
