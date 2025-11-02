from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class CompanySettings(Base):
    __tablename__ = "company_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    timezone = Column(String, default="UTC")
    date_format = Column(String, default="YYYY-MM-DD")
    time_format = Column(String, default="HH:mm")
    currency = Column(String, default="USD")
    language = Column(String, default="en")
    allow_employee_registration = Column(Boolean, default=True)
    require_manager_approval = Column(Boolean, default=False)
    enable_notifications = Column(Boolean, default=True)
    enable_chat = Column(Boolean, default=True)
    enable_meetings = Column(Boolean, default=True)
    max_users = Column(Integer, default=100)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="settings")

    class Config:
        from_attributes = True
