import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_user():
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        user = db.query(User).filter(User.email == "admin@app.com").first()
        if user:
            print(f"User found: {user.email}, role: {user.role}, company_id: {user.company_id}, is_active: {user.is_active}")
            print(f"Hashed password: {user.hashed_password}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
