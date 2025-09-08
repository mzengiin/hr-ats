#!/usr/bin/env python3
"""
Hızlı CORS test
"""
import requests

def test_cors():
    print("=== CORS Test ===")
    
    try:
        # Test backend
        response = requests.get("http://localhost:8001/health")
        print(f"Backend Health: {response.status_code}")
        
        # Test CORS
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.get("http://localhost:8001/api/v1/users/", headers=headers)
        
        print(f"CORS Response: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ CORS WORKING!")
        else:
            print("❌ CORS FAILED!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cors()
