# app/db.py
from sqlalchemy.orm import Session

from app.config import Base, SessionLocal, engine


# Dependency to get DB session in FastAPI routes
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
