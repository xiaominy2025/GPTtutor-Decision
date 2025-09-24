#!/usr/bin/env python3
"""
Test V1.6.5 Improvements
========================

This test validates the following V1.6.5 improvements:

1. LENS-SHIFTING LOGIC FOR FOLLOW-UPS
2. STRATEGIC THINKING LENS: ENFORCE ANALYTICAL DEPTH  
3. STORY IN ACTION: CONTRASTING SCENARIOS
4. FOLLOW-UP PROMPTS: ADD PIVOTING DIMENSIONS
5. CONCEPTS/TOOLS: BALANCED WEIGHTING
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    detect_followup_query,
    shift_domain_for_followup,
    get_top_ranked_concepts_with_lens_shifting,
    generate_domain_aware_followup_prompt,
    enhance_story_with_contrasting_scenarios
)

def test_followup_detection():
    """Test follow-up detection logic"""
    print("🧪 Testing Follow-up Detection")
    print("=" * 50)
    
    test_cases = [
        ("How should I choose between two job offers?", False),
        ("But what if I consider the long-term implications?", True),
        ("What about the technical aspects?", True),
        ("However, what if the market changes?", True),
        ("Also, how does this affect my career?", True),
        ("What should I do?", False),
        ("Can you clarify the strategic implications?", True),
        ("On the other hand, what about costs?", True),
        ("If instead I focus on innovation?", True),
        ("Let's say I take a different approach?", True)
    ]
    
    passed = 0
    for query, expected in test_cases:
        result = detect_followup_query(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} Query: '{query[:50]}...' -> Expected: {expected}, Got: {result}")
        if result == expected:
            passed += 1
    
    print(f"\n📊 Follow-up Detection: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_domain_shifting():
    """Test domain shifting logic for follow-ups"""
    print("\n🧪 Testing Domain Shifting")
    print("=" * 50)
    
    test_cases = [
        ("strategic", "behavioral"),
        ("behavioral", "technical"),
        ("technical", "strategic"),
        ("negotiation", "behavioral"),
        ("general", "strategic")
    ]
    
    passed = 0
    for original, expected in test_cases:
        result = shift_domain_for_followup(original)
        status = "✅" if result == expected else "❌"
        print(f"{status} {original} -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\n📊 Domain Shifting: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_analytical_frameworks():
    """Test that strategic lens includes analytical frameworks"""
    print("\n🧪 Testing Analytical Framework Integration")
    print("=" * 50)
    
    from query_engine import generate_course_domain_strategic_lens
    
    test_cases = [
        ("strategic", ["Porter's Five Forces", "SWOT"]),
        ("technical", ["Monte Carlo", "Linear optimization"]),
        ("behavioral", ["Cognitive bias", "Stakeholder"]),
        ("negotiation", ["BATNA", "ZOPA"])
    ]
    
    passed = 0
    for domain, expected_frameworks in test_cases:
        lens = generate_course_domain_strategic_lens("test query", domain)
        frameworks_found = []
        for framework in expected_frameworks:
            if framework.lower() in lens.lower():
                frameworks_found.append(framework)
        
        status = "✅" if len(frameworks_found) >= 1 else "❌"
        print(f"{status} {domain}: Found {len(frameworks_found)}/{len(expected_frameworks)} frameworks")
        if len(frameworks_found) >= 1:
            passed += 1
    
    print(f"\n📊 Analytical Frameworks: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_concept_balance():
    """Test balanced concept weighting for follow-ups"""
    print("\n🧪 Testing Concept Balance")
    print("=" * 50)
    
    # Test original query
    original_concepts = get_top_ranked_concepts_with_lens_shifting(
        "How should I choose between two job offers?", 
        is_followup=False
    )
    
    # Test follow-up query
    followup_concepts = get_top_ranked_concepts_with_lens_shifting(
        "But what if I consider the behavioral aspects?", 
        is_followup=True
    )
    
    print(f"Original concepts: {[c[0] for c in original_concepts]}")
    print(f"Follow-up concepts: {[c[0] for c in followup_concepts]}")
    
    # Check that concepts are different (lens-shifting working)
    original_names = {c[0].lower() for c in original_concepts}
    followup_names = {c[0].lower() for c in followup_concepts}
    
    overlap = len(original_names.intersection(followup_names))
    total_unique = len(original_names.union(followup_names))
    
    # We want some overlap but not complete overlap
    diversity_score = 1 - (overlap / total_unique) if total_unique > 0 else 0
    
    status = "✅" if diversity_score > 0.2 else "❌"
    print(f"{status} Concept diversity score: {diversity_score:.2f}")
    
    return diversity_score > 0.2

def test_pivoting_dimensions():
    """Test that follow-up prompts include pivoting dimensions"""
    print("\n🧪 Testing Pivoting Dimensions")
    print("=" * 50)
    
    # Test original prompt
    original_prompt = generate_domain_aware_followup_prompt(
        "How should I choose between two job offers?",
        is_followup=False
    )
    
    # Test follow-up prompt
    followup_prompt = generate_domain_aware_followup_prompt(
        "But what if I consider the long-term implications?",
        is_followup=True
    )
    
    # Check for pivoting dimension indicators
    pivoting_indicators = [
        "Short-term vs. Long-term",
        "Cost-focused vs. Innovation",
        "Risk mitigation vs. Growth",
        "Domestic vs. International",
        "Individual vs. Organizational",
        "Technical vs. Behavioral"
    ]
    
    indicators_found = []
    for indicator in pivoting_indicators:
        if indicator in followup_prompt:
            indicators_found.append(indicator)
    
    status = "✅" if len(indicators_found) > 0 else "❌"
    print(f"{status} Found {len(indicators_found)} pivoting indicators in follow-up prompt")
    
    return len(indicators_found) > 0

def test_contrasting_scenarios():
    """Test contrasting scenario enhancement"""
    print("\n🧪 Testing Contrasting Scenarios")
    print("=" * 50)
    
    # Mock entities for testing
    entities = {
        'time_periods': ['short-term', 'long-term'],
        'stakeholders': ['employees', 'customers'],
        'industries': ['technology', 'healthcare'],
        'locations': ['domestic', 'international']
    }
    
    original_story = """**Story in Action**

Sarah, a software engineer, receives two job offers and creates a decision matrix to compare them systematically."""
    
    enhanced_story = enhance_story_with_contrasting_scenarios(
        original_story, entities, is_followup=True
    )
    
    # Check if enhancement added contrasting elements
    enhancement_indicators = [
        "While the first scenario",
        "contrasting approach",
        "creates a tension between",
        "affects both"
    ]
    
    indicators_found = []
    for indicator in enhancement_indicators:
        if indicator.lower() in enhanced_story.lower():
            indicators_found.append(indicator)
    
    status = "✅" if len(indicators_found) > 0 else "❌"
    print(f"{status} Found {len(indicators_found)} contrasting elements")
    
    return len(indicators_found) > 0

def run_comprehensive_test():
    """Run all V1.6.5 improvement tests"""
    print("🚀 V1.6.5 Improvements Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Follow-up Detection", test_followup_detection),
        ("Domain Shifting", test_domain_shifting),
        ("Analytical Frameworks", test_analytical_frameworks),
        ("Concept Balance", test_concept_balance),
        ("Pivoting Dimensions", test_pivoting_dimensions),
        ("Contrasting Scenarios", test_contrasting_scenarios)
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
    print("\n📊 V1.6.5 IMPROVEMENTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All V1.6.5 improvements are working correctly!")
        return True
    else:
        print("⚠️ Some improvements need attention.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 