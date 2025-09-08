from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..db import Base

class Leave(Base):
    __tablename__ = "leaves"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
