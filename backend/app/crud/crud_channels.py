import structlog
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.channels import Channel, ChannelMember, ChannelType
from app.models.user import User
from app.models.company import Company
from app.models.company_department import CompanyDepartment
from app.models.company_team import CompanyTeam

logger = structlog.get_logger(__name__)

def create_channel(db: Session, name: str, type: ChannelType, company_id: int, created_by: int, department_id: Optional[int] = None, team_id: Optional[int] = None) -> Channel:
    """Create a new channel"""
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise ValueError("Company not found")

    db_user = db.query(User).filter(User.id == created_by).first()
    if not db_user:
        raise ValueError("User not found")

    if department_id:
        db_dept = db.query(CompanyDepartment).filter(CompanyDepartment.id == department_id).first()
        if not db_dept or db_dept.company_id != company_id:
            raise ValueError("Invalid department")

    if team_id:
        db_team = db.query(CompanyTeam).filter(CompanyTeam.id == team_id).first()
        if not db_team:
            raise ValueError("Invalid team")
        db_dept = db.query(CompanyDepartment).filter(CompanyDepartment.id == db_team.department_id).first()
        if not db_dept or db_dept.company_id != company_id:
            raise ValueError("Invalid team")

    channel = Channel(
        name=name,
        type=type,
        company_id=company_id,
        created_by=created_by,
        department_id=department_id,
        team_id=team_id
    )
    db.add(channel)
    db.commit()
    db.refresh(channel)
    logger.info("Channel created", channel_id=channel.id, company_id=company_id)
    return channel

def get_channel(db: Session, channel_id: int, company_id: int) -> Optional[Channel]:
    """Get a channel by ID"""
    return db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.company_id == company_id
    ).first()

def get_channels_for_company(db: Session, company_id: int, user_id: Optional[int] = None) -> List[Channel]:
    """Get channels for a company, optionally filtered by user membership"""
    query = db.query(Channel).filter(Channel.company_id == company_id)
    
    if user_id:
        query = query.join(ChannelMember).filter(ChannelMember.user_id == user_id)
    
    return query.order_by(Channel.created_at.desc()).all()

def update_channel(db: Session, channel_id: int, name: Optional[str] = None) -> Channel:
    """Update channel name"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise ValueError("Channel not found")
    
    if name:
        channel.name = name
    
    db.commit()
    db.refresh(channel)
    logger.info("Channel updated", channel_id=channel_id)
    return channel

def delete_channel(db: Session, channel_id: int) -> bool:
    """Delete a channel"""
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return False
    
    db.delete(channel)
    db.commit()
    logger.info("Channel deleted", channel_id=channel_id)
    return True

def add_member_to_channel(db: Session, channel_id: int, user_id: int) -> ChannelMember:
    """Add user to channel"""
    member = ChannelMember(
        channel_id=channel_id,
        user_id=user_id
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    logger.info("Member added to channel", channel_id=channel_id, user_id=user_id)
    return member

def remove_member_from_channel(db: Session, channel_id: int, user_id: int) -> bool:
    """Remove user from channel"""
    member = db.query(ChannelMember).filter(
        ChannelMember.channel_id == channel_id,
        ChannelMember.user_id == user_id
    ).first()
    if not member:
        return False
    
    db.delete(member)
    db.commit()
    logger.info("Member removed from channel", channel_id=channel_id, user_id=user_id)
    return True

def is_user_member_of_channel(db: Session, channel_id: int, user_id: int) -> bool:
    """Check if user is member of channel"""
    member = db.query(ChannelMember).filter(
        ChannelMember.channel_id == channel_id,
        ChannelMember.user_id == user_id
    ).first()
    return bool(member)
