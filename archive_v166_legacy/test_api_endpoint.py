#!/usr/bin/env python3
"""
Test script to test the API endpoint directly
"""
import requests
import json

print("🔍 TESTING API ENDPOINT")
print("=" * 60)

# Test the API endpoint
url = "http://localhost:5000/query"
test_query = "my team members are reluctant to give up his legacy projects, how shall I convience him to think differently?"

payload = {
    "query": test_query,
    "course_id": "decision"
}

print(f"📝 TESTING QUERY: {test_query}")
print(f"🌐 API URL: {url}")
print("=" * 60)

try:
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    
    print(f"📊 RESPONSE STATUS: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response:")
        print(f"   Status: {data.get('status')}")
        print(f"   Answer: {data.get('data', {}).get('answer', 'No answer found')}")
        
        # Check for specific content
        answer = data.get('data', {}).get('answer', '')
        answer_lower = answer.lower()
        
        print(f"\n🔍 CONTENT ANALYSIS:")
        print(f"   Word count: {len(answer.split())} words")
        
        # Check for specific content indicators
        has_behavior_content = any(term in answer_lower for term in ["escalation", "commitment", "prospect theory", "psychological", "bias"])
        print(f"   Human behavior content: {'✅' if has_behavior_content else '❌'}")
        
        has_scenario_content = any(term in answer_lower for term in ["scenario planning", "monte carlo", "simulation"])
        print(f"   Scenario planning content: {'✅' if has_scenario_content else '❌'}")
        
        # Check for specific concepts mentioned
        if "escalation of commitment" in answer_lower:
            print(f"   ✅ Mentions 'Escalation of Commitment'")
        if "prospect theory" in answer_lower:
            print(f"   ✅ Mentions 'Prospect Theory'")
        if "scenario planning" in answer_lower:
            print(f"   ✅ Mentions 'Scenario Planning'")
        if "monte carlo" in answer_lower:
            print(f"   ✅ Mentions 'Monte Carlo'")
        
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n✅ API test complete!") 