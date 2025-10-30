from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.db import Base

class ParticipantRole(str, PyEnum):
    ORGANIZER = "ORGANIZER"
    PARTICIPANT = "PARTICIPANT"

class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    meeting_id = Column(Integer, ForeignKey("meetings.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(Enum(ParticipantRole), nullable=False)
    join_time = Column(DateTime, nullable=True)
    leave_time = Column(DateTime, nullable=True)

    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participations")
