import structlog
from sqlalchemy.orm import Session
from typing import List
from ..models.message_reactions import MessageReaction
from ..models.chat import ChatMessage

logger = structlog.get_logger(__name__)

def add_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> MessageReaction:
    """Add a reaction to a message"""
    # Check if message exists
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise ValueError("Message not found")

    # Check if reaction already exists
    existing = db.query(MessageReaction).filter(
        MessageReaction.message_id == message_id,
        MessageReaction.user_id == user_id,
        MessageReaction.emoji == emoji
    ).first()
    if existing:
        return existing

    reaction = MessageReaction(
        message_id=message_id,
        user_id=user_id,
        emoji=emoji
    )
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    logger.info("Reaction added", message_id=message_id, user_id=user_id, emoji=emoji)
    return reaction

def remove_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> bool:
    """Remove a reaction from a message"""
    reaction = db.query(MessageReaction).filter(
        MessageReaction.message_id == message_id,
        MessageReaction.user_id == user_id,
        MessageReaction.emoji == emoji
    ).first()
    if not reaction:
        return False
    
    db.delete(reaction)
    db.commit()
    logger.info("Reaction removed", message_id=message_id, user_id=user_id, emoji=emoji)
    return True

def get_reactions_for_message(db: Session, message_id: int) -> List[MessageReaction]:
    """Get all reactions for a message"""
    return db.query(MessageReaction).filter(
        MessageReaction.message_id == message_id
    ).order_by(MessageReaction.created_at).all()

def get_reaction_counts(db: Session, message_id: int) -> dict:
    """Get reaction counts grouped by emoji"""
    reactions = get_reactions_for_message(db, message_id)
    counts = {}
    for reaction in reactions:
        emoji = reaction.emoji
        counts[emoji] = counts.get(emoji, 0) + 1
    return counts
