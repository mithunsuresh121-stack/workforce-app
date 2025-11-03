from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db import Base

class MeetingStatus(str, PyEnum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("company_departments.id", ondelete="CASCADE"), nullable=True)
    team_id = Column(Integer, ForeignKey("company_teams.id", ondelete="CASCADE"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(MeetingStatus), nullable=False)
    link = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    organizer = relationship("User", foreign_keys=[organizer_id], back_populates="organized_meetings")
    company = relationship("Company", back_populates="meetings")
    department = relationship("CompanyDepartment", back_populates="meetings")
    team = relationship("CompanyTeam", back_populates="meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
