#!/usr/bin/env python3
"""
Detailed API test script for V1.6.5
"""

import requests
import json

def test_query_detailed():
    """Test query endpoint with detailed output"""
    try:
        data = {"query": "I need to decide between two job offers"}
        response = requests.post("http://127.0.0.1:5000/query", json=data)
        print("✅ Query test:")
        print(f"Status: {response.status_code}")
        
        result = response.json()
        print(f"Response keys: {list(result.keys())}")
        
        if 'answer' in result:
            print(f"\n📝 Full Answer:")
            print("=" * 50)
            print(result['answer'])
            print("=" * 50)
        else:
            print(f"\n❌ No answer in response: {result}")
            
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 V1.6.5 Detailed API Test")
    print("=" * 40)
    
    test_query_detailed() 