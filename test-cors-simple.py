#!/usr/bin/env python3
"""
Basit CORS test scripti
"""
import requests
import json

def test_cors():
    """Test CORS configuration"""
    print("=== CORS Test ===")
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8001/health")
        print(f"✅ Backend Health: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Backend Health Failed: {e}")
        return
    
    # Test CORS headers
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }
        
        response = requests.get("http://localhost:8001/api/v1/users/", headers=headers)
        
        print(f"\n=== CORS Headers ===")
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        for header, value in cors_headers.items():
            if value:
                print(f"✅ {header}: {value}")
            else:
                print(f"❌ {header}: Not found")
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ CORS Test PASSED!")
        else:
            print(f"❌ CORS Test FAILED: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CORS Test Error: {e}")

if __name__ == "__main__":
    test_cors()
