#!/usr/bin/env python3
"""
Test script for the grammar and clarity filtering functions
"""

import sys
import os

# Add the current directory to the path so we can import from query_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the filtering functions
from query_engine import (
    detect_repetitive_patterns,
    detect_grammar_fragments,
    detect_awkward_phrasing,
    fix_grammar_fragments,
    improve_repetitive_openings,
    apply_grammar_and_clarity_filters
)

def test_grammar_filters():
    """Test the grammar and clarity filtering functions"""
    
    print("🧪 Testing Grammar and Clarity Filters")
    print("=" * 50)
    
    # Test cases with problematic text
    test_cases = [
        {
            "name": "Repetitive Patterns",
            "text": "When considering this decision, it's essential to evaluate all options. When considering the alternatives, it is important to weigh the pros and cons.",
            "expected_issues": ["repetitive_patterns"]
        },
        {
            "name": "Grammar Fragments",
            "text": "individual, a professional in the field, should consider the options. person, a manager, needs to evaluate the situation.",
            "expected_issues": ["grammar_fragments"]
        },
        {
            "name": "Awkward Phrasing",
            "text": "It is worth noting that the decision is complex. It is important to note that this requires careful consideration.",
            "expected_issues": ["awkward_phrasing"]
        },
        {
            "name": "Mixed Issues",
            "text": "When considering this choice, individual, a professional, should note that it is worth noting that the options are limited.",
            "expected_issues": ["repetitive_patterns", "grammar_fragments", "awkward_phrasing"]
        },
        {
            "name": "Clean Text",
            "text": "What should you do when faced with this decision? Let's map this out together. A professional should consider all options carefully.",
            "expected_issues": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        print(f"Original text: {test_case['text']}")
        
        # Apply filters
        improved_text, issues = apply_grammar_and_clarity_filters(test_case['text'])
        
        print(f"\nImproved text: {improved_text}")
        
        # Check if issues were detected
        detected_issues = []
        for issue_type, issue_list in issues.items():
            if issue_list:
                detected_issues.append(issue_type)
        
        print(f"\nDetected issues: {detected_issues}")
        print(f"Expected issues: {test_case['expected_issues']}")
        
        # Verify results
        if set(detected_issues) == set(test_case['expected_issues']):
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")
            print(f"   Expected: {test_case['expected_issues']}")
            print(f"   Got: {detected_issues}")
        
        # Show specific issues found
        for issue_type, issue_list in issues.items():
            if issue_list:
                print(f"   • {issue_type}: {', '.join(issue_list)}")

def test_individual_functions():
    """Test individual filtering functions"""
    
    print("\n🔍 Testing Individual Functions")
    print("=" * 50)
    
    # Test repetitive pattern detection
    text = "When considering this decision, it's essential to evaluate options."
    patterns = detect_repetitive_patterns(text)
    print(f"Repetitive patterns in '{text}': {[desc for _, desc in patterns]}")
    
    # Test grammar fragment detection
    text = "individual, a professional, should consider the options."
    fragments = detect_grammar_fragments(text)
    print(f"Grammar fragments in '{text}': {[desc for _, desc in fragments]}")
    
    # Test awkward phrasing detection
    text = "It is worth noting that this is important."
    awkward = detect_awkward_phrasing(text)
    print(f"Awkward phrasing in '{text}': {[desc for _, desc in awkward]}")
    
    # Test fragment fixing
    text = "individual, a professional, should consider individual, an expert, opinion."
    fixed = fix_grammar_fragments(text)
    print(f"Fixed fragments: '{text}' -> '{fixed}'")
    
    # Test repetitive opening improvement
    text = "When considering this decision, it's essential to evaluate options."
    improved = improve_repetitive_openings(text)
    print(f"Improved openings: '{text}' -> '{improved}'")

if __name__ == "__main__":
    test_grammar_filters()
    test_individual_functions()
    
    print("\n✅ Grammar and clarity filtering tests completed!") 