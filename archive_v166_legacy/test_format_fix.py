#!/usr/bin/env python3
"""
Test script to verify the new answer format
"""

from query_engine import process_query

def test_new_format():
    """Test the new answer format"""
    query = "I need to decide between two job offers"
    
    print("🧪 Testing New Answer Format")
    print("=" * 50)
    print(f"Query: {query}")
    print("\n📝 Answer:")
    print("=" * 50)
    
    try:
        answer = process_query(query)
        print(answer)
        print("=" * 50)
        
        # Check for required sections
        required_sections = [
            "**Strategy or Explanation**",
            "**Story in Action**", 
            "**Follow-up Prompts**",
            "**Concept & Tool**"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in answer:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections: {missing_sections}")
            return False
        else:
            print("✅ All required sections present")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_new_format() 