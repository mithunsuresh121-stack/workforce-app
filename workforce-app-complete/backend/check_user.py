from app.deps import get_db
from app.crud import get_user_by_email, create_user
from app.schemas import UserCreate
import bcrypt

def main():
    db = next(get_db())
    email = "demo@company.com"
    company_id = 4
    
    user = get_user_by_email(db, email=email, company_id=company_id)
    
    if user:
        print("User exists:")
        print(f"ID: {user.id}, Email: {user.email}, Company ID: {user.company_id}, Role: {user.role}, Active: {user.is_active}")
    else:
        print("User not found, creating demo user...")
        password = "password123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_in = UserCreate(
            email=email,
            password=password,
            company_id=company_id,
            role="admin",
            is_active=True
        )
        create_user(db, user_in)
        print("Demo user created successfully.")

if __name__ == "__main__":
    main()
