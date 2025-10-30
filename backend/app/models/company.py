from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    domain = Column(String, nullable=True, unique=True)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)  # URL to company logo
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    employee_profiles = relationship("EmployeeProfile", back_populates="company")
    attendances = relationship("Attendance", back_populates="company")
    shifts = relationship("Shift", back_populates="company")
    swap_requests = relationship("SwapRequest", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name}>"
