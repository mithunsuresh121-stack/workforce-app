import structlog
from sqlalchemy.orm import Session

from app.models.announcement import Announcement
from app.schemas.schemas import AnnouncementCreate

logger = structlog.get_logger(__name__)


def create_announcement(
    db: Session, announcement: AnnouncementCreate, company_id: int, created_by: int
):
    db_announcement = Announcement(
        **announcement.dict(), company_id=company_id, created_by=created_by
    )
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement


def get_announcements_for_company(db: Session, company_id: int):
    return (
        db.query(Announcement)
        .filter(Announcement.company_id == company_id)
        .order_by(Announcement.created_at.desc())
        .all()
    )
