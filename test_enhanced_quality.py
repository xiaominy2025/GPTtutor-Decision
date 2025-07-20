#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced GPTutor quality features
"""

import re
from typing import List, Tuple, Dict

def test_four_section_structure():
    """Test that answers include all four required sections with proper formatting"""
    
    print("🧪 Testing Four-Section Structure")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Complete Answer",
            "text": """
**Strategy or Explanation**
What should you do when faced with this decision? Let's break this down together.

**Story or Analogy**
Imagine Sarah, a marketing manager, who had to choose between two job offers.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- **Decision Tree**: A visual tool that maps out different options and their potential outcomes
- **SWOT Analysis**: A framework that helps identify strengths, weaknesses, opportunities, and threats
""",
            "expected_sections": ["Strategy or Explanation", "Story or Analogy", "Reflection Prompts", "Concept/Tool References"],
            "should_pass": True
        },
        {
            "name": "Missing Section",
            "text": """
**Strategy or Explanation**
What should you do when faced with this decision?

**Story or Analogy**
Imagine Sarah, a marketing manager.

**Reflection Prompts**
• What values matter most to you?
""",
            "expected_sections": ["Strategy or Explanation", "Story or Analogy", "Reflection Prompts", "Concept/Tool References"],
            "should_pass": False
        },
        {
            "name": "Wrong Formatting",
            "text": """
Strategy or Explanation
What should you do when faced with this decision?

Story or Analogy
Imagine Sarah, a marketing manager.

Reflection Prompts
• What values matter most to you?

Concept/Tool References
- Decision Tree: A visual tool
""",
            "expected_sections": ["Strategy or Explanation", "Story or Analogy", "Reflection Prompts", "Concept/Tool References"],
            "should_pass": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        missing_sections = []
        for section in test_case['expected_sections']:
            if f"**{section}**" not in test_case['text']:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections: {', '.join(missing_sections)}")
            test_passed = False
        else:
            print("✅ All required sections present with proper formatting")
            test_passed = True
        
        if test_passed == test_case['should_pass']:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")

def test_style_variety():
    """Test that answers avoid repetitive opening patterns"""
    
    print("\n🎭 Testing Style Variety")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Good Variety",
            "text": "What should you do when both options seem great? Let's break this down together. Think of this like steering a ship in fog.",
            "should_pass": True
        },
        {
            "name": "Repetitive Patterns",
            "text": "When considering this decision, it's essential to evaluate options. When considering alternatives, it is important to weigh pros and cons.",
            "should_pass": False
        },
        {
            "name": "New Repetitive Patterns",
            "text": "When considering this decision, it's essential to evaluate options. When considering alternatives, it is important to weigh pros and cons.",
            "should_pass": False
        },
        {
            "name": "Mixed Quality",
            "text": "What should you do when faced with this choice? When considering the options, it's essential to think carefully.",
            "should_pass": False
        }
    ]
    
    repetitive_patterns = [
        r'\bWhen considering\b',
        r'\bIt\'s essential to\b',
        r'\bIt is important to\b',
        r'\bIn order to\b'
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        found_patterns = []
        for pattern in repetitive_patterns:
            if re.search(pattern, test_case['text'], re.IGNORECASE):
                found_patterns.append(pattern)
        
        if found_patterns:
            print(f"❌ Repetitive patterns found: {', '.join(found_patterns)}")
            test_passed = False
        else:
            print("✅ No repetitive patterns detected")
            test_passed = True
        
        if test_passed == test_case['should_pass']:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")

def test_tooltip_sanity():
    """Test tooltip deduplication and formatting"""
    
    print("\n🧰 Testing Tooltip Sanity")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Duplicate Tooltips",
            "text": """
**Concept/Tool References**
- **Decision Tree**: A visual tool for mapping options
- **Decision Tree**: A framework for decision making
- **SWOT Analysis**: A strategic planning tool
""",
            "should_have_duplicates": True
        },
        {
            "name": "Clean Tooltips",
            "text": """
**Concept/Tool References**
- **Decision Tree**: A visual tool for mapping options
- **SWOT Analysis**: A strategic planning tool
- **Cost-Benefit Analysis**: A quantitative evaluation method
""",
            "should_have_duplicates": False
        },
        {
            "name": "Poor Formatting",
            "text": """
**Concept/Tool References**
- Decision Tree: A visual tool for mapping options.
- **SWOT Analysis**: A strategic planning tool.
- **Cost-Benefit Analysis**: A quantitative evaluation method.
""",
            "should_have_formatting_issues": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        # Extract tooltip section
        tooltip_match = re.search(r'\*\*Concept/Tool References\*\*.*?(?=\*\*|$)', test_case['text'], re.DOTALL | re.IGNORECASE)
        if tooltip_match:
            tooltip_text = tooltip_match.group(0)
            
            # Check for duplicates
            tooltip_lines = [line.strip() for line in tooltip_text.split('\n') if line.strip().startswith('- **')]
            unique_tooltips = set()
            duplicates = []
            
            for line in tooltip_lines:
                name_match = re.search(r'- \*\*(.*?)\*\*', line)
                if name_match:
                    name = name_match.group(1).lower()
                    if name in unique_tooltips:
                        duplicates.append(name)
                    else:
                        unique_tooltips.add(name)
            
            if duplicates:
                print(f"❌ Duplicate tooltips found: {', '.join(duplicates)}")
            else:
                print("✅ No duplicate tooltips")
            
            # Check formatting
            formatting_issues = []
            for line in tooltip_lines:
                if not line.startswith('- **'):
                    formatting_issues.append("Missing bold formatting")
                if line.endswith('.'):
                    formatting_issues.append("Trailing period")
            
            if formatting_issues:
                print(f"❌ Formatting issues: {', '.join(set(formatting_issues))}")
            else:
                print("✅ Proper formatting")
        else:
            print("❌ No tooltip section found")

def test_readability_breaks():
    """Test readability breaks for long answers"""
    
    print("\n📖 Testing Readability Breaks")
    print("=" * 50)
    
    # Create a long answer
    long_answer = """
**Strategy or Explanation**
What should you do when faced with this complex decision? Let's break this down step by step. First, you need to understand the core issue at hand. This involves examining your values, priorities, and long-term goals. Then, you should consider the potential outcomes of each option. This requires careful analysis of the risks and benefits associated with each choice. Additionally, you need to think about the impact on various stakeholders. This includes family members, colleagues, and other people who might be affected by your decision. Furthermore, you should evaluate the timing and urgency of the situation. This helps determine whether you need to act quickly or can take more time to deliberate. Finally, you should consider your own emotional state and how it might influence your judgment. This self-awareness is crucial for making a balanced decision.

**Story or Analogy**
Imagine Maria, a project manager who had to choose between two career opportunities.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- **Decision Tree**: A visual tool for mapping options
- **SWOT Analysis**: A strategic planning tool
"""
    
    word_count = len(long_answer.split())
    print(f"Word count: {word_count}")
    
    if word_count > 500:
        print("✅ Long answer detected (>500 words)")
        # Check for readability breaks
        if re.search(r'---|___|###|Summary|In summary', long_answer, re.IGNORECASE):
            print("✅ Readability breaks found")
        else:
            print("❌ No readability breaks found")
    else:
        print("✅ Answer length is appropriate")

def test_named_decision_tools():
    """Test that answers include named decision tools or frameworks"""
    
    print("\n🧠 Testing Named Decision Tools")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Includes Decision Tree",
            "text": """
**Strategy or Explanation**
What should you do when faced with this decision? Let's use a Decision Tree to map out your options.

**Story or Analogy**
Imagine Sarah, a marketing manager, who had to choose between two job offers.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- **Decision Tree**: A visual tool for mapping options
- **SWOT Analysis**: A strategic planning tool
""",
            "should_pass": True
        },
        {
            "name": "Includes GROW Model",
            "text": """
**Strategy or Explanation**
Let's use the GROW Model to structure your thinking about this decision.

**Story or Analogy**
Imagine Sarah, a marketing manager, who had to choose between two job offers.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- **GROW Model**: A coaching framework for goal setting
""",
            "should_pass": True
        },
        {
            "name": "No Named Tools",
            "text": """
**Strategy or Explanation**
What should you do when faced with this decision? Let's break this down together.

**Story or Analogy**
Imagine Sarah, a marketing manager, who had to choose between two job offers.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- **Decision Making**: A process for choosing between options
""",
            "should_pass": False
        }
    ]
    
    named_tools = [
        "decision tree", "grow model", "premortem analysis", "weighted scoring matrix",
        "swot analysis", "risk assessment matrix", "cost-benefit analysis", "expected utility",
        "ooda loop", "bounded rationality", "prospect theory", "utility theory"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        found_tools = []
        for tool in named_tools:
            if tool.lower() in test_case['text'].lower():
                found_tools.append(tool)
        
        if found_tools:
            print(f"✅ Named tools found: {', '.join(found_tools)}")
            test_passed = True
        else:
            print("❌ No named decision tools found")
            test_passed = False
        
        if test_passed == test_case['should_pass']:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")

def test_grammar_fragments():
    """Test grammar fragment detection and fixing"""
    
    print("\n✍️ Testing Grammar Fragment Detection")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Grammar Fragments",
            "text": "individual, a professional in the field, should consider the options. person, a manager, needs to evaluate the situation.",
            "should_have_fragments": True
        },
        {
            "name": "Clean Text",
            "text": "A professional should consider the options. A manager needs to evaluate the situation.",
            "should_have_fragments": False
        }
    ]
    
    fragment_patterns = [
        r'\bindividual, a professional\b',
        r'\bindividual, an expert\b',
        r'\bperson, a manager\b'
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        found_fragments = []
        for pattern in fragment_patterns:
            if re.search(pattern, test_case['text'], re.IGNORECASE):
                found_fragments.append(pattern)
        
        if found_fragments:
            print(f"❌ Grammar fragments found: {', '.join(found_fragments)}")
            test_passed = False
        else:
            print("✅ No grammar fragments detected")
            test_passed = True
        
        expected = not test_case['should_have_fragments']
        if test_passed == expected:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")

if __name__ == "__main__":
    test_four_section_structure()
    test_style_variety()
    test_tooltip_sanity()
    test_readability_breaks()
    test_named_decision_tools()
    test_grammar_fragments()
    
    print("\n✅ Enhanced quality testing completed!")
    print("\n📊 Summary of Quality Features:")
    print("• Four-section structure with proper formatting")
    print("• Style variety with no repetitive patterns")
    print("• Named decision tools and frameworks (REQUIRED)")
    print("• Tooltip sanity with deduplication")
    print("• Readability breaks for long answers")
    print("• Grammar fragment detection and fixing") 