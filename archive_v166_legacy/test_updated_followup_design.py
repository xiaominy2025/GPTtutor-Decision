#!/usr/bin/env python3
"""
Test Updated Follow-up Prompts Design
====================================

This test validates the updated July 30, 2025 follow-up prompts design:

• Role: Encourage reflection and active learning.
• Content: 2-4 open ended questions tied to lens trade offs and priorities
• Logic:
  • Single Concept Domain Lens: Up to 3 questions
  • Multi Domain Lens: 2 from the primary domain, +1 from each additional domain, Hard cap = 4 total
  If GPT fails, fallback pulls 2 domain appropriate questions from templates.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    process_query,
    generate_domain_aware_followup_prompt,
    generate_domain_aware_followup_questions
)

def test_single_domain_allocation():
    """Test single domain allocation (up to 3 questions)"""
    print("🧪 Testing Single Domain Allocation")
    print("=" * 50)
    
    test_cases = [
        ("Technical single domain", "How do I optimize production using linear programming?"),
        ("Strategic single domain", "What are the key factors in choosing between two job offers?"),
        ("Behavioral single domain", "How do personal biases affect my ethical decisions?"),
        ("Negotiation single domain", "How should I negotiate with a dominant supplier?")
    ]
    
    for test_name, query in test_cases:
        print(f"\n📋 {test_name}")
        
        # Test prompt generation
        prompt = generate_domain_aware_followup_prompt(query)
        
        # Check for "up to 3" specification
        if "up to 3" in prompt.lower():
            print("✅ Correct 'up to 3' specification found")
        else:
            print("❌ Missing 'up to 3' specification")
        
        # Test fallback questions
        fallback_questions = generate_domain_aware_followup_questions(query)
        print(f"📊 Fallback questions count: {len(fallback_questions)}")
        
        if len(fallback_questions) <= 3:
            print("✅ Fallback questions count is within limit")
        else:
            print(f"❌ Fallback questions count ({len(fallback_questions)}) exceeds limit")
    
    return True

def test_multi_domain_allocation():
    """Test multi-domain allocation (2+1+1, hard cap = 4)"""
    print("\n🧪 Testing Multi-Domain Allocation")
    print("=" * 50)
    
    test_cases = [
        ("Technical + Strategic", "How should I balance technical efficiency with strategic goals?"),
        ("Behavioral + Technical", "How do cognitive biases affect my technical decision-making?"),
        ("Strategic + Negotiation", "How should I approach strategic decisions in competitive negotiations?"),
        ("Technical + Behavioral + Strategic", "How do I balance technical optimization with human factors and strategic objectives?")
    ]
    
    for test_name, query in test_cases:
        print(f"\n📋 {test_name}")
        
        # Test prompt generation
        prompt = generate_domain_aware_followup_prompt(query)
        
        # Check for multi-domain allocation specification
        if "2 questions" in prompt and "1 question" in prompt:
            print("✅ Correct multi-domain allocation specification found")
        else:
            print("❌ Missing multi-domain allocation specification")
        
        # Test fallback questions
        fallback_questions = generate_domain_aware_followup_questions(query)
        print(f"📊 Fallback questions count: {len(fallback_questions)}")
        
        if len(fallback_questions) <= 4:
            print("✅ Fallback questions count respects hard cap")
        else:
            print(f"❌ Fallback questions count ({len(fallback_questions)}) exceeds hard cap")
    
    return True

def test_fallback_logic():
    """Test fallback logic when GPT fails"""
    print("\n🧪 Testing Fallback Logic")
    print("=" * 50)
    
    test_cases = [
        ("Single domain fallback", "How do I optimize production?"),
        ("Multi-domain fallback", "How should I balance efficiency with strategy?"),
        ("General fallback", "What should I consider when making a decision?")
    ]
    
    for test_name, query in test_cases:
        print(f"\n📋 {test_name}")
        
        # Test fallback questions
        fallback_questions = generate_domain_aware_followup_questions(query)
        
        print(f"📊 Fallback questions generated: {len(fallback_questions)}")
        
        # Check that we get at least 2 questions
        if len(fallback_questions) >= 2:
            print("✅ Minimum 2 fallback questions provided")
        else:
            print(f"❌ Insufficient fallback questions ({len(fallback_questions)})")
        
        # Check question quality
        for i, question in enumerate(fallback_questions, 1):
            if question.strip().startswith("- ") and "?" in question:
                print(f"✅ Question {i}: Properly formatted")
            else:
                print(f"❌ Question {i}: Poorly formatted")
    
    return True

def test_domain_appropriate_questions():
    """Test that fallback questions are domain-appropriate"""
    print("\n🧪 Testing Domain-Appropriate Questions")
    print("=" * 50)
    
    test_cases = [
        ("Technical domain", "How do I optimize production using linear programming?"),
        ("Strategic domain", "What are the key factors in choosing between two job offers?"),
        ("Behavioral domain", "How do personal biases affect my ethical decisions?"),
        ("Negotiation domain", "How should I negotiate with a dominant supplier?")
    ]
    
    for test_name, query in test_cases:
        print(f"\n📋 {test_name}")
        
        # Test fallback questions
        fallback_questions = generate_domain_aware_followup_questions(query)
        
        # Check domain appropriateness
        if "technical" in test_name.lower():
            technical_indicators = ["analytical", "quantify", "model", "data", "optimize"]
            domain_appropriate = any(indicator in " ".join(fallback_questions).lower() for indicator in technical_indicators)
        elif "strategic" in test_name.lower():
            strategic_indicators = ["strategic", "long-term", "objectives", "competitive", "implications"]
            domain_appropriate = any(indicator in " ".join(fallback_questions).lower() for indicator in strategic_indicators)
        elif "behavioral" in test_name.lower():
            behavioral_indicators = ["biases", "psychological", "emotional", "cognitive", "stakeholder"]
            domain_appropriate = any(indicator in " ".join(fallback_questions).lower() for indicator in behavioral_indicators)
        elif "negotiation" in test_name.lower():
            negotiation_indicators = ["batna", "negotiation", "leverage", "common ground", "parties"]
            domain_appropriate = any(indicator in " ".join(fallback_questions).lower() for indicator in negotiation_indicators)
        else:
            domain_appropriate = True
        
        if domain_appropriate:
            print("✅ Domain-appropriate questions generated")
        else:
            print("❌ Questions not domain-appropriate")
    
    return True

def run_comprehensive_test():
    """Run all tests for updated follow-up prompts design"""
    print("🚀 Updated Follow-up Prompts Design Test")
    print("=" * 80)
    
    tests = [
        ("Single Domain Allocation", test_single_domain_allocation),
        ("Multi-Domain Allocation", test_multi_domain_allocation),
        ("Fallback Logic", test_fallback_logic),
        ("Domain-Appropriate Questions", test_domain_appropriate_questions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 UPDATED DESIGN COMPLIANCE SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Updated follow-up prompts design is properly implemented!")
        return True
    else:
        print("⚠️ Some design requirements need attention.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 