import structlog
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..models.chat import ChatMessage
from ..models.channels import Channel, ChannelMember, ChannelType
from ..models.message_reactions import MessageReaction
from ..crud_chat import create_chat_message, get_chat_history
from ..crud.crud_channels import create_channel, add_member_to_channel
from ..crud.crud_reactions import add_reaction, remove_reaction
from ..services.redis_service import redis_service
from ..services.fcm_service import fcm_service
from ..crud_notifications import create_notification
from ..models.notification import NotificationType

logger = structlog.get_logger(__name__)

class ChatService:
    def __init__(self):
        pass

    def create_group_channel(self, db: Session, name: str, company_id: int, created_by: int, member_ids: List[int]) -> Channel:
        """Create a new group channel and add members"""
        channel = create_channel(db, name, ChannelType.GROUP, company_id, created_by)
        for member_id in member_ids:
            add_member_to_channel(db, channel.id, member_id)
        logger.info("Group channel created", channel_id=channel.id, company_id=company_id, member_count=len(member_ids))
        return channel

    def create_direct_channel(self, db: Session, user1_id: int, user2_id: int, company_id: int) -> Channel:
        """Create or get existing direct channel between two users"""
        # Check if direct channel already exists
        existing = db.query(Channel).filter(
            Channel.type == ChannelType.DIRECT,
            Channel.company_id == company_id,
            Channel.members.any(id=user1_id),
            Channel.members.any(id=user2_id)
        ).first()
        if existing:
            return existing

        name = f"Direct-{min(user1_id, user2_id)}-{max(user1_id, user2_id)}"
        channel = create_channel(db, name, ChannelType.DIRECT, company_id, user1_id)
        add_member_to_channel(db, channel.id, user1_id)
        add_member_to_channel(db, channel.id, user2_id)
        logger.info("Direct channel created", channel_id=channel.id, company_id=company_id)
        return channel

    def send_message_to_channel(self, db: Session, channel_id: int, sender_id: int, message: str, attachments: Optional[List[Dict[str, Any]]] = None) -> ChatMessage:
        """Send message to a channel"""
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            raise ValueError("Channel not found")

        # Check if sender is member
        is_member = db.query(ChannelMember).filter(
            ChannelMember.channel_id == channel_id,
            ChannelMember.user_id == sender_id
        ).first()
        if not is_member:
            raise ValueError("User is not a member of this channel")

        chat_message = ChatMessage(
            company_id=channel.company_id,
            sender_id=sender_id,
            channel_id=channel_id,
            message=message,
            attachments=attachments or []
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)

        # Create notifications for other members
        self._notify_channel_members(db, channel_id, sender_id, chat_message)

        logger.info("Message sent to channel", message_id=chat_message.id, channel_id=channel_id, sender_id=sender_id)
        return chat_message

    def get_channel_messages(self, db: Session, channel_id: int, user_id: int, limit: int = 50) -> List[ChatMessage]:
        """Get messages for a channel (user must be member)"""
        # Verify membership
        is_member = db.query(ChannelMember).filter(
            ChannelMember.channel_id == channel_id,
            ChannelMember.user_id == user_id
        ).first()
        if not is_member:
            raise ValueError("User is not a member of this channel")

        messages = db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

        return messages[::-1]  # Reverse to chronological order

    def add_reaction_to_message(self, db: Session, message_id: int, user_id: int, emoji: str) -> MessageReaction:
        """Add reaction to message"""
        return add_reaction(db, message_id, user_id, emoji)

    def remove_reaction_from_message(self, db: Session, message_id: int, user_id: int, emoji: str):
        """Remove reaction from message"""
        remove_reaction(db, message_id, user_id, emoji)

    async def get_typing_users(self, channel_id: int) -> List[int]:
        """Get users currently typing in channel"""
        return await redis_service.get_typing_users(channel_id)

    async def set_typing_indicator(self, channel_id: int, user_id: int):
        """Set typing indicator for user"""
        await redis_service.set_typing_indicator(channel_id, user_id)

    def mark_channel_messages_read(self, db: Session, channel_id: int, user_id: int):
        """Mark all messages in channel as read for user"""
        db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id,
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ).update({"is_read": True})
        db.commit()
        logger.info("Channel messages marked as read", channel_id=channel_id, user_id=user_id)

    def _notify_channel_members(self, db: Session, channel_id: int, sender_id: int, message: ChatMessage):
        """Send notifications to channel members (except sender)"""
        members = db.query(ChannelMember).filter(
            ChannelMember.channel_id == channel_id,
            ChannelMember.user_id != sender_id
        ).all()

        for member in members:
            create_notification(
                db=db,
                user_id=member.user_id,
                company_id=message.company_id,
                title=f"New message in {message.channel.name}",
                message=f"{message.sender.first_name}: {message.message[:50]}...",
                type=NotificationType.CHAT_MESSAGE
            )

# Global chat service instance
chat_service = ChatService()
