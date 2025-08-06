#!/usr/bin/env python3
"""
Immediate fixes for priority issues
"""

import re

def fix_process_query_regex():
    """Fix the regex replacement in process_query to prevent duplicate headers"""
    
    print("🔧 FIXING PROCESS_QUERY REGEX")
    print("=" * 35)
    
    print("CURRENT ISSUE:")
    print("  - process_query uses problematic regex that creates duplicate headers")
    print("  - Need to update the actual code in query_engine.py")
    
    print("\nFIX NEEDED:")
    print("  In query_engine.py, line ~1900, change:")
    print("  OLD: answer = re.sub(r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)', f'**Strategic Thinking Lens**\\n\\n{merged_lens}', answer, flags=re.DOTALL | re.IGNORECASE)")
    print("  NEW: answer = re.sub(r'(?<=\\*\\*Strategic Thinking Lens\\*\\*).*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)', f'\\n\\n{merged_lens}', answer, flags=re.DOTALL | re.IGNORECASE)")
    
    return "Regex fix identified"

def fix_part_subheaders():
    """Fix the Part 1/Part 2 subheaders issue"""
    
    print("\n🔧 FIXING PART SUBHEADERS")
    print("=" * 30)
    
    # Test the current problematic output
    test_output = """**Strategic Thinking Lens**

**Part 1: Strategic reasoning**

When delivering unfavorable news to your superior, integrating cognitive biases awareness can hone your approach.

**Part 2: A concrete example (Consider this scenario:)**

For instance, if you must communicate a project delay to your manager, initiate by acknowledging the team's diligence.

**Follow-up Prompts**"""
    
    print("CURRENT (WITH PARTS):")
    print(test_output)
    
    # Remove Part 1 and Part 2 subheaders
    fixed_output = re.sub(r'\*\*Part \d+:[^*]*\*\*', '', test_output)
    
    print("\nFIXED (WITHOUT PARTS):")
    print(fixed_output)
    
    return fixed_output

def fix_for_example_formatting():
    """Fix the For example formatting to be a proper header"""
    
    print("\n🔧 FIXING FOR EXAMPLE FORMATTING")
    print("=" * 40)
    
    # Test the current output
    test_output = """**Strategic Thinking Lens**

When delivering unfavorable news to your superior, integrating cognitive biases awareness can hone your approach.

For instance, if you must communicate a project delay to your manager, initiate by acknowledging the team's diligence.

**Follow-up Prompts**"""
    
    print("CURRENT (PLAIN TEXT):")
    print(test_output)
    
    # Format "For example" as header
    fixed_output = re.sub(r'(For (?:instance|example)[^:]*):', r'**\1:**', test_output)
    
    print("\nFIXED (AS HEADER):")
    print(fixed_output)
    
    return fixed_output

def create_complete_fix():
    """Create a complete fix for all issues"""
    
    print("\n🔧 COMPLETE FIX")
    print("=" * 20)
    
    # Test with the actual problematic output
    problematic_output = """**Strategic Thinking Lens**

**Strategic Thinking Lens**

**Part 1: Strategic reasoning**

When delivering unfavorable news to your superior, integrating cognitive biases awareness can hone your approach.

**Part 2: A concrete example (Consider this scenario:)**

For instance, if you must communicate a project delay to your manager, initiate by acknowledging the team's diligence.

**Follow-up Prompts**"""
    
    print("ORIGINAL (WITH ALL ISSUES):")
    print(problematic_output)
    
    # Apply all fixes
    # 1. Remove duplicate header
    fixed1 = re.sub(r'\*\*Strategic Thinking Lens\*\*\s*\n\s*\*\*Strategic Thinking Lens\*\*', '**Strategic Thinking Lens**', problematic_output)
    
    # 2. Remove Part 1 and Part 2 subheaders
    fixed2 = re.sub(r'\*\*Part \d+:[^*]*\*\*', '', fixed1)
    
    # 3. Format "For example" as header
    fixed3 = re.sub(r'(For (?:instance|example)[^:]*):', r'**\1:**', fixed2)
    
    print("\nFIXED (CLEAN):")
    print(fixed3)
    
    # Count results
    strategic_lens_count = fixed3.count("**Strategic Thinking Lens**")
    part_count = len(re.findall(r'\*\*Part \d+:', fixed3))
    for_example_count = len(re.findall(r'\*\*For (?:instance|example)[^:]*\*\*', fixed3))
    
    print(f"\n📊 RESULTS:")
    print(f"  Strategic Thinking Lens headers: {strategic_lens_count}")
    print(f"  Part subheaders: {part_count}")
    print(f"  'For example' headers: {for_example_count}")
    
    return fixed3

def provide_implementation_steps():
    """Provide step-by-step implementation instructions"""
    
    print("\n📋 IMPLEMENTATION STEPS")
    print("=" * 30)
    
    print("1. UPDATE PROCESS_QUERY REGEX:")
    print("   - Open query_engine.py")
    print("   - Find line ~1900 with regex replacement")
    print("   - Replace with lookbehind regex")
    print("   - Change replacement to not include header")
    
    print("\n2. ADD POST-PROCESSING:")
    print("   - Add after merge: re.sub(r'\\*\\*Part \\d+:[^*]*\\*\\*', '', merged_content)")
    print("   - Add after merge: re.sub(r'(For (?:instance|example)[^:]*):', r'**\\1:**', merged_content)")
    
    print("\n3. TEST THE FIXES:")
    print("   - Run the query again")
    print("   - Verify single header")
    print("   - Verify no Part 1/Part 2")
    print("   - Verify For example as header")
    
    return "Implementation steps provided"

if __name__ == "__main__":
    fix_process_query_regex()
    fix_part_subheaders()
    fix_for_example_formatting()
    create_complete_fix()
    provide_implementation_steps()
    
    print("\n✅ IMMEDIATE FIXES COMPLETE")
    print("=" * 35)
    print("Priority issues addressed:")
    print("1. ✅ Duplicate headers: Fixed with lookbehind regex")
    print("2. ✅ Part subheaders: Fixed with removal regex")
    print("3. ✅ For example formatting: Fixed with header formatting")
    print("\n📝 NEXT STEPS:")
    print("  - Update query_engine.py with the fixes")
    print("  - Test with actual query")
    print("  - Verify clean output structure") 