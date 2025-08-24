#!/usr/bin/env python3
import requests
import json

# Function URL
FUNCTION_URL = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws"

def test_health():
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{FUNCTION_URL}/health")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_query():
    print("\n🔍 Testing Query Endpoint...")
    try:
        payload = {"query": "How do I plan my production?"}
        response = requests.post(
            f"{FUNCTION_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Query successful!")
            if "data" in data and "answer" in data["data"]:
                answer = data["data"]["answer"]
                print(f"Answer length: {len(answer)} characters")
                print(f"Answer preview: {answer[:200]}...")
                
                # Check for sections
                sections = ["Strategic Thinking Lens", "Follow-up Prompts", "Concepts/Tools"]
                for section in sections:
                    if section in answer:
                        print(f"✅ Found section: {section}")
                    else:
                        print(f"❌ Missing section: {section}")
                return True
            else:
                print("❌ Unexpected response format")
                return False
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick V1666 Test")
    print("=" * 50)
    
    health_ok = test_health()
    if health_ok:
        test_query()
    else:
        print("❌ Health check failed - stopping tests")