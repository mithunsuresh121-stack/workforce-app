import os
import shutil
from typing import List

import structlog
from fastapi import (APIRouter, Depends, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.document import Document, DocumentType
from app.models.user import User
from app.schemas.schemas import DocumentCreate, DocumentOut

logger = structlog.get_logger(__name__)

router = APIRouter()

UPLOAD_DIR = "backend/uploads"


def get_role_level(role: str) -> int:
    levels = {"Employee": 1, "Manager": 2, "CompanyAdmin": 3, "SuperAdmin": 3}
    return levels.get(role, 0)


def can_access_document(user_role: str, doc_access_role: str) -> bool:
    user_level = get_role_level(user_role)
    doc_level = get_role_level(doc_access_role.upper())
    return user_level >= doc_level


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    type: str = Form(...),
    access_role: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check role: only MANAGER, ADMIN
    if current_user.role not in ["Manager", "CompanyAdmin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Validate type
    try:
        doc_type = DocumentType(type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document type")

    # Validate access_role
    if access_role not in ["EMPLOYEE", "MANAGER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid access role")

    # Sanitize filename
    filename = file.filename.replace(" ", "_").replace("/", "_").replace("\\", "_")

    # Create directory
    company_dir = os.path.join(UPLOAD_DIR, str(current_user.company_id))
    user_dir = os.path.join(company_dir, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create document record
    document = Document(
        company_id=current_user.company_id,
        user_id=current_user.id,
        file_path=file_path,
        type=doc_type,
        access_role=access_role,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/list", response_model=List[DocumentOut])
def list_documents(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    query = db.query(Document).filter(Document.company_id == current_user.company_id)
    documents = query.all()
    # Filter based on access
    visible_docs = [
        doc
        for doc in documents
        if can_access_document(current_user.role, doc.access_role)
    ]
    return visible_docs


@router.get("/download/{document_id}")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id, Document.company_id == current_user.company_id
        )
        .first()
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not can_access_document(current_user.role, document.access_role):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=document.file_path,
        filename=os.path.basename(document.file_path),
        media_type="application/octet-stream",
    )
