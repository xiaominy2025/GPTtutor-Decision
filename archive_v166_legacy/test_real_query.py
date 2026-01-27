#!/usr/bin/env python3
"""
Test script to test the actual query_engine.py with a real query
"""

import sys
import os

# Add the current directory to the path so we can import query_engine
sys.path.insert(0, os.getcwd())

# Import the process_query function
from query_engine import process_query

def test_real_query():
    """Test the actual query_engine with a real query"""
    
    # Test query that should trigger entity enhancement
    test_query = "Under tariff uncertainty, how can I optimize the production of my auto parts plant to maximize profit for the next year?"
    
    print("=== TESTING REAL QUERY ===")
    print(f"Query: {test_query}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Process the query
        result = process_query(test_query)
        
        print("=== RESULT ===")
        print(result)
        print("\n" + "="*50 + "\n")
        
        # Analyze the sections
        print("=== SECTION ANALYSIS ===")
        
        import re
        
        # Extract each section to verify they're properly isolated
        sections = {
            'Strategic Thinking Lens': r'\*\*Strategic Thinking Lens\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
            'Story in Action': r'\*\*Story in Action\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
            'Follow-up Prompts': r'\*\*Follow-up Prompts\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
            'Concepts/Tools': r'\*\*Concepts/Tools\*\*.*?(?=\n\*\*[^*]+\*\*|$)'
        }
        
        for section_name, pattern in sections.items():
            match = re.search(pattern, result, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(0)
                print(f"{section_name}:")
                print(f"Length: {len(content)}")
                print(f"Content preview: {content[:100]}...")
                print()
            else:
                print(f"{section_name}: NOT FOUND")
                print()
        
        # Check if sections are bleeding into each other
        print("=== BLEEDING CHECK ===")
        
        # Check if Story in Action contains content from other sections
        story_match = re.search(r'\*\*Story in Action\*\*.*?(?=\n\*\*[^*]+\*\*|$)', result, re.DOTALL | re.IGNORECASE)
        if story_match:
            story_content = story_match.group(0)
            if "Follow-up Prompts" in story_content or "Concepts/Tools" in story_content:
                print("❌ Story in Action is bleeding into other sections")
            else:
                print("✅ Story in Action is properly isolated")
        
        # Check if Follow-up Prompts contains content from other sections
        followup_match = re.search(r'\*\*Follow-up Prompts\*\*.*?(?=\n\*\*[^*]+\*\*|$)', result, re.DOTALL | re.IGNORECASE)
        if followup_match:
            followup_content = followup_match.group(0)
            if "Concepts/Tools" in followup_content:
                print("❌ Follow-up Prompts is bleeding into other sections")
            else:
                print("✅ Follow-up Prompts is properly isolated")
        
        # Check if Concepts/Tools contains content from other sections
        concepts_match = re.search(r'\*\*Concepts/Tools\*\*.*?(?=\n\*\*[^*]+\*\*|$)', result, re.DOTALL | re.IGNORECASE)
        if concepts_match:
            concepts_content = concepts_match.group(0)
            if "Strategic Thinking Lens" in concepts_content or "Story in Action" in concepts_content or "Follow-up Prompts" in concepts_content:
                print("❌ Concepts/Tools is bleeding into other sections")
            else:
                print("✅ Concepts/Tools is properly isolated")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_query() 