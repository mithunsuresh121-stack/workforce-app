from app.db import SessionLocal
from app.crud import get_user_by_email
from app.auth import verify_password

def main():
    db = SessionLocal()
    
    # Check if user exists
    user = get_user_by_email(db, 'admin@techcorp.com', 1)
    if not user:
        print("❌ User not found: admin@techcorp.com with company_id=1")
        return
    
    print(f"✅ User found:")
    print(f"   Email: {user.email}")
    print(f"   Full Name: {user.full_name}")
    print(f"   Role: {user.role}")
    print(f"   Company ID: {user.company_id}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Hashed Password: {user.hashed_password}")
    
    # Test password verification
    test_password = "password123"
    print(f"\n🔐 Testing password verification:")
    print(f"   Plain password: {test_password}")
    
    try:
        is_match = verify_password(test_password, user.hashed_password)
        if is_match:
            print("   ✅ Password verification: MATCH")
        else:
            print("   ❌ Password verification: MISMATCH")
    except Exception as e:
        print(f"   ⚠️  Password verification error: {e}")
    
    # Test with wrong password
    wrong_password = "wrongpassword"
    print(f"\n🔐 Testing with wrong password:")
    print(f"   Plain password: {wrong_password}")
    
    try:
        is_match = verify_password(wrong_password, user.hashed_password)
        if is_match:
            print("   ❌ Password verification: MATCH (unexpected!)")
        else:
            print("   ✅ Password verification: MISMATCH (expected)")
    except Exception as e:
        print(f"   ⚠️  Password verification error: {e}")

if __name__ == "__main__":
    main()
