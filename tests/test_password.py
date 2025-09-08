import sys
import os
sys.path.append('backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://workforce:workforce_pw@localhost:5432/workforce"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_password():
    db = SessionLocal()
    try:
        from backend.app.models.user import User
        from backend.app.auth import verify_password
        user = db.query(User).filter(User.email == "admin@app.com").first()
        if user:
            print(f"Testing password for {user.email}")
            print(f"Hashed: {user.hashed_password}")
            result = verify_password("supersecure123", user.hashed_password)
            print(f"Password verification result: {result}")
        else:
            print("User not found")
    finally:
        db.close()

if __name__ == "__main__":
    test_password()
