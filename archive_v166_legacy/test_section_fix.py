#!/usr/bin/env python3
"""
Test script for section formatting fix
"""

import re

def test_section_formatting():
    """Test the section formatting fix"""
    
    # Sample response with the issue
    sample_response = """**Strategic Thinking Lens**

Evaluate the job offers based on factors such as salary, benefits, career growth potential, company culture, work-life balance, and location. Consider the long-term impact each role may have on your career trajectory and personal life. Anticipate how your decision fits into your larger goals and aspirations, weighing short-term gains against potential future opportunities. Reflect on which offer aligns best with your values, skills, and long-term objectives to make a well-rounded decision. This decision should be evaluated against multiple criteria including feasibility, impact, and alignment with organizational objectives. Consider both short-term and long-term implications. The decision-making process should incorporate relevant frameworks and analytical tools to ensure comprehensive evaluation. This approach should be evaluated against multiple criteria and stakeholder perspectives. The implementation should consider practical constraints and real-world application of the decision framework.**Story in Action**

When choosing between job offers, analyze how each position aligns with your career goals, financial needs, and personal values. Imagine deciding between a higher-paying job in a city you don't love compared to a slightly lower-paying role in a company with strong growth opportunities that align with your passion for sustainability. This situation requires careful analysis of all available options and their potential outcomes. Consider stakeholder perspectives and organizational impact when making this decision.**Follow-up Prompts**

1. How might each job offer impact your long-term career growth prospects?
2. Which company's values and work culture resonate more with your personal preferences?
3. Have you envisioned how each role could contribute to your overall life satisfaction and work-life balance?
4. What tradeoffs are you willing to make between salary, job responsibilities, and personal fulfillment in your decision-making process?

**Concepts/Tools**

Decision Tree: A visual representation to map out the potential outcomes and choices in a decision-making process.
Scenario Analysis: A method to examine various hypothetical situations and their potential implications on decision outcomes."""

    print("=== BEFORE FIX ===")
    print(sample_response)
    print("\n" + "="*50 + "\n")
    
    # Apply the fix
    fixed_response = re.sub(r'\*\*Story in Action\*\*', r'\n\n**Story in Action**', sample_response)
    fixed_response = re.sub(r'\*\*Follow-up Prompts\*\*', r'\n\n**Follow-up Prompts**', fixed_response)
    fixed_response = re.sub(r'\*\*Concepts/Tools\*\*', r'\n\n**Concepts/Tools**', fixed_response)
    
    print("=== AFTER FIX ===")
    print(fixed_response)
    print("\n" + "="*50 + "\n")
    
    # Test section extraction
    strategic_match = re.search(r'\*\*Strategic Thinking Lens\*\*(.*?)(?=\*\*Story in Action\*\*|\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)', fixed_response, re.DOTALL | re.IGNORECASE)
    story_match = re.search(r'\*\*Story in Action\*\*(.*?)(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)', fixed_response, re.DOTALL | re.IGNORECASE)
    
    print("=== SECTION EXTRACTION TEST ===")
    if strategic_match:
        print("✅ Strategic Thinking Lens found:")
        print(strategic_match.group(1).strip()[:200] + "...")
    else:
        print("❌ Strategic Thinking Lens not found")
        
    if story_match:
        print("✅ Story in Action found:")
        print(story_match.group(1).strip()[:200] + "...")
    else:
        print("❌ Story in Action not found")

if __name__ == "__main__":
    test_section_formatting() 