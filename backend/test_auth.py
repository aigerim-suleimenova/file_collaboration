#!/usr/bin/env python3
"""
Test script to debug authentication issues
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_signup():
    """Test user signup"""
    url = f"{BASE_URL}/users/signup"
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    print(f"Testing signup: {url}")
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response

def test_login():
    """Test user login"""
    url = f"{BASE_URL}/login/access-token"
    data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"\nTesting login: {url}")
    response = requests.post(url, data=data)  # Note: using data, not json
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response

def test_files_with_token(token):
    """Test files endpoint with token"""
    url = f"{BASE_URL}/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nTesting files endpoint: {url}")
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response

if __name__ == "__main__":
    print("🔍 Testing Authentication Flow...")
    
    # Test signup
    signup_response = test_signup()
    
    if signup_response.status_code == 200:
        print("✅ Signup successful")
        
        # Test login
        login_response = test_login()
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            token_data = login_response.json()
            token = token_data.get("access_token")
            
            if token:
                print(f"✅ Got token: {token[:20]}...")
                
                # Test files endpoint
                files_response = test_files_with_token(token)
                
                if files_response.status_code == 200:
                    print("✅ Files endpoint working!")
                else:
                    print(f"❌ Files endpoint failed: {files_response.status_code}")
            else:
                print("❌ No token in response")
        else:
            print("❌ Login failed")
    else:
        print("❌ Signup failed")
