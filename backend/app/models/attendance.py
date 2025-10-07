from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import enum

class AttendanceStatusEnum(str, enum.Enum):
    CLOCKED_IN = "CLOCKED_IN"
    CLOCKED_OUT = "CLOCKED_OUT"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    ip_address = Column(String, nullable=True)
    clock_in_time = Column(DateTime(timezone=True), nullable=False)
    clock_out_time = Column(DateTime(timezone=True), nullable=True)
    total_hours = Column(Float, nullable=True)  # computed on clock-out
    status = Column(Enum(AttendanceStatusEnum), server_default="CLOCKED_OUT", nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("User", back_populates="attendance_records")
    breaks = relationship("Break", back_populates="attendance")

    __table_args__ = (
        Index('ix_attendance_employee_clockin', 'employee_id', 'clock_in_time'),
    )


class Break(Base):
    __tablename__ = "breaks"

    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendance.id"), nullable=False)
    break_start = Column(DateTime(timezone=True), nullable=False)
    break_end = Column(DateTime(timezone=True), nullable=True)
    break_type = Column(String(50), default="lunch")  # lunch, short_break, etc.
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attendance = relationship("Attendance", back_populates="breaks")


# Add relationships to User model
# This will be added to the User model in user.py
# user.attendance_records = relationship("Attendance", back_populates="employee")
# attendance.breaks = relationship("Break", back_populates="attendance")
