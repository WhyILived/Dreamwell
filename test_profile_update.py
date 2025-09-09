#!/usr/bin/env python3
"""
Test script to debug profile update functionality
"""

import requests
import json

def test_profile_update():
    base_url = "http://localhost:5000"
    
    # First, let's login to get a token
    login_data = {
        "email": "test@dreamwell.com",
        "password": "TestPassword123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_result = login_response.json()
    token = login_result['access_token']
    print("✅ Login successful")
    
    # Now test profile update
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "company_name": "Updated Test Company",
        "website": "https://updatedtest.com",
        "keywords": "test, updated, keywords, debugging"
    }
    
    print("📝 Testing profile update...")
    update_response = requests.put(f"{base_url}/api/auth/profile", json=update_data, headers=headers)
    
    print(f"Status Code: {update_response.status_code}")
    print(f"Response: {update_response.text}")
    
    if update_response.status_code == 200:
        print("✅ Profile update successful!")
        result = update_response.json()
        print(f"Updated user: {json.dumps(result['user'], indent=2)}")
    else:
        print("❌ Profile update failed")

if __name__ == "__main__":
    test_profile_update()
