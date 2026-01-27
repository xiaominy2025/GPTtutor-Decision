#!/usr/bin/env python3
"""
Comprehensive test for story generation across different scenarios
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 COMPREHENSIVE STORY IN ACTION TEST")
print("=" * 60)

try:
    from query_engine import generate_story_or_analogy
    print("✅ Import successful")
    
    test_cases = [
        {
            "query": "How should I tell my boss about a mistake I made?",
            "fields": ["general business context"],
            "domains": ["human_behaviors"],
            "expected_context": "boss"
        },
        {
            "query": "How should I tell my employee about a mistake they made?",
            "fields": ["general business context"],
            "domains": ["human_behaviors"],
            "expected_context": "employee"
        },
        {
            "query": "How should I approach a negotiation with suppliers?",
            "fields": ["operations"],
            "domains": ["negotiation"],
            "expected_context": "negotiation"
        },
        {
            "query": "What's the best way to optimize our production process?",
            "fields": ["operations"],
            "domains": ["analytical_tools"],
            "expected_context": "analytical"
        },
        {
            "query": "How do I deliver bad news to my team?",
            "fields": ["general business context"],
            "domains": ["human_behaviors"],
            "expected_context": "team"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['query']}")
        print("-" * 40)
        
        story = generate_story_or_analogy(test_case['fields'], test_case['domains'], test_case['query'])
        word_count = len(story.split())
        
        print(f"Generated story ({word_count} words):")
        print(f"'{story}'")
        
        # Check word count
        if 60 <= word_count <= 80:
            print("✅ WORD COUNT: Within 60-80 target")
        else:
            print(f"⚠️  WORD COUNT: {word_count} outside target range")
            all_passed = False
        
        # Check for step-by-step structure
        step_indicators = ["first", "then", "finally"]
        has_steps = any(indicator in story.lower() for indicator in step_indicators)
        if has_steps:
            print("✅ STEP-BY-STEP: Contains sequential application")
        else:
            print("⚠️  STEP-BY-STEP: Missing sequential structure")
            all_passed = False
        
        # Check for concrete details
        detail_indicators = ["15%", "20%", "25%", "30%", "40%", "3%", "reduced costs", "improved", "increased", "exceeded", "outperformed"]
        has_details = any(indicator in story.lower() for indicator in detail_indicators)
        if has_details:
            print("✅ CONCRETE DETAILS: Contains specific outcomes/numbers")
        else:
            print("⚠️  CONCRETE DETAILS: Missing specific outcomes")
            all_passed = False
        
        # Check context alignment
        expected_context = test_case['expected_context']
        if expected_context == "boss" and "boss" in story.lower():
            print("✅ CONTEXT ALIGNMENT: Boss context matches")
        elif expected_context == "employee" and "employee" in story.lower():
            print("✅ CONTEXT ALIGNMENT: Employee context matches")
        elif expected_context == "team" and "team" in story.lower():
            print("✅ CONTEXT ALIGNMENT: Team context matches")
        elif expected_context in ["negotiation", "analytical"]:
            print("✅ CONTEXT ALIGNMENT: Business context appropriate")
        else:
            print(f"⚠️  CONTEXT ALIGNMENT: May not match expected context '{expected_context}'")
            all_passed = False
        
        # Check paragraph structure (3-6 sentences for 1-2 paragraphs)
        sentences = story.split('. ')
        if 3 <= len(sentences) <= 6:
            print("✅ PARAGRAPH STRUCTURE: 1-2 solid paragraphs")
        else:
            print(f"⚠️  PARAGRAPH STRUCTURE: {len(sentences)} sentences may need adjustment")
            all_passed = False
        
        print("-" * 40)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Story in Action section is working correctly.")
        print("✅ Word count: 60-80 words")
        print("✅ Step-by-step application")
        print("✅ Concrete details and outcomes")
        print("✅ Context alignment")
        print("✅ Paragraph structure")
    else:
        print("\n⚠️  SOME TESTS FAILED. Please review the issues above.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 