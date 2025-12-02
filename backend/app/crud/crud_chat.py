from typing import Dict, List, Optional

import structlog
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.channels import Channel, ChannelMember
from app.models.chat import ChatMessage
from app.models.company import Company
from app.models.message_reactions import MessageReaction
from app.models.user import User
from app.schemas.schemas import ChatMessageCreate

logger = structlog.get_logger(__name__)


def create_chat_message(
    db: Session,
    channel_id: int,
    sender_id: int,
    text: str,
    attachments: Optional[List[Dict]] = None,
    company_id: Optional[int] = None,
) -> Dict:
    """Create a new chat message in a channel"""
    if company_id is None:
        user = db.query(User).filter(User.id == sender_id).first()
        if not user:
            raise ValueError("Sender not found")
        company_id = user.company_id

    db_message = ChatMessage(
        company_id=company_id,
        sender_id=sender_id,
        channel_id=channel_id,
        message=text,
        attachments=attachments or [],
        is_read=False,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    logger.info(
        "Chat message created",
        message_id=db_message.id,
        sender_id=sender_id,
        company_id=company_id,
        channel_id=channel_id,
    )
    return {
        "id": db_message.id,
        "sender_id": sender_id,
        "text": text,
        "attachments": attachments or [],
        "created_at": db_message.created_at,
        "reactions": [],
    }


def get_chat_history(
    db: Session,
    sender_id: int,
    company_id: int,
    receiver_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    limit: int = 50,
) -> List[ChatMessage]:
    """Get chat history between two users, in a channel, or company-wide"""
    query = db.query(ChatMessage).filter(ChatMessage.company_id == company_id)

    if channel_id:
        query = query.filter(ChatMessage.channel_id == channel_id)
    elif receiver_id:
        # Between two users (direct messages)
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
        # Company-wide messages (no receiver or channel)
        query = query.filter(
            ChatMessage.receiver_id.is_(None), ChatMessage.channel_id.is_(None)
        )

    return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()


def get_channel_messages(
    db: Session,
    channel_id: int,
    company_id: int,
    limit: int = 50,
    before: Optional[int] = None,
) -> List[Dict]:
    """Get messages for a specific channel with optional pagination"""
    query = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.channel_id == channel_id, ChatMessage.company_id == company_id
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )

    if before:
        query = query.filter(ChatMessage.id < before)

    messages = query.all()
    result = []
    for msg in messages:
        reactions = get_reactions_for_message(db, msg.id)
        result.append(
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "text": msg.message,
                "attachments": msg.attachments or [],
                "created_at": msg.created_at,
                "edited_at": msg.updated_at,  # Use updated_at as edited_at
                "reactions": reactions,
            }
        )
    return result


def mark_message_as_read(
    db: Session, message_id: int, user_id: int
) -> Optional[ChatMessage]:
    """Mark a chat message as read for direct or channel messages"""
    subquery = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == ChatMessage.channel_id,
            ChannelMember.user_id == user_id,
        )
        .exists()
    )

    message = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.id == message_id,
            (
                (ChatMessage.receiver_id == user_id)
                | (ChatMessage.channel_id.isnot(None) & subquery)
            ),
        )
        .first()
    )
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
        logger.info("Message marked as read", message_id=message_id, user_id=user_id)
    return message


def get_unread_count(
    db: Session, user_id: int, company_id: int, channel_id: Optional[int] = None
) -> int:
    """Get unread chat messages count for user in direct messages or specific channel"""
    subquery = (
        db.query(ChannelMember)
        .filter(
            ChannelMember.channel_id == ChatMessage.channel_id,
            ChannelMember.user_id == user_id,
        )
        .exists()
    )

    query = db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id, ChatMessage.is_read == False
    )

    if channel_id:
        query = query.filter(ChatMessage.channel_id == channel_id)
    else:
        query = query.filter(
            (ChatMessage.receiver_id == user_id)
            | (ChatMessage.channel_id.isnot(None) & subquery)
        )

    return query.count()


def get_company_chat_messages(
    db: Session, company_id: int, limit: int = 50
) -> List[ChatMessage]:
    """Get company-wide chat messages"""
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.company_id == company_id,
            ChatMessage.receiver_id.is_(None),
            ChatMessage.channel_id.is_(None),
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )


def update_message(
    db: Session, message_id: int, user_id: int, new_message: str
) -> Optional[ChatMessage]:
    """Update a chat message (only by sender)"""
    from datetime import datetime

    message = (
        db.query(ChatMessage)
        .filter(ChatMessage.id == message_id, ChatMessage.sender_id == user_id)
        .first()
    )
    if message:
        message.message = new_message
        message.updated_at = datetime.utcnow()  # Use updated_at as edited_at
        db.commit()
        db.refresh(message)
        logger.info("Message updated", message_id=message_id, user_id=user_id)
    return message


def add_reaction(
    db: Session, message_id: int, user_id: int, emoji: str
) -> MessageReaction:
    """Add a reaction to a message"""
    reaction = MessageReaction(message_id=message_id, user_id=user_id, emoji=emoji)
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    logger.info(
        "Reaction added",
        reaction_id=reaction.id,
        message_id=message_id,
        user_id=user_id,
        emoji=emoji,
    )
    return reaction


def get_reactions_for_message(db: Session, message_id: int) -> List[Dict]:
    """Get reactions for a message, grouped by emoji with counts and users"""
    reactions = (
        db.query(
            MessageReaction.emoji,
            func.count(MessageReaction.id).label("count"),
            func.group_concat(MessageReaction.user_id).label("users"),
        )
        .filter(MessageReaction.message_id == message_id)
        .group_by(MessageReaction.emoji)
        .all()
    )

    result = []
    for emoji, count, users_str in reactions:
        users = [int(u) for u in users_str.split(",") if u] if users_str else []
        result.append({"emoji": emoji, "count": count, "users": users})
    return result
