from sqlalchemy.orm import Session
from ..models.document import Document
from ..schemas.document import DocumentCreate

def create_document(db: Session, document: DocumentCreate, uploaded_by: int, company_id: int):
    db_document = Document(
        **document.dict(),
        uploaded_by=uploaded_by,
        company_id=company_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_by_company(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(Document).filter(Document.company_id == company_id).offset(skip).limit(limit).all()

def update_document(db: Session, document_id: int, document: DocumentCreate):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        for key, value in document.dict().items():
            setattr(db_document, key, value)
        db.commit()
        db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db.delete(db_document)
        db.commit()
    return db_document
