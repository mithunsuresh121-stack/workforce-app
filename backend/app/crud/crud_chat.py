import structlog
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.chat import ChatMessage
from app.schemas.schemas import ChatMessageCreate
from app.models.user import User
from app.models.company import Company
from app.models.channels import Channel, ChannelMember

logger = structlog.get_logger(__name__)

def create_chat_message(db: Session, message_create: ChatMessageCreate, sender_id: int, company_id: int, channel_id: Optional[int] = None) -> ChatMessage:
    """Create a new chat message"""
    db_message = ChatMessage(
        company_id=company_id,
        sender_id=sender_id,
        receiver_id=message_create.receiver_id if not channel_id else None,
        channel_id=channel_id,
        message=message_create.message,
        attachments=getattr(message_create, 'attachments', []),
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    logger.info("Chat message created", message_id=db_message.id, sender_id=sender_id, company_id=company_id)
    return db_message

def get_chat_history(db: Session, sender_id: int, company_id: int, receiver_id: Optional[int] = None, channel_id: Optional[int] = None, limit: int = 50) -> List[ChatMessage]:
    """Get chat history between two users, in a channel, or company-wide"""
    query = db.query(ChatMessage).filter(ChatMessage.company_id == company_id)
    
    if channel_id:
        query = query.filter(ChatMessage.channel_id == channel_id)
    elif receiver_id:
        # Between two users (direct messages)
        query = query.filter(
            ((ChatMessage.sender_id == sender_id) & (ChatMessage.receiver_id == receiver_id)) |
            ((ChatMessage.sender_id == receiver_id) & (ChatMessage.receiver_id == sender_id))
        )
    else:
        # Company-wide messages (no receiver or channel)
        query = query.filter(ChatMessage.receiver_id.is_(None), ChatMessage.channel_id.is_(None))
    
    return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()

def get_channel_messages(db: Session, channel_id: int, company_id: int, limit: int = 50) -> List[ChatMessage]:
    """Get messages for a specific channel"""
    return db.query(ChatMessage).filter(
        ChatMessage.channel_id == channel_id,
        ChatMessage.company_id == company_id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

def mark_message_as_read(db: Session, message_id: int, user_id: int) -> Optional[ChatMessage]:
    """Mark a chat message as read for direct or channel messages"""
    subquery = db.query(ChannelMember).filter(
        ChannelMember.channel_id == ChatMessage.channel_id,
        ChannelMember.user_id == user_id
    ).exists()
    
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        (
            (ChatMessage.receiver_id == user_id) |
            (ChatMessage.channel_id.isnot(None) & subquery)
        )
    ).first()
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
        logger.info("Message marked as read", message_id=message_id, user_id=user_id)
    return message

def get_unread_count(db: Session, user_id: int, company_id: int, channel_id: Optional[int] = None) -> int:
    """Get unread chat messages count for user in direct messages or specific channel"""
    subquery = db.query(ChannelMember).filter(
        ChannelMember.channel_id == ChatMessage.channel_id,
        ChannelMember.user_id == user_id
    ).exists()
    
    query = db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.is_read == False
    )
    
    if channel_id:
        query = query.filter(ChatMessage.channel_id == channel_id)
    else:
        query = query.filter(
            (ChatMessage.receiver_id == user_id) |
            (ChatMessage.channel_id.isnot(None) & subquery)
        )
    
    return query.count()

def get_company_chat_messages(db: Session, company_id: int, limit: int = 50) -> List[ChatMessage]:
    """Get company-wide chat messages"""
    return db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.receiver_id.is_(None),
        ChatMessage.channel_id.is_(None)
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

def update_message(db: Session, message_id: int, user_id: int, new_message: str) -> Optional[ChatMessage]:
    """Update a chat message (only by sender)"""
    from datetime import datetime
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.sender_id == user_id
    ).first()
    if message:
        message.message = new_message
        message.edited_at = datetime.utcnow()
        db.commit()
        db.refresh(message)
        logger.info("Message updated", message_id=message_id, user_id=user_id)
    return message
