from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    departments = relationship(
        "CompanyDepartment", back_populates="company", cascade="all, delete-orphan"
    )
    shifts = relationship(
        "Shift", back_populates="company", cascade="all, delete-orphan"
    )
    employee_profiles = relationship(
        "EmployeeProfile", back_populates="company", cascade="all, delete-orphan"
    )
    attendances = relationship(
        "Attendance", back_populates="company", cascade="all, delete-orphan"
    )
    channels = relationship(
        "Channel", back_populates="company", cascade="all, delete-orphan"
    )
    meetings = relationship(
        "Meeting", back_populates="company", cascade="all, delete-orphan"
    )
    chat_messages = relationship(
        "ChatMessage", back_populates="company", cascade="all, delete-orphan"
    )
    settings = relationship(
        "CompanySettings",
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )
    vendors = relationship(
        "Vendor", back_populates="company", cascade="all, delete-orphan"
    )
    purchase_orders = relationship(
        "PurchaseOrder", back_populates="company", cascade="all, delete-orphan"
    )
    inventory_items = relationship(
        "InventoryItem", back_populates="company", cascade="all, delete-orphan"
    )
    invites = relationship(
        "Invite", back_populates="company", cascade="all, delete-orphan"
    )
