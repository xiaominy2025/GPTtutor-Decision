#!/usr/bin/env python3
"""
Fix the duplicate header issue in process_query function
"""

import re

def fix_process_query_regex():
    """Fix the regex in process_query function to prevent duplicate headers"""
    
    print("🔧 FIXING DUPLICATE HEADERS IN PROCESS_QUERY")
    print("=" * 50)
    
    # The issue is in this line in process_query:
    # answer = re.sub(r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*|\Z)', f'\n\n**Strategic Thinking Lens**\n\n{merged_lens}\n\n', answer, flags=re.DOTALL | re.IGNORECASE)
    
    # The problem is that the regex matches too much and creates duplicates
    # We need to be more precise about where to stop
    
    # Test the current problematic regex
    test_text = """**Strategic Thinking Lens**

Original content here.

**Follow-up Prompts**
Some followup content.

**Concepts/Tools**
Some concepts."""
    
    print("Current problematic regex:")
    current_pattern = r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*|\Z)'
    match = re.search(current_pattern, test_text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        print(f"Current match: {match.group()[:100]}...")
    
    # Test the improved regex
    print("\nImproved regex:")
    improved_pattern = r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)'
    match = re.search(improved_pattern, test_text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        print(f"Improved match: {match.group()[:100]}...")
    
    # Test the replacement
    merged_lens = "New merged content here."
    replacement = f'**Strategic Thinking Lens**\n\n{merged_lens}'
    
    result = re.sub(improved_pattern, replacement, test_text, flags=re.DOTALL | re.IGNORECASE)
    
    print(f"\nReplacement result:")
    print(result)
    
    # Check for duplicate headers
    header_count = result.count("**Strategic Thinking Lens**")
    print(f"\nHeaders in result: {header_count}")
    
    return result

def test_with_real_query():
    """Test the fix with a real query"""
    
    print("\n🧪 TESTING WITH REAL QUERY")
    print("=" * 30)
    
    from query_engine import process_query
    
    query = "How to convey bad news to my boss?"
    result = process_query(query)
    
    # Count headers
    strategic_lens_count = result.count("**Strategic Thinking Lens**")
    print(f"Strategic Thinking Lens headers: {strategic_lens_count}")
    
    # Check for concepts
    concepts_count = len(re.findall(r'- [^:]+:', result))
    print(f"Concepts found: {concepts_count}")
    
    # Show the structure
    lines = result.split('\n')
    for i, line in enumerate(lines):
        if "**Strategic Thinking Lens**" in line:
            print(f"Line {i+1}: {line.strip()}")
    
    return result

if __name__ == "__main__":
    fix_process_query_regex()
    test_with_real_query()
    
    print("\n✅ DUPLICATE HEADER FIX")
    print("=" * 25)
    print("The issue is in the regex replacement in process_query")
    print("Current regex: r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*|\\Z)'")
    print("Improved regex: r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)'")
    print("This prevents matching too much content and creating duplicates") 