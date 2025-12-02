from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class VendorStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="vendors")
    purchase_orders = relationship(
        "PurchaseOrder", back_populates="vendor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Vendor {self.name}>"
