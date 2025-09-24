#!/usr/bin/env python3
"""
Comprehensive test to verify:
1. Answers are created correctly with all 4 sections
2. Follow-up questions generate different answers than original queries
"""

from query_engine import process_query, extract_application_field, detect_course_concept_domains

def test_answer_creation():
    """Test that answers are created correctly with all 4 sections."""
    
    print("🧪 Comprehensive Q&A Test")
    print("=" * 70)
    
    # Test cases with original queries and follow-up questions
    test_cases = [
        {
            "original": "How can I use linear programming to optimize production?",
            "followup": "What are the key trade-offs between efficiency and flexibility in this approach?",
            "description": "Technical operations query"
        },
        {
            "original": "I have two job offers, how to decide?",
            "followup": "How do you balance immediate benefits with long-term career growth?",
            "description": "Strategic job decision query"
        },
        {
            "original": "Should I start a business using AI algorithms?",
            "followup": "What are the risks and opportunities of early technology adoption?",
            "description": "Strategic startup with technology query"
        },
        {
            "original": "How do I reduce groupthink in team decisions?",
            "followup": "What specific techniques can improve team decision quality?",
            "description": "Behavioral leadership query"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print("=" * 60)
        
        # Test original query
        print(f"Original Query: {test_case['original']}")
        print("-" * 40)
        
        try:
            original_response = process_query(test_case['original'])
            
            # Check if all 4 sections are present
            sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts", "Concepts/Tools"]
            missing_sections = []
            
            for section in sections:
                if section not in original_response:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections in original: {missing_sections}")
                all_passed = False
            else:
                print("✅ Original answer has all 4 sections")
            
            # Check response length
            if len(original_response) > 500:
                print(f"✅ Original response length: {len(original_response)} characters")
            else:
                print(f"❌ Original response too short: {len(original_response)} characters")
                all_passed = False
            
            # Extract strategic lens for comparison
            if "Strategic Thinking Lens" in original_response:
                original_lens = original_response.split("Strategic Thinking Lens")[1].split("##")[0].strip()
                print(f"✅ Original strategic lens extracted ({len(original_lens)} chars)")
            else:
                print("❌ Original strategic lens not found")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Original query failed: {str(e)}")
            all_passed = False
            continue
        
        # Test follow-up query
        print(f"\nFollow-up Query: {test_case['followup']}")
        print("-" * 40)
        
        try:
            followup_response = process_query(test_case['followup'])
            
            # Check if all 4 sections are present
            missing_sections = []
            for section in sections:
                if section not in followup_response:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections in follow-up: {missing_sections}")
                all_passed = False
            else:
                print("✅ Follow-up answer has all 4 sections")
            
            # Check response length
            if len(followup_response) > 500:
                print(f"✅ Follow-up response length: {len(followup_response)} characters")
            else:
                print(f"❌ Follow-up response too short: {len(followup_response)} characters")
                all_passed = False
            
            # Extract strategic lens for comparison
            if "Strategic Thinking Lens" in followup_response:
                followup_lens = followup_response.split("Strategic Thinking Lens")[1].split("##")[0].strip()
                print(f"✅ Follow-up strategic lens extracted ({len(followup_lens)} chars)")
            else:
                print("❌ Follow-up strategic lens not found")
                all_passed = False
            
            # Compare strategic lenses
            if 'original_lens' in locals() and 'followup_lens' in locals():
                if original_lens != followup_lens:
                    print("✅ Strategic lenses are different (as expected)")
                    
                    # Show a snippet of the difference
                    original_words = original_lens.split()[:10]
                    followup_words = followup_lens.split()[:10]
                    print(f"   Original starts with: {' '.join(original_words)}...")
                    print(f"   Follow-up starts with: {' '.join(followup_words)}...")
                else:
                    print("❌ Strategic lenses are identical (should be different)")
                    all_passed = False
            
            # Compare overall responses
            if len(original_response) != len(followup_response):
                print(f"✅ Responses have different lengths: {len(original_response)} vs {len(followup_response)}")
            else:
                print("⚠️ Responses have same length (may still be different content)")
            
            # Check for significant content differences
            original_words = set(original_response.lower().split())
            followup_words = set(followup_response.lower().split())
            unique_original = original_words - followup_words
            unique_followup = followup_words - original_words
            
            if len(unique_original) > 10 and len(unique_followup) > 10:
                print("✅ Responses have significantly different content")
            else:
                print("⚠️ Responses may be too similar")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Follow-up query failed: {str(e)}")
            all_passed = False
        
        print("=" * 60)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Answers are created correctly with all 4 sections")
        print("✅ Follow-up questions generate different answers")
    else:
        print("❌ Some tests failed - check details above")
    
    return all_passed

def test_domain_detection_consistency():
    """Test that domain detection works consistently for original vs follow-up queries."""
    
    print("\n🔍 Domain Detection Consistency Test")
    print("=" * 50)
    
    test_queries = [
        ("How can I optimize production?", "What are the trade-offs in this approach?"),
        ("I have two job offers, how to decide?", "How do you evaluate career growth potential?"),
        ("Should I start a business?", "What are the key risks of entrepreneurship?")
    ]
    
    for original, followup in test_queries:
        print(f"\nOriginal: {original}")
        original_domains = detect_course_concept_domains(original)
        original_field = extract_application_field(original)
        print(f"  Domains: {original_domains}")
        print(f"  Field: {original_field}")
        
        print(f"Follow-up: {followup}")
        followup_domains = detect_course_concept_domains(followup)
        followup_field = extract_application_field(followup)
        print(f"  Domains: {followup_domains}")
        print(f"  Field: {followup_field}")
        
        # Check if they're different
        if original_domains != followup_domains or original_field != followup_field:
            print("✅ Different domains/fields detected (good for variety)")
        else:
            print("⚠️ Same domains/fields detected (may lead to similar answers)")

if __name__ == "__main__":
    # Run comprehensive Q&A test
    success = test_answer_creation()
    
    # Run domain detection consistency test
    test_domain_detection_consistency()
    
    print(f"\n🎯 Overall Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}") 