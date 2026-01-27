#!/usr/bin/env python3
"""
Test script to verify ThinkPal V1.6.3 response structure
"""

import query_engine

def test_v163_structure():
    """Test that the V1.6.3 structure is properly enforced"""
    
    # Test query
    test_query = "Should I accept a job offer at a startup or stay at my current corporate job?"
    
    print("🧪 Testing ThinkPal V1.6.3 Response Structure")
    print("=" * 50)
    print(f"Query: {test_query}")
    print()
    
    try:
        # Process the query
        response = query_engine.process_query(test_query)
        
        print("📋 Response Structure Analysis:")
        print("-" * 30)
        
        # Check for required sections
        required_sections = [
            "Strategic Thinking Lens",
            "Story in Action", 
            "Follow-up Prompts",
            "Concepts/Tools"
        ]
        
        for section in required_sections:
            if f"**{section}**" in response:
                print(f"✅ {section}: Found")
            else:
                print(f"❌ {section}: Missing")
        
        print()
        print("📄 Full Response:")
        print("=" * 50)
        print(response)
        
        # Test concept extraction
        print()
        print("🔍 Testing Concept Extraction:")
        print("-" * 30)
        
        if hasattr(query_engine, 'extract_tools_from_section'):
            concepts = query_engine.extract_tools_from_section(response)
            print(f"Found {len(concepts)} concepts:")
            for concept in concepts:
                print(f"  - {concept['term']}: {concept['definition'][:50]}...")
        else:
            print("❌ extract_tools_from_section function not found")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v163_structure() 