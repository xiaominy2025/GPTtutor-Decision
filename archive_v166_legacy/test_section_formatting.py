#!/usr/bin/env python3
"""
Test script to demonstrate and fix the section formatting issue
"""

import re

def test_section_extraction():
    """Test the current section extraction patterns"""
    
    # Sample answer with sections that should be properly separated
    sample_answer = """**Strategic Thinking Lens**

This is the strategic thinking lens content.

**Story in Action**

This is the story content with some details.

**Follow-up Prompts**

- First follow-up question?
- Second follow-up question?
- Third follow-up question?

**Concepts/Tools**

Linear Optimization: A mathematical method for maximizing or minimizing a linear objective function.
Scenario Analysis: A method that explores different hypothetical futures.
"""

    print("=== ORIGINAL ANSWER ===")
    print(sample_answer)
    print("\n" + "="*50 + "\n")
    
    # Test the current problematic patterns
    print("=== CURRENT PATTERNS (PROBLEMATIC) ===")
    
    # Current pattern used in process_query
    story_pattern = r'(\*\*Story in Action\*\*.*?)(?=\*\*|$)'
    followup_pattern = r'(\*\*Follow-up Prompts\*\*.*?)(?=\*\*|$)'
    concepts_pattern = r'(\*\*Concepts/Tools\*\*.*?)(?=\*\*|$)'
    
    story_match = re.search(story_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    followup_match = re.search(followup_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    concepts_match = re.search(concepts_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    
    print("Story in Action (current pattern):")
    if story_match:
        print(repr(story_match.group(1)))
    else:
        print("No match found")
    
    print("\nFollow-up Prompts (current pattern):")
    if followup_match:
        print(repr(followup_match.group(1)))
    else:
        print("No match found")
    
    print("\nConcepts/Tools (current pattern):")
    if concepts_match:
        print(repr(concepts_match.group(1)))
    else:
        print("No match found")
    
    print("\n" + "="*50 + "\n")
    
    # Test improved patterns
    print("=== IMPROVED PATTERNS ===")
    
    # Improved pattern that stops at the next section header
    improved_story_pattern = r'(\*\*Story in Action\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    improved_followup_pattern = r'(\*\*Follow-up Prompts\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    improved_concepts_pattern = r'(\*\*Concepts/Tools\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    
    improved_story_match = re.search(improved_story_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    improved_followup_match = re.search(improved_followup_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    improved_concepts_match = re.search(improved_concepts_pattern, sample_answer, re.DOTALL | re.IGNORECASE)
    
    print("Story in Action (improved pattern):")
    if improved_story_match:
        print(repr(improved_story_match.group(1)))
    else:
        print("No match found")
    
    print("\nFollow-up Prompts (improved pattern):")
    if improved_followup_match:
        print(repr(improved_followup_match.group(1)))
    else:
        print("No match found")
    
    print("\nConcepts/Tools (improved pattern):")
    if improved_concepts_match:
        print(repr(improved_concepts_match.group(1)))
    else:
        print("No match found")

def test_realistic_case():
    """Test with a more realistic case that might cause section bleeding"""
    
    # This mimics the actual problem where sections might bleed into each other
    realistic_answer = """**Strategic Thinking Lens**

This is the strategic thinking lens content that discusses optimization and decision-making frameworks.

**Story in Action**

This is the story content with some details about a manufacturing plant facing tariff uncertainty. The plant manager needs to optimize production while considering various constraints and market conditions.

**Follow-up Prompts**

- How does linear optimization inform your approach to balancing efficiency with flexibility?
- What trade-offs exist between your options?
- How would you handle the uncertainty in tariff rates?

**Concepts/Tools**

Linear Optimization: A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints.
Scenario Analysis: A method that explores different hypothetical futures (e.g., best-case, worst-case) to support strategic decision planning.
Risk Assessment: Systematic evaluation of potential threats and their impact on decision outcomes.
"""

    print("\n" + "="*50)
    print("=== REALISTIC CASE TEST ===")
    print("="*50)
    
    print("Original answer:")
    print(realistic_answer)
    print("\n" + "="*50 + "\n")
    
    # Test current patterns
    print("=== CURRENT PATTERNS (REALISTIC CASE) ===")
    
    story_pattern = r'(\*\*Story in Action\*\*.*?)(?=\*\*|$)'
    followup_pattern = r'(\*\*Follow-up Prompts\*\*.*?)(?=\*\*|$)'
    concepts_pattern = r'(\*\*Concepts/Tools\*\*.*?)(?=\*\*|$)'
    
    story_match = re.search(story_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    followup_match = re.search(followup_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    concepts_match = re.search(concepts_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    
    print("Story in Action (current pattern):")
    if story_match:
        print("LENGTH:", len(story_match.group(1)))
        print("CONTENT:", repr(story_match.group(1)))
    else:
        print("No match found")
    
    print("\nFollow-up Prompts (current pattern):")
    if followup_match:
        print("LENGTH:", len(followup_match.group(1)))
        print("CONTENT:", repr(followup_match.group(1)))
    else:
        print("No match found")
    
    print("\nConcepts/Tools (current pattern):")
    if concepts_match:
        print("LENGTH:", len(concepts_match.group(1)))
        print("CONTENT:", repr(concepts_match.group(1)))
    else:
        print("No match found")
    
    print("\n" + "="*50 + "\n")
    
    # Test improved patterns
    print("=== IMPROVED PATTERNS (REALISTIC CASE) ===")
    
    # More specific pattern that looks for the next section header
    improved_story_pattern = r'(\*\*Story in Action\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    improved_followup_pattern = r'(\*\*Follow-up Prompts\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    improved_concepts_pattern = r'(\*\*Concepts/Tools\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
    
    improved_story_match = re.search(improved_story_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    improved_followup_match = re.search(improved_followup_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    improved_concepts_match = re.search(improved_concepts_pattern, realistic_answer, re.DOTALL | re.IGNORECASE)
    
    print("Story in Action (improved pattern):")
    if improved_story_match:
        print("LENGTH:", len(improved_story_match.group(1)))
        print("CONTENT:", repr(improved_story_match.group(1)))
    else:
        print("No match found")
    
    print("\nFollow-up Prompts (improved pattern):")
    if improved_followup_match:
        print("LENGTH:", len(improved_followup_match.group(1)))
        print("CONTENT:", repr(improved_followup_match.group(1)))
    else:
        print("No match found")
    
    print("\nConcepts/Tools (improved pattern):")
    if improved_concepts_match:
        print("LENGTH:", len(improved_concepts_match.group(1)))
        print("CONTENT:", repr(improved_concepts_match.group(1)))
    else:
        print("No match found")

if __name__ == "__main__":
    test_section_extraction()
    test_realistic_case() 