#!/usr/bin/env python3
"""
Pre-deployment validation test
"""

import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_health_endpoint():
    """Test health endpoint structure"""
    print("🧪 Testing health endpoint...")
    
    try:
        from lambda_function import lambda_handler
        
        # Create a mock health request event
        health_event = {
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/health"
                }
            },
            "headers": {
                "origin": "https://www.engentlabs.com"
            }
        }
        
        result = lambda_handler(health_event, None)
        print(f"✅ Health endpoint: Status {result['statusCode']}")
        
        # Parse body to check structure
        body = json.loads(result['body'])
        print(f"   Version: {body.get('version', 'MISSING')}")
        print(f"   Status: {body.get('status', 'MISSING')}")
        
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_course_endpoint():
    """Test course endpoint structure"""
    print("\n🧪 Testing course endpoint...")
    
    try:
        from lambda_function import lambda_handler
        
        # Create a mock course request event
        course_event = {
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/api/course/decision"
                }
            },
            "headers": {
                "origin": "https://www.engentlabs.com"
            }
        }
        
        result = lambda_handler(course_event, None)
        print(f"✅ Course endpoint: Status {result['statusCode']}")
        
        # Parse body to check structure
        body = json.loads(result['body'])
        data = body.get('data', {})
        print(f"   Title: {data.get('title', 'MISSING')}")
        print(f"   Tagline: {data.get('tagline', 'MISSING')}")
        
        return True
    except Exception as e:
        print(f"❌ Course endpoint test failed: {e}")
        return False

def test_options_handling():
    """Test OPTIONS handling"""
    print("\n🧪 Testing OPTIONS handling...")
    
    try:
        from lambda_function import handle_options
        
        # Test OPTIONS request
        options_event = {
            "headers": {
                "origin": "https://www.engentlabs.com"
            }
        }
        
        result = handle_options(options_event)
        print(f"✅ OPTIONS handling: Status {result['statusCode']}")
        print(f"   CORS Origin: {result['headers'].get('Access-Control-Allow-Origin', 'MISSING')}")
        print(f"   CORS Methods: {result['headers'].get('Access-Control-Allow-Methods', 'MISSING')}")
        
        return True
    except Exception as e:
        print(f"❌ OPTIONS handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Pre-deployment Validation Test")
    print("=" * 50)
    
    try:
        # Run all tests
        health_ok = test_health_endpoint()
        course_ok = test_course_endpoint()
        options_ok = test_options_handling()
        
        if health_ok and course_ok and options_ok:
            print("\n✅ All validation tests passed! Ready for deployment.")
        else:
            print("\n❌ Some validation tests failed. Fix before deployment.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)
