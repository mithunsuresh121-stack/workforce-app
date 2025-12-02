from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SwapRequestBase(BaseModel):
    requester_shift_id: int
    target_shift_id: int
    reason: Optional[str] = None


class SwapRequestCreate(SwapRequestBase):
    pass


class SwapRequestOut(SwapRequestBase):
    id: int
    company_id: int
    requester_id: int
    target_employee_id: int
    status: str
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
