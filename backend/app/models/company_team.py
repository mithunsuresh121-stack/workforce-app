from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class CompanyTeam(Base):
    __tablename__ = "company_teams"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(
        Integer,
        ForeignKey("company_departments.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    department = relationship("CompanyDepartment", back_populates="teams")
    users = relationship("User", back_populates="team")
    channels = relationship(
        "Channel", back_populates="team", cascade="all, delete-orphan"
    )
    meetings = relationship(
        "Meeting", back_populates="team", cascade="all, delete-orphan"
    )
