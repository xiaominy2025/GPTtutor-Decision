#!/usr/bin/env python3
"""
Fix V1666 Response Format Issue
"""

import requests
import json

# Function URL
FUNCTION_URL = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws"

def test_current_response():
    """Test current response format"""
    print("🔍 Testing Current Response Format")
    print("=" * 80)
    
    query = "How do I plan my production?"
    payload = {"query": query}
    
    try:
        response = requests.post(
            f"{FUNCTION_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received")
            print(f"Response structure: {list(data.keys())}")
            
            if "data" in data:
                answer_data = data["data"]
                print(f"Data structure: {list(answer_data.keys())}")
                
                if "answer" in answer_data:
                    answer = answer_data["answer"]
                    print(f"Answer length: {len(answer)} characters")
                    print(f"Answer preview: {answer[:200]}...")
                    
                    # Check for structured fields
                    structured_fields = ["strategicThinkingLens", "followUpPrompts", "conceptsToolsPractice"]
                    for field in structured_fields:
                        if field in answer_data:
                            print(f"✅ Found structured field: {field}")
                            print(f"   Content: {answer_data[field]}")
                        else:
                            print(f"❌ Missing structured field: {field}")
                else:
                    print("❌ No 'answer' field in data")
            else:
                print("❌ No 'data' field in response")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_expected_format():
    """Test what the expected format should be"""
    print("\n🎯 Expected Response Format")
    print("=" * 80)
    
    # The expected format should be a single answer with embedded sections
    expected_sections = [
        "Strategic Thinking Lens",
        "Follow-up Prompts", 
        "Concepts/Tools"
    ]
    
    print("Expected answer should contain these sections:")
    for section in expected_sections:
        print(f"  - {section}")
    
    print("\nExpected format:")
    print("""
**Strategic Thinking Lens**
[Strategic narrative in paragraph form]

**Follow-up Prompts**
1. [Question about specific application]
2. [Question about implementation]  
3. [Question about monitoring/adaptation]

**Concepts/Tools**
- **Concept Name**: Brief definition
- **Tool Name**: Brief definition
    """)

def analyze_issue():
    """Analyze the root cause of the issue"""
    print("\n🔍 Issue Analysis")
    print("=" * 80)
    
    print("Root Cause: The V1666 system is working correctly but returning structured data")
    print("instead of a formatted text response with embedded sections.")
    print()
    print("Current flow:")
    print("1. ✅ Query processed correctly")
    print("2. ✅ OpenAI API call successful") 
    print("3. ✅ Structured data extracted")
    print("4. ❌ Response not formatted as expected text")
    print()
    print("Fix needed: Modify process_query_v166 to return formatted text instead of structured data")

def main():
    print("🚀 V1666 Response Format Investigation")
    print("=" * 80)
    
    test_current_response()
    test_expected_format()
    analyze_issue()
    
    print("\n📋 Next Steps:")
    print("1. Modify process_query_v166 to return formatted text")
    print("2. Update Lambda function to handle the new format")
    print("3. Test with the three development queries")
    print("4. Verify all sections are present in the response")

if __name__ == "__main__":
    main()
