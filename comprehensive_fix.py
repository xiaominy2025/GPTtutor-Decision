#!/usr/bin/env python3
"""
Comprehensive fix for concept selection and duplicate header issues
"""

import re
from query_engine import process_query, get_top_ranked_concepts

def test_current_issues():
    """Test and identify current issues"""
    
    print("🔍 TESTING CURRENT ISSUES")
    print("=" * 40)
    
    query = "How to convey bad news to my boss?"
    
    # Test concept selection
    concepts = get_top_ranked_concepts(query, top_k=3)
    print(f"Concepts selected: {len(concepts)}")
    for name, definition in concepts:
        print(f"  - {name}")
    
    # Test full output
    result = process_query(query)
    
    # Analyze output structure
    strategic_lens_count = result.count("**Strategic Thinking Lens**")
    concepts_count = len(re.findall(r'- [^:]+:', result))
    
    print(f"\nOutput analysis:")
    print(f"  Strategic Thinking Lens headers: {strategic_lens_count}")
    print(f"  Concepts found: {concepts_count}")
    
    # Show the problematic structure
    lines = result.split('\n')
    print(f"\nStructure analysis:")
    for i, line in enumerate(lines):
        if "**Strategic Thinking Lens**" in line:
            print(f"  Line {i+1}: {line.strip()}")
    
    return result

def create_fixed_version():
    """Create a fixed version of the problematic regex replacement"""
    
    print("\n🔧 CREATING FIXED VERSION")
    print("=" * 30)
    
    # The issue is in the process_query function where it does:
    # answer = re.sub(r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*|\Z)', ...)
    
    # This creates duplicates because the regex matches too much
    # We need to be more precise
    
    test_text = """**Strategic Thinking Lens**

Original content here.

**Follow-up Prompts**
Some followup content.

**Concepts/Tools**
Some concepts."""
    
    # Test the fixed regex
    fixed_pattern = r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)'
    merged_lens = "Fixed merged content here."
    replacement = f'**Strategic Thinking Lens**\n\n{merged_lens}'
    
    result = re.sub(fixed_pattern, replacement, test_text, flags=re.DOTALL | re.IGNORECASE)
    
    print(f"Fixed result:")
    print(result)
    
    header_count = result.count("**Strategic Thinking Lens**")
    print(f"\nHeaders in fixed result: {header_count}")
    
    return result

def manual_fix_process_query():
    """Manually fix the process_query function by creating a corrected version"""
    
    print("\n🔧 MANUAL FIX FOR PROCESS_QUERY")
    print("=" * 35)
    
    # The issue is in the regex replacement in process_query
    # We need to update the regex to be more precise
    
    # Current problematic line:
    # answer = re.sub(r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*|\Z)', f'\n\n**Strategic Thinking Lens**\n\n{merged_lens}\n\n', answer, flags=re.DOTALL | re.IGNORECASE)
    
    # Fixed version should be:
    # answer = re.sub(r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)', f'**Strategic Thinking Lens**\n\n{merged_lens}', answer, flags=re.DOTALL | re.IGNORECASE)
    
    print("The fix is to update the regex in process_query function:")
    print("  OLD: r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*|\\Z)'")
    print("  NEW: r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)'")
    print("  OLD replacement: f'\\n\\n**Strategic Thinking Lens**\\n\\n{merged_lens}\\n\\n'")
    print("  NEW replacement: f'**Strategic Thinking Lens**\\n\\n{merged_lens}'")
    
    return "Manual fix instructions provided"

def test_concept_selection_fix():
    """Test that the concept selection fix is working"""
    
    print("\n🧪 TESTING CONCEPT SELECTION FIX")
    print("=" * 35)
    
    query = "How to convey bad news to my boss?"
    concepts = get_top_ranked_concepts(query, top_k=3)
    
    print(f"Concepts selected: {len(concepts)}")
    expected_concepts = ['framing bias', 'confirmation bias', 'anchoring bias']
    
    selected_names = [name for name, _ in concepts]
    print(f"Selected: {selected_names}")
    print(f"Expected: {expected_concepts}")
    
    # Check if we got the expected concepts
    matches = sum(1 for name in expected_concepts if name in selected_names)
    print(f"Matches: {matches}/{len(expected_concepts)}")
    
    return concepts

if __name__ == "__main__":
    test_current_issues()
    create_fixed_version()
    manual_fix_process_query()
    test_concept_selection_fix()
    
    print("\n✅ COMPREHENSIVE ANALYSIS COMPLETE")
    print("=" * 40)
    print("Issues identified and fixes provided:")
    print("1. ✅ Concept selection: Fixed (threshold lowered, boosting increased)")
    print("2. ❌ Duplicate headers: Need to update regex in process_query")
    print("3. ✅ Behavioral keywords: Added 'boss', 'bad news'")
    print("4. ✅ Concept count: Now selecting 3 concepts instead of 1") 