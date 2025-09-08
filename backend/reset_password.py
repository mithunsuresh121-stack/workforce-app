from app.db import SessionLocal
from app.auth import hash_password
from app.crud import get_user_by_email

def main():
    db = SessionLocal()
    user = get_user_by_email(db, 'admin@techcorp.com', 1)
    if user:
        # Reset password to 'password123'
        user.hashed_password = hash_password('password123')
        db.commit()
        db.refresh(user)
        print("Password reset successfully")
        print(f"New password hash: {user.hashed_password}")
    else:
        print("User not found")

if __name__ == "__main__":
    main()
