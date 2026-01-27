#!/usr/bin/env python3
"""
Simple test script for the grammar and clarity filtering functions
"""

import re
from typing import List, Tuple, Dict

def detect_repetitive_patterns(text: str) -> List[Tuple[str, str]]:
    """Detect and return repetitive opening patterns that should be varied"""
    repetitive_patterns = [
        (r'\bWhen considering\b', "When considering"),
        (r'\bIt\'s essential to\b', "It's essential to"),
        (r'\bIt is important to\b', "It is important to"),
        (r'\bIn order to\b', "In order to"),
        (r'\bTo properly\b', "To properly"),
        (r'\bWhen making\b', "When making"),
        (r'\bWhen faced with\b', "When faced with"),
        (r'\bWhen dealing with\b', "When dealing with"),
        (r'\bWhen evaluating\b', "When evaluating"),
        (r'\bWhen analyzing\b', "When analyzing")
    ]
    
    found_patterns = []
    for pattern, description in repetitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_patterns.append((pattern, description))
    
    return found_patterns

def detect_grammar_fragments(text: str) -> List[Tuple[str, str]]:
    """Detect common grammar fragments and awkward phrasing"""
    fragment_patterns = [
        (r'\bindividual, a professional\b', "individual, a professional"),
        (r'\bindividual, an expert\b', "individual, an expert"),
        (r'\bperson, a manager\b', "person, a manager"),
        (r'\bindividual, a decision-maker\b', "individual, a decision-maker"),
        (r'\bindividual, a leader\b', "individual, a leader"),
        (r'\bindividual, a student\b', "individual, a student"),
        (r'\bindividual, a business\b', "individual, a business"),
        (r'\bindividual, a company\b', "individual, a company"),
        (r'\bindividual, an organization\b', "individual, an organization"),
        (r'\bindividual, a team\b', "individual, a team"),
        # Add more fragment patterns
        (r'\bdecision, a choice\b', "decision, a choice"),
        (r'\boption, a possibility\b', "option, a possibility"),
        (r'\bstrategy, a plan\b', "strategy, a plan"),
        (r'\bapproach, a method\b', "approach, a method"),
        (r'\bprocess, a procedure\b', "process, a procedure")
    ]
    
    found_fragments = []
    for pattern, description in fragment_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_fragments.append((pattern, description))
    
    return found_fragments

def detect_awkward_phrasing(text: str) -> List[Tuple[str, str]]:
    """Detect awkward or robotic phrasing patterns"""
    awkward_patterns = [
        (r'\bIt is worth noting that\b', "It is worth noting that"),
        (r'\bIt should be mentioned that\b', "It should be mentioned that"),
        (r'\bIt is important to note that\b', "It is important to note that"),
        (r'\bIt is crucial to understand that\b', "It is crucial to understand that"),
        (r'\bIt is necessary to consider that\b', "It is necessary to consider that"),
        (r'\bIt is essential to recognize that\b', "It is essential to recognize that"),
        (r'\bIt is vital to acknowledge that\b', "It is vital to acknowledge that"),
        (r'\bIt is imperative to realize that\b', "It is imperative to realize that"),
        (r'\bIt is critical to understand that\b', "It is critical to understand that"),
        (r'\bIt is fundamental to consider that\b', "It is fundamental to consider that"),
        # Robotic patterns
        (r'\bIn conclusion\b', "In conclusion"),
        (r'\bTo summarize\b', "To summarize"),
        (r'\bAs previously mentioned\b', "As previously mentioned"),
        (r'\bAs stated earlier\b', "As stated earlier"),
        (r'\bAs mentioned before\b', "As mentioned before"),
        (r'\bAs discussed above\b', "As discussed above"),
        (r'\bAs outlined previously\b', "As outlined previously"),
        (r'\bAs indicated earlier\b', "As indicated earlier"),
        (r'\bAs noted before\b', "As noted before"),
        (r'\bAs described above\b', "As described above")
    ]
    
    found_awkward = []
    for pattern, description in awkward_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            found_awkward.append((pattern, description))
    
    return found_awkward

def fix_grammar_fragments(text: str) -> str:
    """Automatically fix common grammar fragments"""
    # Fix "individual, a professional" patterns
    text = re.sub(r'\bindividual, a professional\b', "a professional", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, an expert\b', "an expert", text, flags=re.IGNORECASE)
    text = re.sub(r'\bperson, a manager\b', "a manager", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a decision-maker\b', "a decision-maker", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a leader\b', "a leader", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a student\b', "a student", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a business\b', "a business", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a company\b', "a company", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, an organization\b', "an organization", text, flags=re.IGNORECASE)
    text = re.sub(r'\bindividual, a team\b', "a team", text, flags=re.IGNORECASE)
    
    # Fix other fragment patterns
    text = re.sub(r'\bdecision, a choice\b', "a choice", text, flags=re.IGNORECASE)
    text = re.sub(r'\boption, a possibility\b', "a possibility", text, flags=re.IGNORECASE)
    text = re.sub(r'\bstrategy, a plan\b', "a plan", text, flags=re.IGNORECASE)
    text = re.sub(r'\bapproach, a method\b', "a method", text, flags=re.IGNORECASE)
    text = re.sub(r'\bprocess, a procedure\b', "a procedure", text, flags=re.IGNORECASE)
    
    return text

def improve_repetitive_openings(text: str) -> str:
    """Replace repetitive opening patterns with varied alternatives"""
    import random
    
    # Define replacement patterns
    replacements = {
        r'\bWhen considering\b': [
            "What should you do when",
            "Let's map this out together.",
            "Think of this like",
            "Here's a practical approach:",
            "Consider this scenario:"
        ],
        r'\bIt\'s essential to\b': [
            "The key is to",
            "What matters most is",
            "Your focus should be on",
            "The real question is",
            "Here's what you need to do:"
        ],
        r'\bIt is important to\b': [
            "Keep in mind that",
            "Remember that",
            "The crucial point is",
            "What you should know is",
            "Here's what to consider:"
        ],
        r'\bIn order to\b': [
            "To",
            "So that you can",
            "With the goal of",
            "Aiming to",
            "Working toward"
        ]
    }
    
    improved_text = text
    for pattern, alternatives in replacements.items():
        if re.search(pattern, improved_text, re.IGNORECASE):
            replacement = random.choice(alternatives)
            improved_text = re.sub(pattern, replacement, improved_text, flags=re.IGNORECASE)
    
    return improved_text

def apply_grammar_and_clarity_filters(answer: str) -> Tuple[str, Dict[str, List[str]]]:
    """Apply comprehensive grammar and clarity filtering"""
    issues = {
        "repetitive_patterns": [],
        "grammar_fragments": [],
        "awkward_phrasing": []
    }
    
    # Detect issues
    repetitive = detect_repetitive_patterns(answer)
    fragments = detect_grammar_fragments(answer)
    awkward = detect_awkward_phrasing(answer)
    
    # Record issues
    for pattern, description in repetitive:
        issues["repetitive_patterns"].append(description)
    
    for pattern, description in fragments:
        issues["grammar_fragments"].append(description)
    
    for pattern, description in awkward:
        issues["awkward_phrasing"].append(description)
    
    # Apply fixes
    improved_answer = answer
    improved_answer = fix_grammar_fragments(improved_answer)
    improved_answer = improve_repetitive_openings(improved_answer)
    
    return improved_answer, issues

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