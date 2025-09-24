#!/usr/bin/env python3
"""
Test and verify the current fix status
"""

import re
from query_engine import process_query

def test_current_output():
    """Test the current output to see the exact structure"""
    
    print("🔍 TESTING CURRENT OUTPUT")
    print("=" * 40)
    
    query = "How to convey bad news to my boss?"
    result = process_query(query)
    
    print("📋 CURRENT OUTPUT (FIRST 800 CHARS):")
    print(result[:800])
    
    # Count headers
    strategic_lens_count = result.count("**Strategic Thinking Lens**")
    part_count = len(re.findall(r'\*\*Part \d+:', result))
    for_example_count = len(re.findall(r'\*\*For (?:instance|example)[^:]*\*\*', result))
    
    print(f"\n📊 ANALYSIS:")
    print(f"  Strategic Thinking Lens headers: {strategic_lens_count}")
    print(f"  Part subheaders: {part_count}")
    print(f"  'For example' headers: {for_example_count}")
    
    # Check if fixes are working
    if strategic_lens_count == 1:
        print("✅ Duplicate headers: FIXED")
    else:
        print(f"❌ Duplicate headers: STILL PRESENT ({strategic_lens_count} headers)")
    
    if part_count == 0:
        print("✅ Part subheaders: FIXED")
    else:
        print(f"❌ Part subheaders: STILL PRESENT ({part_count} parts)")
    
    if for_example_count > 0:
        print("✅ For example formatting: FIXED")
    else:
        print("❌ For example formatting: NOT FIXED")
    
    return result

def apply_complete_fix():
    """Apply the complete fix to resolve all issues"""
    
    print("\n🔧 APPLYING COMPLETE FIX")
    print("=" * 30)
    
    # The issue is that the original GPT response has the header
    # and the merge function creates content with Part 1/Part 2
    # We need to:
    # 1. Remove the original header from GPT response
    # 2. Remove Part 1/Part 2 subheaders
    # 3. Format For example as header
    
    print("ISSUE IDENTIFIED:")
    print("  - Original GPT response has '**Strategic Thinking Lens**' header")
    print("  - Merge function creates 'Part 1:' and 'Part 2:' structure")
    print("  - Need to remove original header and clean up structure")
    
    print("\nCOMPLETE FIX NEEDED:")
    print("  1. Remove original header from GPT response before merge")
    print("  2. Remove Part 1/Part 2 subheaders after merge")
    print("  3. Format For example as header after merge")
    
    return "Complete fix identified"

if __name__ == "__main__":
    test_current_output()
    apply_complete_fix()
    
    print("\n✅ VERIFICATION COMPLETE")
    print("=" * 30)
    print("Status:")
    print("1. ❌ Duplicate headers still present")
    print("2. ❌ Part subheaders still present") 
    print("3. ❌ For example not formatted as header")
    print("\n📝 NEXT STEP:")
    print("  - Need to remove original header from GPT response")
    print("  - Need to clean up merge function output") 