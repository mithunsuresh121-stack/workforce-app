import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_users():
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        users = db.query(User).all()
        print("Existing users:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}, Company: {user.company_id}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
