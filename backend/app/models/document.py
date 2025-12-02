import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class DocumentType(str, enum.Enum):
    POLICY = "POLICY"
    PAYSLIP = "PAYSLIP"
    NOTICE = "NOTICE"
    OTHER = "OTHER"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    type = Column(Enum(DocumentType), nullable=False)
    access_role = Column(String, nullable=False)  # "EMPLOYEE", "MANAGER", "ADMIN"
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company")
    user = relationship("User")

    def __repr__(self):
        return f"<Document {self.file_path} for company {self.company_id}>"
