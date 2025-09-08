#!/usr/bin/env python3
"""
Test CORS configuration
"""
import requests
import json

def test_cors():
    """Test CORS configuration"""
    base_url = "http://localhost:8001"
    
    print("=== CORS Test ===")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test 2: CORS preflight request
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization, Content-Type'
        }
        response = requests.options(f"{base_url}/api/v1/users/", headers=headers)
        print(f"CORS preflight: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"CORS preflight failed: {e}")
    
    # Test 3: Actual request with CORS headers
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{base_url}/api/v1/users/", headers=headers)
        print(f"Users API: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
    except Exception as e:
        print(f"Users API failed: {e}")

if __name__ == "__main__":
    test_cors()
