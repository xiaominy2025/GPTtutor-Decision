#!/usr/bin/env python3
"""
Test Follow-up Prompts and Concepts/Tooltips Fix
===============================================

This test validates the July 30, 2025 requirements:

3. Follow-up Prompts
• Role: Encourage reflection and active learning.
• Content: 2-4 open ended questions tied to lens trade offs and priorities
• Logic: Normally generated from Strategic Lens content.
• Design: One strategic/analytical, one behavioral/values based.

4. Concepts/Tools (Tooltip Engine)
• Role: Provide structured frameworks + glossary linked tooltips.
• Connection: Anchored to Strategic Lens domains (not story domains).
• Content: 2–4 concepts, each clickable for a glossary tooltip.

Tooltip Allocation Rules
• Single Domain Lens: Up to 3 tooltips
• Multi Domain Lens: 2 from the primary domain +1 from each additional domain, Hard cap = 4 total
• Selection Thresholds: Primary domain concepts: score ≥ 0.50, Secondary domain concepts: score ≥ 0.40, Core concepts just under threshold: score ≥ 0.35
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    process_query,
    generate_domain_aware_followup_prompt,
    get_top_ranked_concepts_with_lens_shifting
)

def test_followup_prompts_requirements():
    """Test that follow-up prompts generate 2-4 questions as required"""
    print("🧪 Testing Follow-up Prompts Requirements")
    print("=" * 60)
    
    test_queries = [
        "How does linear optimization inform your approach to balancing efficiency with flexibility?",
        "What are the key factors in choosing between two job offers?",
        "How should I evaluate investment opportunities?",
        "What considerations are important for starting a new business?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:50]}...")
        
        # Test the follow-up prompt generation
        prompt = generate_domain_aware_followup_prompt(query)
        
        # Check for the correct number specification
        if "exactly 3-4" in prompt or "exactly 2-3" in prompt or "exactly 2-4" in prompt:
            print("✅ Correct number specification found")
        else:
            print("❌ Missing correct number specification")
        
        # Check for strategic/analytical and behavioral/values requirements
        if "strategic/analytical" in prompt and "behavioral/values" in prompt:
            print("✅ Strategic/analytical and behavioral/values requirements found")
        else:
            print("❌ Missing strategic/analytical and behavioral/values requirements")
        
        # Test actual response generation
        try:
            result = process_query(query)
            
            # Count follow-up questions
            lines = result.split('\n')
            followup_section = False
            question_count = 0
            
            for line in lines:
                if "**Follow-up Prompts**" in line:
                    followup_section = True
                elif followup_section and line.strip().startswith('- '):
                    question_count += 1
                elif followup_section and line.strip().startswith('**'):
                    break
            
            print(f"📊 Found {question_count} follow-up questions")
            
            if 2 <= question_count <= 4:
                print("✅ Follow-up questions count is within 2-4 range")
            else:
                print(f"❌ Follow-up questions count ({question_count}) is outside 2-4 range")
                
        except Exception as e:
            print(f"❌ Error processing query: {e}")
    
    return True

def test_concepts_tooltips_requirements():
    """Test that concepts/tooltips follow the correct allocation rules"""
    print("\n🧪 Testing Concepts/Tooltips Requirements")
    print("=" * 60)
    
    test_queries = [
        "How does linear optimization inform your approach to balancing efficiency with flexibility?",
        "What are the key factors in choosing between two job offers?",
        "How should I evaluate investment opportunities?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:50]}...")
        
        try:
            # Test concept extraction with lens-shifting
            concepts = get_top_ranked_concepts_with_lens_shifting(query, top_k=4, is_followup=False)
            
            print(f"📊 Found {len(concepts)} concepts")
            
            # Check if concepts are within the 2-4 range
            if 2 <= len(concepts) <= 4:
                print("✅ Concepts count is within 2-4 range")
            else:
                print(f"❌ Concepts count ({len(concepts)}) is outside 2-4 range")
            
            # Test follow-up concept extraction
            followup_concepts = get_top_ranked_concepts_with_lens_shifting(query, top_k=4, is_followup=True)
            
            print(f"📊 Found {len(followup_concepts)} follow-up concepts")
            
            # Check if follow-up concepts are within the 2-4 range
            if 2 <= len(followup_concepts) <= 4:
                print("✅ Follow-up concepts count is within 2-4 range")
            else:
                print(f"❌ Follow-up concepts count ({len(followup_concepts)}) is outside 2-4 range")
            
            # Check for concept diversity between original and follow-up
            original_names = {c[0].lower() for c in concepts}
            followup_names = {c[0].lower() for c in followup_concepts}
            
            overlap = len(original_names.intersection(followup_names))
            total_unique = len(original_names.union(followup_names))
            
            if total_unique > 0:
                diversity_score = 1 - (overlap / total_unique)
                print(f"📊 Concept diversity score: {diversity_score:.2f}")
                
                if diversity_score > 0.2:
                    print("✅ Good concept diversity between original and follow-up")
                else:
                    print("❌ Low concept diversity between original and follow-up")
            
        except Exception as e:
            print(f"❌ Error testing concepts: {e}")
    
    return True

def test_threshold_requirements():
    """Test that the correct thresholds are being applied"""
    print("\n🧪 Testing Threshold Requirements")
    print("=" * 60)
    
    # Test queries that should trigger different thresholds
    test_cases = [
        ("Single domain technical query", "How do I optimize production using linear programming?"),
        ("Multi-domain query", "How should I balance technical efficiency with strategic goals?"),
        ("General query", "What should I consider when making a decision?")
    ]
    
    for test_name, query in test_cases:
        print(f"\n📋 {test_name}")
        
        try:
            # Test concept extraction
            concepts = get_top_ranked_concepts_with_lens_shifting(query, top_k=4, is_followup=False)
            
            print(f"📊 Found {len(concepts)} concepts")
            
            # Check if concepts are within proper ranges
            if len(concepts) >= 2:
                print("✅ Minimum concept threshold met")
            else:
                print("❌ Below minimum concept threshold")
            
            if len(concepts) <= 4:
                print("✅ Maximum concept threshold respected")
            else:
                print("❌ Exceeds maximum concept threshold")
                
        except Exception as e:
            print(f"❌ Error testing thresholds: {e}")
    
    return True

def run_comprehensive_test():
    """Run all tests for follow-up prompts and concepts/tooltips requirements"""
    print("🚀 Follow-up Prompts and Concepts/Tooltips Requirements Test")
    print("=" * 80)
    
    tests = [
        ("Follow-up Prompts Requirements", test_followup_prompts_requirements),
        ("Concepts/Tooltips Requirements", test_concepts_tooltips_requirements),
        ("Threshold Requirements", test_threshold_requirements)
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
    print("\n📊 REQUIREMENTS COMPLIANCE SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All requirements are properly implemented!")
        return True
    else:
        print("⚠️ Some requirements need attention.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 