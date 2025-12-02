from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hire_date = Column(DateTime, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    # gender column removed as per request
    # gender = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    employee_id = Column(String, unique=True, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship(
        "User", back_populates="employee_profile", foreign_keys=[user_id]
    )
    company = relationship("Company", back_populates="employee_profiles")
    manager = relationship("User", foreign_keys=[manager_id])

    def __repr__(self):
        return f"<EmployeeProfile {self.user_id}>"
