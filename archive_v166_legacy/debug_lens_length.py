#!/usr/bin/env python3
"""
Debug script to test the enforce_thinkpal_structure function directly
"""

import re
import query_engine

def test_enforce_structure_directly():
    """Test the enforce_thinkpal_structure function directly"""
    
    # Create a short Strategic Thinking Lens that should trigger fallback
    short_answer = """**Strategic Thinking Lens**

This decision involves strategic thinking about alternatives and trade-offs.

**Story in Action**

Alex considers his options carefully.

**Follow-up Prompts**

- What are your main objectives?
- What are the trade-offs?

**Concepts/Tools**

Decision Matrix: A tool for comparing options
Pros and Cons List: Simple evaluation method"""

    print("🧪 Testing enforce_thinkpal_structure directly")
    print("=" * 60)
    
    print(f"📝 Original answer length: {len(short_answer)} characters")
    
    # Extract original lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', short_answer, re.DOTALL | re.IGNORECASE)
    if lens_match:
        original_lens = lens_match.group(1).strip()
        original_word_count = len(original_lens.split())
        print(f"📊 Original lens word count: {original_word_count}")
    
    # Test the function
    query = "How do I choose between two job offers?"
    result = query_engine.enforce_thinkpal_structure(short_answer, query)
    
    print(f"📝 Result length: {len(result)} characters")
    
    # Extract result lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', result, re.DOTALL | re.IGNORECASE)
    if lens_match:
        result_lens = lens_match.group(1).strip()
        result_word_count = len(result_lens.split())
        print(f"📊 Result lens word count: {result_word_count}")
        
        if result_word_count >= 120:
            print("✅ PASS: Lens was enhanced to meet length requirements")
        else:
            print("❌ FAIL: Lens was not enhanced properly")
            
        print(f"🔍 First 200 chars of result lens: {result_lens[:200]}...")
    else:
        print("❌ FAIL: No Strategic Thinking Lens found in result")

if __name__ == "__main__":
    test_enforce_structure_directly() 