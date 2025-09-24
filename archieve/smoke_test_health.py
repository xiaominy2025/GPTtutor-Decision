#!/usr/bin/env python3
"""
Smoke Test for Engent Labs V1.6.6.6 Backend Deployment
Tests /health endpoint to validate Step 1-3 deployment
"""

import requests
import json
import sys
from datetime import datetime

def smoke_test_health():
    """
    Test the /health endpoint of the deployed Lambda function
    """
    print("🚀 Starting Smoke Test for V1.6.6.6 Backend Deployment")
    print("=" * 60)
    
    # Lambda function URL
    base_url = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws"
    health_endpoint = f"{base_url}/health"
    
    print(f"📍 Testing endpoint: {health_endpoint}")
    print(f"⏰ Test time: {datetime.utcnow().isoformat()}Z")
    print("-" * 60)
    
    try:
        # Send GET request to /health endpoint
        print("📡 Sending GET request to /health...")
        response = requests.get(health_endpoint, timeout=30)
        
        # Print status code
        print(f"📊 Status Code: {response.status_code}")
        
        # Print response headers (for debugging)
        print("\n📋 Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['content-type', 'access-control-allow-origin', 'access-control-allow-methods']:
                print(f"  {key}: {value}")
        
        # Parse and print JSON response
        print("\n📄 Response Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text}")
            return False
        
        # Validate response
        print("\n🔍 Validating response...")
        validation_passed = True
        validation_errors = []
        
        # Check status code
        if response.status_code != 200:
            validation_errors.append(f"Status code {response.status_code} != 200")
            validation_passed = False
        else:
            print("✅ Status code: 200")
        
        # Check for required keys
        required_keys = ["data", "status", "version", "timestamp"]
        for key in required_keys:
            if key not in response_json:
                validation_errors.append(f"Missing required key: {key}")
                validation_passed = False
            else:
                print(f"✅ Found key: {key}")
        
        # Check data.status
        if "data" in response_json and "status" in response_json["data"]:
            if response_json["data"]["status"] == "healthy":
                print("✅ data.status: healthy")
            else:
                validation_errors.append(f"data.status '{response_json['data']['status']}' != 'healthy'")
                validation_passed = False
        else:
            validation_errors.append("Missing data.status or data.status != 'healthy'")
            validation_passed = False
        
        # Check status
        if "status" in response_json:
            if response_json["status"] == "success":
                print("✅ status: success")
            else:
                validation_errors.append(f"status '{response_json['status']}' != 'success'")
                validation_passed = False
        
        # Check version
        if "version" in response_json:
            if response_json["version"] == "V1.6.6.6":
                print("✅ version: V1.6.6.6")
            else:
                validation_errors.append(f"version '{response_json['version']}' != 'V1.6.6.6'")
                validation_passed = False
        
        # Check timestamp format
        if "timestamp" in response_json:
            timestamp = response_json["timestamp"]
            if isinstance(timestamp, str) and "T" in timestamp and "Z" in timestamp:
                print("✅ timestamp: Valid ISO format")
            else:
                validation_errors.append(f"timestamp format invalid: {timestamp}")
                validation_passed = False
        
        # Print validation results
        print("\n" + "=" * 60)
        if validation_passed:
            print("🎉 /health check PASSED")
            print("✅ All validations successful")
            print("✅ Step 1-3 deployment is working correctly")
            print("✅ Ready to proceed to Step 5 (Frontend Test)")
            return True
        else:
            print("❌ /health check FAILED")
            print("❌ Validation errors:")
            for error in validation_errors:
                print(f"   - {error}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Lambda function may be cold starting")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Check if Lambda function URL is accessible")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """
    Main function to run the smoke test
    """
    print("🔬 Engent Labs V1.6.6.6 Backend - Smoke Test")
    print("Testing /health endpoint deployment validation")
    print()
    
    success = smoke_test_health()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 SMOKE TEST RESULT: PASSED")
        print("✅ Backend deployment is healthy and ready")
    else:
        print("🎯 SMOKE TEST RESULT: FAILED")
        print("❌ Backend deployment needs attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
