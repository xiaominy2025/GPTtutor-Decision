#!/usr/bin/env python3
"""
Detailed test to check Strategic Thinking Lens enhancement process
"""

import re
import query_engine

def test_detailed_lens_enhancement():
    """Test the complete process from query to enhanced lens"""
    
    query = "How do I choose between two job offers?"
    
    print("🧪 Testing Complete Strategic Thinking Lens Enhancement Process")
    print("=" * 70)
    
    print(f"📝 Query: {query}")
    
    # Step 1: Process the query
    print("\n📋 Step 1: Processing query...")
    result = query_engine.process_query(query)
    
    print(f"📊 Result length: {len(result)} characters")
    
    # Step 2: Extract Strategic Thinking Lens
    print("\n📋 Step 2: Extracting Strategic Thinking Lens...")
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', result, re.DOTALL | re.IGNORECASE)
    
    if lens_match:
        lens_content = lens_match.group(1).strip()
        word_count = len(lens_content.split())
        
        print(f"📊 Lens word count: {word_count}")
        print(f"📊 Target range: 120-160 words")
        
        if 120 <= word_count <= 160:
            print("✅ PASS: Lens meets length requirements")
        elif word_count < 100:
            print("❌ FAIL: Lens is too short and should have been enhanced")
        elif word_count < 120:
            print("⚠️  WARNING: Lens is below minimum but above threshold")
        elif word_count > 160:
            print("⚠️  WARNING: Lens is above maximum")
        
        # Check content quality
        has_tradeoffs = any(word in lens_content.lower() for word in ['trade', 'balance', 'weigh', 'versus', 'against'])
        has_multiple_domains = len(re.findall(r'\b(strategic|analytical|behavioral|technical|negotiation|operations|startup|admission|job)\b', lens_content.lower())) >= 2
        
        print(f"🔍 Tradeoffs mentioned: {'✅' if has_tradeoffs else '❌'}")
        print(f"🔍 Multiple domains: {'✅' if has_multiple_domains else '❌'}")
        
        # Show first 300 characters
        print(f"📄 First 300 chars: {lens_content[:300]}...")
        
    else:
        print("❌ FAIL: No Strategic Thinking Lens section found")
    
    # Step 3: Test enforce_thinkpal_structure directly
    print("\n📋 Step 3: Testing enforce_thinkpal_structure directly...")
    
    # Create a mock short answer
    short_answer = """**Strategic Thinking Lens**

This decision involves strategic thinking.

**Story in Action**

Alex considers options.

**Follow-up Prompts**

- What are your objectives?

**Concepts/Tools**

Decision Matrix: A comparison tool"""
    
    enhanced_result = query_engine.enforce_thinkpal_structure(short_answer, query)
    
    # Extract enhanced lens
    enhanced_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', enhanced_result, re.DOTALL | re.IGNORECASE)
    
    if enhanced_match:
        enhanced_lens = enhanced_match.group(1).strip()
        enhanced_word_count = len(enhanced_lens.split())
        
        print(f"📊 Enhanced lens word count: {enhanced_word_count}")
        
        if 120 <= enhanced_word_count <= 160:
            print("✅ PASS: Direct enhancement works correctly")
        else:
            print("❌ FAIL: Direct enhancement failed")
            
        print(f"📄 First 300 chars of enhanced lens: {enhanced_lens[:300]}...")
    
    print("\n" + "=" * 70)
    print("🏁 Detailed Lens Enhancement Test Complete")

if __name__ == "__main__":
    test_detailed_lens_enhancement() 