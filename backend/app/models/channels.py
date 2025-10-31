from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db import Base

class ChannelType(str, PyEnum):
    DIRECT = "DIRECT"
    GROUP = "GROUP"
    PUBLIC = "PUBLIC"

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ChannelType), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_message_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="channels")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_channels")
    members = relationship("User", secondary="channel_members", overlaps="channel_memberships")
    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")
    channel_members = relationship("ChannelMember", back_populates="channel", cascade="all, delete-orphan", overlaps="members")

class ChannelMember(Base):
    __tablename__ = "channel_members"

    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, server_default=func.now())

    channel = relationship("Channel", back_populates="channel_members", overlaps="members")
    user = relationship("User", back_populates="channel_memberships", overlaps="members")
