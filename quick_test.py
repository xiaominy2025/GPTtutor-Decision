#!/usr/bin/env python3
"""
Quick test for Lambda CORS functionality
"""
import requests

def test_lambda_cors():
    url = "https://suu42zea6k74bqdogirjfhh2p40vflgq.lambda-url.us-east-2.on.aws"
    
    print("🧪 Testing Lambda CORS functionality")
    print(f"🔗 URL: {url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"📋 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test courses endpoint
    try:
        response = requests.get(f"{url}/courses", headers={"Origin": "http://localhost:5174"})
        print(f"✅ Courses endpoint: {response.status_code}")
        print(f"📋 CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ Courses test failed: {e}")
    
    # Test query endpoint
    try:
        response = requests.post(f"{url}/query", 
                               json={"query": "test query", "course_id": "decision"},
                               headers={"Origin": "http://localhost:5174"})
        print(f"✅ Query endpoint: {response.status_code}")
        print(f"📋 CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ Query test failed: {e}")

if __name__ == "__main__":
    test_lambda_cors()