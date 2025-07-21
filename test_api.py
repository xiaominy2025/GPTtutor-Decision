import requests
import json

# Test the API endpoint
url = "http://localhost:5000/query"
data = {
    "query": "I'm offered a new job. How to decide to accept it or not?"
}

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print("=== FULL API RESPONSE ===")
        print(json.dumps(result, indent=2))
        print("=== END FULL API RESPONSE ===")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error connecting to API: {e}") 