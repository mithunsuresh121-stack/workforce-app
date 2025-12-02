from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in_time = Column(DateTime(timezone=True), nullable=False)
    clock_out_time = Column(DateTime(timezone=True), nullable=True)
    total_hours = Column(Float, nullable=True)
    overtime_hours = Column(Float, default=0.0)
    status = Column(String(50), default="active")  # active, completed, approved
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="attendances")
    employee = relationship("User", back_populates="attendance_records")
    breaks = relationship("Break", back_populates="attendance")


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
