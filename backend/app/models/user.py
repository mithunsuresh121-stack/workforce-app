from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
from .refresh_token import RefreshToken

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="Employee")  # SuperAdmin, CompanyAdmin, Manager, Employee
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Nullable for Super Admin
    is_active = Column(Boolean, default=True)
    fcm_token = Column(String, nullable=True)  # Firebase Cloud Messaging token for push notifications
    last_active = Column(DateTime, nullable=True)  # Track user's last activity
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False, foreign_keys="[EmployeeProfile.user_id]", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    shifts = relationship("Shift", back_populates="employee", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    sent_messages = relationship("ChatMessage", back_populates="sender", cascade="all, delete-orphan")
    received_messages = relationship("ChatMessage", back_populates="receiver", cascade="all, delete-orphan")
    message_reactions = relationship("MessageReaction", back_populates="user", cascade="all, delete-orphan")
    organized_meetings = relationship("Meeting", back_populates="organizer", cascade="all, delete-orphan")
    meeting_participations = relationship("MeetingParticipant", back_populates="user", cascade="all, delete-orphan")
    channel_memberships = relationship("ChannelMember", back_populates="user", cascade="all, delete-orphan")
    created_channels = relationship("Channel", back_populates="creator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
