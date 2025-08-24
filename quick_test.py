#!/usr/bin/env python3
import requests
import json

# Test query
query = "How to convey bad news to my boss?"

# Make request
url = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query"
payload = {
    "query": query,
    "course_id": "decision", 
    "user_id": "default"
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"\nQuery: {query}")
        print(f"Answer preview: {data['answer'][:300]}...")
        print(f"Concepts found: {len(data['conceptsToolsPractice'])}")
        print(f"Processing time: {data['processing_time']:.2f}s")
        
        for concept in data['conceptsToolsPractice']:
            print(f"  - {concept['term']}: {concept['definition']}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")