# app/db.py
from sqlalchemy.orm import Session
from app.config import engine, SessionLocal, Base

# Dependency to get DB session in FastAPI routes
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
