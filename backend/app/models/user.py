from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="Employee")  # SuperAdmin, CompanyAdmin, Manager, Employee
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)  # Nullable for Super Admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="users")
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False, foreign_keys="[EmployeeProfile.user_id]")
    attendance_records = relationship("Attendance", back_populates="employee")
    shifts = relationship("Shift", back_populates="employee")
    
    def __repr__(self):
        return f"<User {self.email}>"
