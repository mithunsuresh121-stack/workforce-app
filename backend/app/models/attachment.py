from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(
        String(50), nullable=False
    )  # e.g., 'image/jpeg', 'application/pdf'
    file_size = Column(Float, nullable=False)  # in MB
    uploaded_at = Column(DateTime, server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User")

    def __repr__(self):
        return f"<Attachment id={self.id} task_id={self.task_id} file_path={self.file_path!r} file_type={self.file_type}>"
