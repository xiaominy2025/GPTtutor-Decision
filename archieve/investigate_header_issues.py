#!/usr/bin/env python3
"""
Investigate the multiple header issues and "For instance" formatting
"""

import re
from query_engine import process_query

def analyze_header_issues():
    """Analyze the multiple header issues"""
    
    print("🔍 INVESTIGATING HEADER ISSUES")
    print("=" * 50)
    
    query = "How to convey bad news to my boss?"
    result = process_query(query)
    
    # Split into lines to analyze structure
    lines = result.split('\n')
    
    print("📋 OUTPUT STRUCTURE ANALYSIS:")
    print("-" * 40)
    
    strategic_lens_lines = []
    for i, line in enumerate(lines):
        if "**Strategic Thinking Lens**" in line:
            strategic_lens_lines.append((i+1, line.strip()))
        if "For instance" in line or "For example" in line:
            print(f"Line {i+1}: '{line.strip()}'")
    
    print(f"\nStrategic Thinking Lens headers found at lines:")
    for line_num, line_content in strategic_lens_lines:
        print(f"  Line {line_num}: '{line_content}'")
    
    # Analyze the issue
    print(f"\n🔍 ISSUE ANALYSIS:")
    print("-" * 20)
    
    if len(strategic_lens_lines) == 2:
        print("✅ CONFIRMED: Two Strategic Thinking Lens headers")
        print("  - Line 1: Original header from GPT response")
        print("  - Line 3: New header from regex replacement")
        print("\n❌ PROBLEM: The regex replacement is creating a duplicate header")
        print("  Current regex: r'\\*\\*Strategic Thinking Lens\\*\\*.*?(?=\\*\\*Follow-up Prompts\\*\\*|\\*\\*Concepts/Tools\\*\\*|\\Z)'")
        print("  This regex matches the original header and replaces it with a new one")
    
    return result

def analyze_for_instance_formatting():
    """Analyze the "For instance" formatting issue"""
    
    print("\n🔍 ANALYZING 'FOR INSTANCE' FORMATTING")
    print("=" * 50)
    
    query = "How to convey bad news to my boss?"
    result = process_query(query)
    
    # Find "For instance" or "For example" patterns
    for_instance_patterns = re.findall(r'For (?:instance|example)[^:]*:', result)
    for_instance_text = re.findall(r'For (?:instance|example)[^:]*', result)
    
    print(f"Found patterns:")
    for pattern in for_instance_patterns:
        print(f"  - '{pattern}'")
    
    print(f"\nFound text:")
    for text in for_instance_text:
        print(f"  - '{text}'")
    
    # Check if any are formatted as headers
    header_patterns = re.findall(r'\*\*For (?:instance|example)[^:]*\*\*', result)
    print(f"\nHeader patterns:")
    for pattern in header_patterns:
        print(f"  - '{pattern}'")
    
    print(f"\n🔍 FORMATTING ANALYSIS:")
    print("-" * 25)
    print("❌ PROBLEM: 'For instance' is not formatted as a header")
    print("  Current: 'For instance:' (plain text)")
    print("  Should be: '**For instance:**' (markdown header)")
    print("\n📝 UI INTERPRETATION:")
    print("  - '**For instance:**' would be interpreted as a bold header")
    print("  - 'For instance:' is just plain text")
    print("  - The UI expects markdown formatting for headers")
    
    return result

def identify_root_causes():
    """Identify the root causes of the issues"""
    
    print("\n🔍 ROOT CAUSE ANALYSIS")
    print("=" * 30)
    
    print("1. DUPLICATE HEADERS:")
    print("   - Original GPT response contains '**Strategic Thinking Lens**'")
    print("   - Regex replacement adds another '**Strategic Thinking Lens**'")
    print("   - Result: Two headers instead of one")
    print()
    print("2. 'FOR INSTANCE' FORMATTING:")
    print("   - Merge function creates 'For instance:' as plain text")
    print("   - Should create '**For instance:**' as markdown header")
    print("   - UI expects markdown formatting for proper display")
    print()
    print("3. CONCEPTS NOT APPEARING:")
    print("   - Concepts are selected but not properly formatted in output")
    print("   - May be related to concept extraction from merged content")
    
    return "Root causes identified"

def propose_fixes():
    """Propose specific fixes for the issues"""
    
    print("\n🔧 PROPOSED FIXES")
    print("=" * 20)
    
    print("1. FIX DUPLICATE HEADERS:")
    print("   - Update regex to NOT include header in replacement")
    print("   - Current: f'**Strategic Thinking Lens**\\n\\n{merged_lens}'")
    print("   - Fixed: f'{merged_lens}' (let original header remain)")
    print()
    print("2. FIX 'FOR INSTANCE' FORMATTING:")
    print("   - Update merge prompt to request markdown headers")
    print("   - Add post-processing to format connectors as headers")
    print("   - Ensure 'For instance:' becomes '**For instance:**'")
    print()
    print("3. FIX CONCEPTS NOT APPEARING:")
    print("   - Check concept extraction from merged content")
    print("   - Ensure concepts are properly formatted in output")
    print("   - May need to extract concepts before merging")
    
    return "Fixes proposed"

if __name__ == "__main__":
    analyze_header_issues()
    analyze_for_instance_formatting()
    identify_root_causes()
    propose_fixes()
    
    print("\n✅ INVESTIGATION COMPLETE")
    print("=" * 30)
    print("Issues identified and fixes proposed:")
    print("1. Duplicate headers from regex replacement")
    print("2. 'For instance' not formatted as markdown header")
    print("3. Concepts not appearing in final output") 