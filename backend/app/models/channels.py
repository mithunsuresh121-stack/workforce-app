from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from ..db import Base

class ChannelType(str, PyEnum):
    DIRECT = "DIRECT"
    GROUP = "GROUP"
    PUBLIC = "PUBLIC"

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ChannelType), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company")
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", secondary="channel_members")
    messages = relationship("ChatMessage", back_populates="channel")

class ChannelMember(Base):
    __tablename__ = "channel_members"

    channel_id = Column(Integer, ForeignKey("channels.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime, server_default=func.now())

    channel = relationship("Channel")
    user = relationship("User")
