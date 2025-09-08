#!/usr/bin/env python3
"""
CORS monitoring and health check
"""
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_cors_health():
    """Check CORS health"""
    base_url = "http://localhost:8001"
    
    try:
        # Test basic health
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Backend health check passed")
        else:
            logger.error(f"❌ Backend health check failed: {response.status_code}")
            return False
        
        # Test CORS preflight
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization, Content-Type'
        }
        
        response = requests.options(f"{base_url}/api/v1/users/", headers=headers, timeout=5)
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        logger.info(f"CORS Headers: {cors_headers}")
        
        if response.status_code == 200:
            logger.info("✅ CORS preflight check passed")
            return True
        else:
            logger.error(f"❌ CORS preflight check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ CORS health check failed: {e}")
        return False

def monitor_cors():
    """Monitor CORS continuously"""
    logger.info("Starting CORS monitoring...")
    
    while True:
        try:
            if check_cors_health():
                logger.info("✅ CORS is working correctly")
            else:
                logger.error("❌ CORS issues detected")
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            logger.info("CORS monitoring stopped")
            break
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_cors()
