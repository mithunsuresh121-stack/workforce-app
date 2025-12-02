import structlog
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.schemas import DocumentCreate

logger = structlog.get_logger(__name__)


def create_document(
    db: Session, document: DocumentCreate, company_id: int, user_id: int
):
    db_document = Document(**document.dict(), company_id=company_id, user_id=user_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_documents_for_company(db: Session, company_id: int):
    return db.query(Document).filter(Document.company_id == company_id).all()


def get_document_by_id(db: Session, document_id: int, company_id: int):
    return (
        db.query(Document)
        .filter(Document.id == document_id, Document.company_id == company_id)
        .first()
    )
