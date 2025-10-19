"""
Test script to debug authentication issues.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup():
    """Test user signup."""
    print("Testing signup...")
    data = {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Signup failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test user login."""
    print("\nTesting login...")
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_verify(token):
    """Test token verification."""
    print(f"\nTesting token verification...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Verification failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=== Authentication Test ===")
    
    # Test signup
    signup_result = test_signup()
    
    if signup_result:
        print(f"Signup successful: {signup_result}")
        
        # Test login
        login_result = test_login()
        
        if login_result:
            print(f"Login successful: {login_result}")
            
            # Test token verification
            token = login_result.get('token')
            if token:
                verify_result = test_verify(token)
                if verify_result:
                    print(f"Token verification successful: {verify_result}")
                else:
                    print("Token verification failed")
            else:
                print("No token in login response")
        else:
            print("Login failed")
    else:
        print("Signup failed - user may already exist")
    
    print("\n=== Test Complete ===")
