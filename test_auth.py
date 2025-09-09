#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""

import requests
import json

def test_auth():
    base_url = "http://localhost:5000"
    
    print("Testing Dreamwell Authentication API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test user registration
    try:
        register_data = {
            "email": "test@company.com",
            "password": "TestPassword123",
            "company_name": "Test Company",
            "website": "https://testcompany.com"
        }
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Registration: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"   User created: {result['user']['email']}")
            access_token = result['access_token']
        else:
            print(f"   Error: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # Test user login
    try:
        login_data = {
            "email": "test@company.com",
            "password": "TestPassword123"
        }
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Logged in: {result['user']['email']}")
            access_token = result['access_token']
        else:
            print(f"   Error: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Test protected endpoint
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{base_url}/api/auth/profile", headers=headers)
        print(f"✅ Profile: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Profile: {result['user']['company_name']}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"❌ Profile failed: {e}")
    
    print("\n🎉 Authentication testing complete!")

if __name__ == "__main__":
    test_auth()
