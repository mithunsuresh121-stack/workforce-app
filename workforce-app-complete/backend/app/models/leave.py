from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.db import Base

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, nullable=False)
    type = Column(Enum('ANNUAL', 'SICK', 'MATERNITY', 'PATERNITY', 'PERSONAL', name='leavetype'), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(Enum('Approved', 'Pending', 'Rejected', name='leavestatus'), default="Pending")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
