from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Document(DocumentBase):
    id: int
    uploaded_by: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    title: str
    type: str
    size: int
    uploaded_by: str  # Will be populated from user relationship
    upload_date: datetime
    description: Optional[str] = None

    class Config:
        from_attributes = True
