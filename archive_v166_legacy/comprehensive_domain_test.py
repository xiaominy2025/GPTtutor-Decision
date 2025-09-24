#!/usr/bin/env python3
"""
Comprehensive test to verify all course concept domains and application fields 
are properly considered for answer generation.
"""

from query_engine import (
    process_query, 
    extract_application_field, 
    detect_course_concept_domains,
    generate_course_domain_strategic_lens
)

def test_all_domains_and_fields():
    """Test all course concept domains and application fields."""
    
    print("🧪 Comprehensive Domain and Application Field Test")
    print("=" * 70)
    
    # Test cases for all course concept domains and application fields
    test_cases = [
        # Technical domain tests
        {
            "query": "How can I use linear programming to optimize production?",
            "expected_domain": "technical",
            "expected_field": "operations",
            "expected_keywords": ["technical", "operations", "production", "optimization"]
        },
        {
            "query": "What simulation models can help with demand forecasting?",
            "expected_domain": "technical", 
            "expected_field": "operations",
            "expected_keywords": ["technical", "simulation", "models", "forecasting"]
        },
        {
            "query": "How do I implement AI algorithms in my business?",
            "expected_domain": "technical",
            "expected_field": "technology", 
            "expected_keywords": ["technical", "technology", "algorithms", "implementation"]
        },
        
        # Strategic domain tests
        {
            "query": "I have two job offers, how to decide?",
            "expected_domain": "strategic",
            "expected_field": "job",
            "expected_keywords": ["strategic", "career", "professional", "job"]
        },
        {
            "query": "Should I start a new business venture?",
            "expected_domain": "strategic", 
            "expected_field": "startup",
            "expected_keywords": ["strategic", "business", "entrepreneurial", "startup"]
        },
        {
            "query": "Which investment portfolio should I choose?",
            "expected_domain": "strategic",
            "expected_field": "finance",
            "expected_keywords": ["strategic", "finance", "investment", "portfolio"]
        },
        {
            "query": "Which college should I attend?",
            "expected_domain": "strategic",
            "expected_field": "admission",
            "expected_keywords": ["strategic", "education", "academic", "admission"]
        },
        
        # Behavioral domain tests
        {
            "query": "How do I reduce groupthink in team decisions?",
            "expected_domain": "behavioral",
            "expected_field": "leadership",
            "expected_keywords": ["behavioral", "leadership", "team", "groupthink"]
        },
        {
            "query": "How do personal biases affect my ethical decisions?",
            "expected_domain": "behavioral",
            "expected_field": "ethics",
            "expected_keywords": ["behavioral", "ethics", "biases", "moral"]
        },
        
        # Negotiation domain tests
        {
            "query": "How should I negotiate with a dominant supplier?",
            "expected_domain": "negotiation",
            "expected_field": "operations",
            "expected_keywords": ["negotiation", "supplier", "operations", "bargaining"]
        },
        
        # Health and wellness tests
        {
            "query": "Which health insurance plan should I choose?",
            "expected_domain": "strategic",
            "expected_field": "health",
            "expected_keywords": ["strategic", "health", "wellness", "insurance"]
        },
        
        # Education tests
        {
            "query": "Which online course should I take for skill development?",
            "expected_domain": "strategic",
            "expected_field": "education",
            "expected_keywords": ["strategic", "education", "learning", "skill"]
        },
        
        # Relocation tests
        {
            "query": "Should I move to a new city for better opportunities?",
            "expected_domain": "strategic",
            "expected_field": "relocation",
            "expected_keywords": ["strategic", "relocation", "location", "lifestyle"]
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}/{total_tests}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        # Test domain detection
        detected_domains = detect_course_concept_domains(test_case['query'])
        primary_domain = max(detected_domains.items(), key=lambda x: x[1])[0] if detected_domains else 'general'
        
        # Test application field detection
        detected_field = extract_application_field(test_case['query'])
        
        # Test strategic lens generation
        strategic_lens = generate_course_domain_strategic_lens(
            test_case['query'], 
            primary_domain, 
            detected_field
        )
        
        # Check if expected keywords are present
        lens_lower = strategic_lens.lower()
        expected_keywords = test_case['expected_keywords']
        found_keywords = [kw for kw in expected_keywords if kw.lower() in lens_lower]
        
        # Validate results
        domain_correct = primary_domain == test_case['expected_domain']
        field_correct = detected_field == test_case['expected_field']
        keywords_found = len(found_keywords) >= 2  # At least 2 expected keywords should be found
        
        print(f"Expected domain: {test_case['expected_domain']}")
        print(f"Detected domain: {primary_domain}")
        print(f"Domain correct: {'✅' if domain_correct else '❌'}")
        
        print(f"Expected field: {test_case['expected_field']}")
        print(f"Detected field: {detected_field}")
        print(f"Field correct: {'✅' if field_correct else '❌'}")
        
        print(f"Expected keywords: {expected_keywords}")
        print(f"Found keywords: {found_keywords}")
        print(f"Keywords found: {'✅' if keywords_found else '❌'}")
        
        # Test full response generation
        try:
            full_response = process_query(test_case['query'])
            response_success = len(full_response) > 500  # Reasonable response length
            print(f"Full response generated: {'✅' if response_success else '❌'}")
            print(f"Response length: {len(full_response)} characters")
        except Exception as e:
            print(f"Full response error: ❌ {str(e)}")
            response_success = False
        
        # Overall test result
        test_passed = domain_correct and field_correct and keywords_found and response_success
        if test_passed:
            passed_tests += 1
            print("🎯 TEST PASSED ✅")
        else:
            print("❌ TEST FAILED")
        
        print("=" * 50)
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! All domains and application fields working correctly.")
    else:
        print("⚠️ Some tests failed. Check the results above for details.")
    
    return passed_tests == total_tests

def test_edge_cases():
    """Test edge cases and boundary conditions."""
    
    print("\n🔍 Testing Edge Cases")
    print("=" * 50)
    
    edge_cases = [
        {
            "query": "What should I do?",
            "description": "Very general query"
        },
        {
            "query": "How do I optimize the production of my plant to maximize profit under tariff uncertainty?",
            "description": "Complex technical operations query"
        },
        {
            "query": "Should I choose option A or option B?",
            "description": "Simple choice query"
        }
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {case['description']}")
        print(f"Query: {case['query']}")
        
        try:
            response = process_query(case['query'])
            domains = detect_course_concept_domains(case['query'])
            field = extract_application_field(case['query'])
            
            print(f"Response length: {len(response)}")
            print(f"Detected domains: {domains}")
            print(f"Application field: {field}")
            print("✅ Edge case handled successfully")
            
        except Exception as e:
            print(f"❌ Edge case failed: {str(e)}")

if __name__ == "__main__":
    # Run comprehensive tests
    success = test_all_domains_and_fields()
    
    # Run edge case tests
    test_edge_cases()
    
    print(f"\n🎯 Overall Result: {'SUCCESS' if success else 'NEEDS ATTENTION'}") 