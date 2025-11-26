from app.db import SessionLocal
from app.models.user import User
from app.crud import create_user
from app.auth import hash_password

def main():
    db = SessionLocal()
    create_user(db, 'admin@techcorp.com', 'password123', 'Admin User', 'SuperAdmin', 1)
    print("User created successfully.")

if __name__ == "__main__":
    main()
