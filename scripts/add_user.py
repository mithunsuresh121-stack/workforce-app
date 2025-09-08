from backend.db import SessionLocal
from backend.models.user import User
from backend.crud import create_user
from backend.auth import hash_password

def main():
    db = SessionLocal()
    create_user(db, 'admin@techcorp.com', 'password123', 'Admin User', 'SuperAdmin', 1)
    print("User created successfully.")

if __name__ == "__main__":
    main()
