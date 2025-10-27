import structlog
from sqlalchemy.orm import Session
from typing import List, Optional
from .models.chat import ChatMessage
from .schemas.schemas import ChatMessageCreate
from .models.user import User
from .models.company import Company

logger = structlog.get_logger(__name__)

def create_chat_message(db: Session, message_create: ChatMessageCreate, sender_id: int, company_id: int) -> ChatMessage:
    """Create a new chat message"""
    db_message = ChatMessage(
        company_id=company_id,
        sender_id=sender_id,
        receiver_id=message_create.receiver_id,
        message=message_create.message,
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_history(db: Session, sender_id: int, receiver_id: Optional[int], company_id: int, limit: int = 50) -> List[ChatMessage]:
    """Get chat history between two users or company-wide"""
    query = db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id
    )
    
    if receiver_id:
        # Between two users
        query = query.filter(
            ((ChatMessage.sender_id == sender_id) & (ChatMessage.receiver_id == receiver_id)) |
            ((ChatMessage.sender_id == receiver_id) & (ChatMessage.receiver_id == sender_id))
        )
    else:
        # Company-wide messages
        query = query.filter(ChatMessage.receiver_id.is_(None))
    
    return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()

def mark_message_as_read(db: Session, message_id: int, user_id: int) -> Optional[ChatMessage]:
    """Mark a chat message as read"""
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id,
        ChatMessage.receiver_id == user_id
    ).first()
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
    return message

def get_unread_count(db: Session, user_id: int, company_id: int) -> int:
    """Get unread chat messages count for user"""
    return db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.receiver_id == user_id,
        ChatMessage.is_read == False
    ).count()

def get_company_chat_messages(db: Session, company_id: int, limit: int = 50) -> List[ChatMessage]:
    """Get company-wide chat messages"""
    return db.query(ChatMessage).filter(
        ChatMessage.company_id == company_id,
        ChatMessage.receiver_id.is_(None)
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
