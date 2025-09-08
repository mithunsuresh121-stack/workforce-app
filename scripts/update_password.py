import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_password():
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        from backend.app.auth import hash_password
        user = db.query(User).filter(User.email == "admin@app.com").first()
        if user:
            new_hashed = hash_password("supersecure123")
            user.hashed_password = new_hashed
            db.commit()
            print(f"Updated password for {user.email}")
            print(f"New hashed: {new_hashed}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    update_password()
