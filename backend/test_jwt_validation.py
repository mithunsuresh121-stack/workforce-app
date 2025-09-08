import requests
from jose import jwt
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login"

def test_jwt_structure_and_claims():
    """Test JWT token structure, claims, and expiry"""
    print("Testing JWT token structure and claims...")
    
    # Test login to get a valid token
    payload = {
        "email": "admin@techcorp.com",
        "password": "password123",
        "company_id": 1
    }
    
    try:
        response = requests.post(LOGIN_URL, json=payload)
        if response.status_code != 200:
            print(f"✗ Login failed: {response.status_code} {response.text}")
            return False
        
        token_data = response.json()
        access_token = token_data["access_token"]
        token_type = token_data["token_type"]
        
        print(f"✓ Login successful. Token: {access_token[:50]}...")
        print(f"✓ Token type: {token_type}")
        
        # Decode the token without verification to inspect claims
        try:
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            
            # Validate required claims
            required_claims = ["sub", "company_id", "role", "exp"]
            missing_claims = [claim for claim in required_claims if claim not in decoded_token]
            
            if missing_claims:
                print(f"✗ Missing required claims: {missing_claims}")
                return False
            else:
                print("✓ All required claims present")
                
            # Check for optional iat claim
            if "iat" in decoded_token:
                print("✓ iat claim present")
                iat_time = datetime.fromtimestamp(decoded_token["iat"])
                print(f"✓ Token issued at: {iat_time}")
            else:
                print("ℹ iat claim not present (optional)")
                
            # Validate claim values
            if decoded_token["sub"] != "admin@techcorp.com":
                print(f"✗ Invalid sub claim: {decoded_token['sub']}")
                return False
            else:
                print(f"✓ Valid sub claim: {decoded_token['sub']}")
            
            if decoded_token["company_id"] != 1:
                print(f"✗ Invalid company_id claim: {decoded_token['company_id']}")
                return False
            else:
                print(f"✓ Valid company_id claim: {decoded_token['company_id']}")
            
            if decoded_token["role"] != "SuperAdmin":
                print(f"✗ Invalid role claim: {decoded_token['role']}")
                return False
            else:
                print(f"✓ Valid role claim: {decoded_token['role']}")
            
            # Validate expiry time (should be reasonable)
            exp_time = datetime.fromtimestamp(decoded_token["exp"])
            current_time = datetime.now()
            
            if exp_time < current_time:
                print(f"✗ Token already expired: {exp_time}")
                return False
            elif (exp_time - current_time).total_seconds() > 3600 * 24:  # More than 24 hours
                print(f"✗ Token expiry time too long: {exp_time}")
                return False
            else:
                print(f"✓ Valid expiry time: {exp_time}")
                print(f"✓ Token expires in: {(exp_time - current_time).total_seconds() / 60:.1f} minutes")
            
            # Test token validation with protected endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            companies_response = requests.get(f"{BASE_URL}/companies/1", headers=headers)
            
            if companies_response.status_code == 200:
                print("✓ Token successfully validated with protected endpoint")
                return True
            else:
                print(f"✗ Token validation failed: {companies_response.status_code} {companies_response.text}")
                return False
                
        except jwt.InvalidTokenError as e:
            print(f"✗ Invalid token structure: {e}")
            return False
            
    except Exception as e:
        print(f"✗ JWT validation error: {e}")
        return False

def test_expired_token():
    """Test handling of expired tokens"""
    print("\nTesting expired token handling...")
    
    # Create an expired token manually (using the same secret as the app)
    expired_payload = {
        "sub": "admin@techcorp.com",
        "company_id": 1,
        "role": "SuperAdmin",
        "exp": datetime.utcnow() - timedelta(minutes=10),  # Expired 10 minutes ago
        "iat": datetime.utcnow() - timedelta(minutes=70)   # Issued 70 minutes ago
    }
    
    try:
        # Use the same secret key that the app uses
        expired_token = jwt.encode(expired_payload, "CHANGE_ME", algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = requests.get(f"{BASE_URL}/companies/1", headers=headers)
        
        if response.status_code == 401:
            print("✓ Expired token correctly rejected with 401 status")
            return True
        else:
            print(f"✗ Expired token not properly rejected: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Expired token test error: {e}")
        return False

def test_invalid_token():
    """Test handling of invalid tokens"""
    print("\nTesting invalid token handling...")
    
    # Test with malformed token
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/companies/1", headers=headers)
    
    if response.status_code == 401:
        print("✓ Invalid token correctly rejected with 401 status")
        return True
    else:
        print(f"✗ Invalid token not properly rejected: {response.status_code}")
        return False

def main():
    print("Starting JWT validation tests...")
    print("=" * 50)
    
    results = []
    
    # Run all tests
    results.append(test_jwt_structure_and_claims())
    results.append(test_expired_token())
    results.append(test_invalid_token())
    
    print("\n" + "=" * 50)
    print("JWT Validation Test Summary:")
    print("=" * 50)
    
    test_names = [
        "JWT Structure and Claims",
        "Expired Token Handling", 
        "Invalid Token Handling"
    ]
    
    all_passed = True
    for i, (test_name, result) in enumerate(zip(test_names, results), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i}. {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL JWT VALIDATION TESTS PASSED!")
        print("The authentication system is working correctly with proper:")
        print("- Token structure and claims validation")
        print("- Expiry time handling")
        print("- Invalid token rejection")
    else:
        print("❌ SOME TESTS FAILED - Check the implementation")
    
    return all_passed

if __name__ == "__main__":
    main()
