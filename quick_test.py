#!/usr/bin/env python3
"""
Quick test to verify Strategic Thinking Lens enhancement
"""

import query_engine
import re

def test_strategic_thinking_lens():
    """Test that Strategic Thinking Lens is comprehensive and detailed"""
    
    print("🧪 Testing Strategic Thinking Lens Enhancement")
    print("=" * 50)
    
    # Test query
    test_query = "Should I invest in stocks or bonds?"
    
    print(f"📝 Query: {test_query}")
    print("-" * 30)
    
    try:
        # Generate response
        response = query_engine.process_query(test_query)
        
        # Extract Strategic Thinking Lens section
        strategic_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n\n(.*?)(?=\n\n\*\*Story in Action\*\*|$)', response, re.DOTALL)
        
        if strategic_match:
            strategic_content = strategic_match.group(1).strip()
            word_count = len(strategic_content.split())
            
            print(f"✅ Strategic Thinking Lens found")
            print(f"📊 Word count: {word_count} words")
            
            # Check if it meets the enhanced requirements
            if word_count >= 150:
                print("✅ Meets minimum length requirement (150+ words)")
            else:
                print(f"❌ Below minimum length requirement (need 150+, got {word_count})")
            
            # Check for subsections
            subsections = re.findall(r'\*\*([^*]+):\*\*', strategic_content)
            if subsections:
                print(f"✅ Contains {len(subsections)} subsections:")
                for subsection in subsections:
                    print(f"   • {subsection}")
            else:
                print("⚠️ No subsections found")
            
            # Check for forbidden phrases
            forbidden_phrases = ["strategic mindset", "human behavior awareness", "analytical tools"]
            found_forbidden = []
            for phrase in forbidden_phrases:
                if phrase.lower() in strategic_content.lower():
                    found_forbidden.append(phrase)
            
            if found_forbidden:
                print(f"❌ Found forbidden phrases: {found_forbidden}")
            else:
                print("✅ No forbidden phrases detected")
            
            print("\n📄 Content Preview:")
            print("-" * 30)
            print(strategic_content[:300] + "..." if len(strategic_content) > 300 else strategic_content)
            
        else:
            print("❌ Strategic Thinking Lens section not found")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_strategic_thinking_lens() 