#!/usr/bin/env python3
"""
Simple API test script for V1.6.5
"""

import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        print("✅ Health check:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_query():
    """Test query endpoint"""
    try:
        data = {"query": "I need to decide between two job offers"}
        response = requests.post("http://127.0.0.1:5000/query", json=data)
        print("\n✅ Query test:")
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Success: {result.get('success', 'N/A')}")
        if 'answer' in result:
            print(f"Answer length: {len(result['answer'])} characters")
            print("Answer preview:")
            print(result['answer'][:200] + "...")
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 V1.6.5 API Test")
    print("=" * 30)
    
    health_ok = test_health()
    query_ok = test_query()
    
    if health_ok and query_ok:
        print("\n🎉 All API tests passed!")
    else:
        print("\n❌ Some API tests failed!") 