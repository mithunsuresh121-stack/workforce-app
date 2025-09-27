from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base
import enum

class DocumentType(str, enum.Enum):
    CONTRACT = "CONTRACT"
    POLICY = "POLICY"
    TRAINING = "TRAINING"
    CERTIFICATE = "CERTIFICATE"
    OTHER = "OTHER"

class AccessLevel(str, enum.Enum):
    PUBLIC = "PUBLIC"  # Visible to all company employees
    PRIVATE = "PRIVATE"  # Only uploader and admins
    RESTRICTED = "RESTRICTED"  # Specific roles only

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String(500), nullable=False)  # URL/path to stored file
    file_type = Column(String(100), nullable=True)  # MIME type
    document_type = Column(Enum(DocumentType), nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.PRIVATE, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="documents")
    uploader = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.title} by user {self.user_id}>"
