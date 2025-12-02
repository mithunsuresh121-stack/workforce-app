from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.models import User

# Setup engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_user_role(email: str = "admin@app.com"):
    """Fetch a user by email and print their role and company."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print("=== User Role Information ===")
            print(f"Email      : {user.email}")
            print(f"Role       : {user.role}")
            print(f"Company ID : {user.company_id}")
        else:
            print(f"User with email '{email}' not found.")
    finally:
        db.close()


if __name__ == "__main__":
    # Default check for admin@app.com
    get_user_role()
