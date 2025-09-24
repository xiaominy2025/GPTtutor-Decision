#!/usr/bin/env python3
"""
Debug and fix priority issues: missing example content and duplicate headers
"""

import re
from query_engine import process_query

def debug_current_output():
    """Debug the current output to identify issues"""
    
    print("🔍 DEBUGGING CURRENT OUTPUT")
    print("=" * 40)
    
    query = "How to convey bad news to my boss?"
    result = process_query(query)
    
    print("📋 CURRENT OUTPUT:")
    print(result)
    
    # Analyze the structure
    lines = result.split('\n')
    strategic_lens_lines = []
    for_example_lines = []
    
    for i, line in enumerate(lines):
        if "**Strategic Thinking Lens**" in line:
            strategic_lens_lines.append((i+1, line.strip()))
        if "For example" in line or "For instance" in line:
            for_example_lines.append((i+1, line.strip()))
    
    print(f"\n📊 ANALYSIS:")
    print(f"  Strategic Thinking Lens headers: {len(strategic_lens_lines)}")
    for line_num, content in strategic_lens_lines:
        print(f"    Line {line_num}: '{content}'")
    
    print(f"  'For example' lines: {len(for_example_lines)}")
    for line_num, content in for_example_lines:
        print(f"    Line {line_num}: '{content}'")
    
    return result

def identify_root_causes():
    """Identify the root causes of the issues"""
    
    print("\n🔍 ROOT CAUSE ANALYSIS")
    print("=" * 30)
    
    print("1. MISSING EXAMPLE CONTENT:")
    print("   - The merge function should include 'For example' content")
    print("   - But it's being removed or not properly merged")
    print("   - This suggests the merge prompt or post-processing is wrong")
    
    print("\n2. DUPLICATE HEADERS:")
    print("   - Original GPT response has '**Strategic Thinking Lens**'")
    print("   - Regex replacement adds another '**Strategic Thinking Lens**'")
    print("   - The lookbehind regex fix isn't working properly")
    
    return "Root causes identified"

def test_merge_function():
    """Test the merge function to see what it's producing"""
    
    print("\n🧪 TESTING MERGE FUNCTION")
    print("=" * 30)
    
    from query_engine import merge_and_extend_with_story
    
    # Test with sample content
    lens_draft = "When delivering negative news to your boss, applying strategic thinking is paramount."
    story_draft = "For example, when discussing a project delay, provide detailed reasons and proactive solutions."
    
    merged_content = merge_and_extend_with_story(lens_draft, story_draft, 1)
    
    print("LENS DRAFT:")
    print(lens_draft)
    print("\nSTORY DRAFT:")
    print(story_draft)
    print("\nMERGED CONTENT:")
    print(merged_content)
    
    # Check if "For example" is in the merged content
    has_for_example = "For example" in merged_content or "For instance" in merged_content
    print(f"\nContains 'For example': {has_for_example}")
    
    return merged_content

def fix_merge_prompt():
    """Fix the merge prompt to ensure example content is included"""
    
    print("\n🔧 FIXING MERGE PROMPT")
    print("=" * 30)
    
    print("CURRENT MERGE PROMPT ISSUES:")
    print("  - May not be preserving the example content properly")
    print("  - May be creating 'Part 1:' and 'Part 2:' structure")
    print("  - May be removing 'For example' during post-processing")
    
    print("\nPROPOSED FIXES:")
    print("  1. Update merge prompt to explicitly request 'For example' content")
    print("  2. Ensure post-processing doesn't remove example content")
    print("  3. Fix regex replacement to preserve all content")
    
    return "Merge prompt fixes identified"

def fix_regex_replacement():
    """Fix the regex replacement to prevent duplicate headers"""
    
    print("\n🔧 FIXING REGEX REPLACEMENT")
    print("=" * 35)
    
    # Test the current problematic regex
    test_text = """**Strategic Thinking Lens**

Original content here.

**Follow-up Prompts**"""
    
    print("CURRENT PROBLEMATIC REGEX:")
    current_pattern = r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)'
    match = re.search(current_pattern, test_text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        print(f"  Matches: '{match.group()[:50]}...'")
    
    print("\nFIXED REGEX (LOOKBEHIND):")
    fixed_pattern = r'(?<=\*\*Strategic Thinking Lens\*\*).*?(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)'
    match = re.search(fixed_pattern, test_text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        print(f"  Matches: '{match.group()[:50]}...'")
    
    # Test replacement
    merged_lens = "Fixed merged content with example here."
    replacement = f'\n\n{merged_lens}'
    
    result = re.sub(fixed_pattern, replacement, test_text, flags=re.DOTALL | re.IGNORECASE)
    
    print(f"\nREPLACEMENT RESULT:")
    print(result)
    
    header_count = result.count("**Strategic Thinking Lens**")
    print(f"\nHeaders in result: {header_count}")
    
    return result

def create_comprehensive_fix():
    """Create a comprehensive fix for both issues"""
    
    print("\n🔧 COMPREHENSIVE FIX")
    print("=" * 25)
    
    print("1. FIX MISSING EXAMPLE CONTENT:")
    print("   - Update merge prompt to explicitly include 'For example'")
    print("   - Ensure post-processing doesn't remove example content")
    print("   - Add validation to check if example content is preserved")
    
    print("\n2. FIX DUPLICATE HEADERS:")
    print("   - Update process_query regex to use lookbehind:")
    print("   - r'(?<=\\*\\*Strategic Thinking Lens\\*\\*).*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)'")
    print("   - Change replacement to: f'\\n\\n{merged_lens}'")
    
    print("\n3. ADD VALIDATION:")
    print("   - Check if merged content contains 'For example'")
    print("   - Check if only one 'Strategic Thinking Lens' header exists")
    print("   - Log warnings if content is missing")
    
    return "Comprehensive fix created"

if __name__ == "__main__":
    debug_current_output()
    identify_root_causes()
    test_merge_function()
    fix_merge_prompt()
    fix_regex_replacement()
    create_comprehensive_fix()
    
    print("\n✅ DEBUG COMPLETE")
    print("=" * 25)
    print("Priority issues identified:")
    print("1. ❌ Example content missing from Strategic Thinking Lens")
    print("2. ❌ Duplicate headers still appearing")
    print("3. ✅ Root causes identified and fixes proposed") 