from pydantic import BaseModel
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

class Document(DocumentBase):
    id: int
    uploaded_by: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
