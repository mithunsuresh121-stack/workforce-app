from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import enum

class ShiftStatus(str, enum.Enum):
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    status = Column(Enum(ShiftStatus), default=ShiftStatus.PENDING, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="shifts")
    employee = relationship("User", foreign_keys=[employee_id], backref="shifts")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_shifts")
