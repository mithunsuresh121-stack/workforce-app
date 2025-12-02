from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class CompanyDepartment(Base):
    __tablename__ = "company_departments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="departments")
    teams = relationship(
        "CompanyTeam", back_populates="department", cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="department")
    channels = relationship(
        "Channel", back_populates="department", cascade="all, delete-orphan"
    )
    meetings = relationship(
        "Meeting", back_populates="department", cascade="all, delete-orphan"
    )
