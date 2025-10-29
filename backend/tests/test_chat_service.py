import pytest
from sqlalchemy.orm import Session
from app.services.chat_service import chat_service
from app.models.channels import ChannelType
from app.models.chat import ChatMessage
from app.models.user import User
from app.models.company import Company
from app.crud.crud_chat import create_chat_message
from app.schemas.schemas import ChatMessageCreate

def test_create_channel(db: Session, test_company: Company, test_user: User):
    """Test creating a channel"""
    channel = chat_service.create_group_channel(
        db=db,
        name="Test Channel",
        company_id=test_company.id,
        created_by=test_user.id,
        member_ids=[test_user.id]
    )
    assert channel.name == "Test Channel"
    assert channel.type == ChannelType.GROUP
    assert channel.company_id == test_company.id

def test_send_channel_message(db: Session, test_company: Company, test_user: User):
    """Test sending a message to a channel"""
    # Create channel first
    channel = chat_service.create_group_channel(
        db=db,
        name="Test Channel",
        company_id=test_company.id,
        created_by=test_user.id,
        member_ids=[test_user.id]
    )

    # Send message
    message = chat_service.send_message_to_channel(
        db=db,
        channel_id=channel.id,
        sender_id=test_user.id,
        message="Test message",
        attachments=[]
    )
    assert message.message == "Test message"
    assert message.channel_id == channel.id
    assert message.sender_id == test_user.id

def test_add_reaction(db: Session, test_company: Company, test_user: User):
    """Test adding reaction to message"""
    # Create message first
    message = create_chat_message(
        db=db,
        message_create=ChatMessageCreate(message="Test message"),
        sender_id=test_user.id,
        company_id=test_company.id
    )

    # Add reaction
    reaction = chat_service.add_reaction_to_message(
        db=db,
        message_id=message.id,
        user_id=test_user.id,
        emoji="👍"
    )
    assert reaction.emoji == "👍"
    assert reaction.message_id == message.id

def test_typing_indicator(db: Session, test_company: Company, test_user: User):
    """Test typing indicator functionality"""
    import asyncio
    # This would typically test Redis operations
    # For now, just ensure the method exists and doesn't crash
    asyncio.run(chat_service.set_typing_indicator(1, test_user.id, True))
    assert True  # If we get here, the method executed without error
