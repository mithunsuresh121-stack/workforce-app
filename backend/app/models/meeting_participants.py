from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class ParticipantRole(str, PyEnum):
    ORGANIZER = "ORGANIZER"
    PARTICIPANT = "PARTICIPANT"


class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    meeting_id = Column(
        Integer, ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role = Column(Enum(ParticipantRole), nullable=False)
    join_time = Column(DateTime, nullable=True)
    leave_time = Column(DateTime, nullable=True)

    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participations")
