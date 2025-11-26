from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VendorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class PurchaseOrderStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

class InventoryStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"

class VendorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_email: EmailStr
    phone: Optional[str] = None
    status: VendorStatus = VendorStatus.ACTIVE

class VendorCreate(VendorBase):
    pass

class VendorOut(VendorBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PurchaseOrderBase(BaseModel):
    vendor_id: int
    item_name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderOut(PurchaseOrderBase):
    id: int
    status: PurchaseOrderStatus
    approver_id: Optional[int]
    created_by: int
    company_id: int
    bids: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    unit_price: float = Field(..., ge=0)
    expiry_date: Optional[datetime] = None
    status: InventoryStatus = InventoryStatus.IN_STOCK

class InventoryItemCreate(InventoryItemBase):
    purchase_order_id: Optional[int] = None

class InventoryItemOut(InventoryItemBase):
    id: int
    purchase_order_id: Optional[int]
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BidCreate(BaseModel):
    vendor_id: int
    amount: float = Field(..., gt=0)
    notes: Optional[str] = None
