from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from ..deps import get_db, get_current_user
from ..schemas.document import Document, DocumentCreate, DocumentOut
from ..crud import create_document, get_document, get_documents_by_company, update_document, delete_document
from ..models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"

@router.post("/", response_model=Document, status_code=status.HTTP_201_CREATED)
def upload_document(
    title: str,
    description: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    document = DocumentCreate(
        title=title,
        description=description,
        file_path=file_path,
        file_type=file.content_type,
        file_size=os.path.getsize(file_path)
    )

    return create_document(db, document, current_user.id, current_user.company_id)

@router.post("/upload", response_model=Document, status_code=status.HTTP_201_CREATED)
def upload_document_simple(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Use filename as title, no description
    document = DocumentCreate(
        title=file.filename,
        description=None,
        file_path=file_path,
        file_type=file.content_type,
        file_size=os.path.getsize(file_path)
    )

    return create_document(db, document, current_user.id, current_user.company_id)

@router.get("/", response_model=List[DocumentOut])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_documents_by_company(db, current_user.company_id, skip, limit)

@router.get("/{document_id}", response_model=Document)
def get_document_by_id(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = get_document(db, document_id)
    if not document or document.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = get_document(db, document_id)
    if not document or document.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=document.file_path, filename=document.title, media_type='application/octet-stream')

@router.put("/{document_id}", response_model=Document)
def update_document_endpoint(
    document_id: int,
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_document = get_document(db, document_id)
    if not db_document or db_document.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return update_document(db, document_id, document)

@router.delete("/{document_id}")
def delete_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = get_document(db, document_id)
    if not document or document.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(db, document_id)
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    return {"message": "Document deleted"}
