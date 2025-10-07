from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from ..deps import get_db, get_current_user
from ..schemas.document import Document, DocumentCreate, DocumentOut, DocumentUpdate
from ..crud import create_document, get_document, get_documents_by_company, delete_document
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

    return create_document(
        db=db,
        company_id=current_user.company_id,
        uploaded_by=current_user.id,
        title=document.title,
        file_path=document.file_path,
        file_type=document.file_type,
        file_size=document.file_size,
        description=document.description
    )

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

    return create_document(
        db=db,
        company_id=current_user.company_id,
        uploaded_by=current_user.id,
        title=document.title,
        file_path=document.file_path,
        file_type=document.file_type,
        file_size=document.file_size,
        description=document.description
    )

@router.get("/", response_model=List[DocumentOut])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    documents = get_documents_by_company(db, current_user.company_id, skip, limit)
    # Map Document model to DocumentOut schema manually
    result = []
    for doc in documents:
        result.append(
            DocumentOut(
                id=doc.id,
                title=doc.title,
                type=doc.file_type,
                size=doc.file_size,
                uploaded_by=doc.uploader.full_name if doc.uploader else "Unknown",
                upload_date=doc.created_at,
                description=doc.description
            )
        )
    return result

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
    document: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_document = get_document(db, document_id)
    if not db_document or db_document.company_id != current_user.company_id:
        raise HTTPException(status_code=404, detail="Document not found")
    # Update only provided fields
    for key, value in document.dict(exclude_unset=True).items():
        setattr(db_document, key, value)
    db.commit()
    db.refresh(db_document)
    return db_document

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
