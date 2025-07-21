import requests
import json

# Test the API endpoint with tariff uncertainty question
url = "http://localhost:5000/query"
data = {
    "query": "Under tarrif uncertainty, how do I plan my production?"
}

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print("=== TARIFF UNCERTAINTY API RESPONSE ===")
        print(result.get('data', {}).get('answer', 'No answer found'))
        print("=== END API RESPONSE ===")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error connecting to API: {e}") 