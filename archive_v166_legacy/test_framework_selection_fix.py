#!/usr/bin/env python3
"""
Test script to verify the framework selection fix for preventing unrelated frameworks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import generate_course_domain_strategic_lens, detect_course_concept_domains, extract_application_field

def test_linear_optimization_query():
    """Test that linear optimization queries exclude Monte Carlo simulation."""
    
    print("🔍 Testing Linear Optimization Query")
    print("=" * 50)
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    
    try:
        domains = detect_course_concept_domains(query)
        application_field = extract_application_field(query)
        course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
        
        strategic_lens = generate_course_domain_strategic_lens(query, course_domain, application_field)
        
        print(f"Query: {query}")
        print(f"Domain: {course_domain}")
        print(f"Application field: {application_field}")
        
        # Check for unwanted frameworks
        unwanted = ["Monte Carlo simulation", "Monte Carlo", "simulation"]
        found_unwanted = [fw for fw in unwanted if fw.lower() in strategic_lens.lower()]
        
        if found_unwanted:
            print(f"❌ PROBLEM: Found unwanted frameworks: {found_unwanted}")
            return False
        else:
            print("✅ No unwanted frameworks found")
        
        # Check for wanted frameworks
        wanted = ["Linear optimization", "optimization"]
        found_wanted = [fw for fw in wanted if fw.lower() in strategic_lens.lower()]
        
        if found_wanted:
            print(f"✅ Found relevant frameworks: {found_wanted}")
            return True
        else:
            print("❌ No relevant frameworks found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_monte_carlo_query():
    """Test that Monte Carlo queries exclude linear optimization."""
    
    print(f"\n🔍 Testing Monte Carlo Query")
    print("=" * 50)
    
    query = "How can I use Monte Carlo simulation to analyze risk in my investment portfolio?"
    
    try:
        domains = detect_course_concept_domains(query)
        application_field = extract_application_field(query)
        course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
        
        strategic_lens = generate_course_domain_strategic_lens(query, course_domain, application_field)
        
        print(f"Query: {query}")
        print(f"Domain: {course_domain}")
        print(f"Application field: {application_field}")
        
        # Check for unwanted frameworks
        unwanted = ["Linear optimization", "linear programming", "optimization"]
        found_unwanted = [fw for fw in unwanted if fw.lower() in strategic_lens.lower()]
        
        if found_unwanted:
            print(f"❌ PROBLEM: Found unwanted frameworks: {found_unwanted}")
            return False
        else:
            print("✅ No unwanted frameworks found")
        
        # Check for wanted frameworks
        wanted = ["Monte Carlo simulation", "Monte Carlo", "simulation"]
        found_wanted = [fw for fw in wanted if fw.lower() in strategic_lens.lower()]
        
        if found_wanted:
            print(f"✅ Found relevant frameworks: {found_wanted}")
            return True
        else:
            print("❌ No relevant frameworks found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_general_query():
    """Test that general queries work without conflicts."""
    
    print(f"\n🔍 Testing General Query")
    print("=" * 50)
    
    query = "How should I choose between two job offers?"
    
    try:
        domains = detect_course_concept_domains(query)
        application_field = extract_application_field(query)
        course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
        
        strategic_lens = generate_course_domain_strategic_lens(query, course_domain, application_field)
        
        print(f"Query: {query}")
        print(f"Domain: {course_domain}")
        print(f"Application field: {application_field}")
        
        # Check that frameworks are selected
        if "using" in strategic_lens and "and" in strategic_lens:
            print("✅ Frameworks are being selected")
            return True
        else:
            print("❌ No frameworks found in response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_framework_conflict_prevention():
    """Test that the conflict prevention logic works."""
    
    print(f"\n🔧 Testing Framework Conflict Prevention")
    print("=" * 50)
    
    test_cases = [
        {
            "query": "How does linear optimization help with resource allocation?",
            "should_exclude": ["Monte Carlo", "simulation"],
            "should_include": ["Linear optimization", "optimization"]
        },
        {
            "query": "What Monte Carlo simulation approach should I use for risk analysis?",
            "should_exclude": ["Linear optimization", "linear programming"],
            "should_include": ["Monte Carlo", "simulation"]
        },
        {
            "query": "How do I use sensitivity analysis for decision making?",
            "should_exclude": [],  # No specific exclusions
            "should_include": ["Sensitivity analysis", "sensitivity"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['query']}")
        
        try:
            domains = detect_course_concept_domains(test_case['query'])
            application_field = extract_application_field(test_case['query'])
            course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
            
            strategic_lens = generate_course_domain_strategic_lens(test_case['query'], course_domain, application_field)
            
            # Check exclusions
            found_excluded = []
            for exclude in test_case['should_exclude']:
                if exclude.lower() in strategic_lens.lower():
                    found_excluded.append(exclude)
            
            if found_excluded:
                print(f"❌ Found excluded frameworks: {found_excluded}")
                results.append(False)
            else:
                print("✅ No excluded frameworks found")
                
                # Check inclusions
                found_included = []
                for include in test_case['should_include']:
                    if include.lower() in strategic_lens.lower():
                        found_included.append(include)
                
                if found_included:
                    print(f"✅ Found included frameworks: {found_included}")
                    results.append(True)
                else:
                    print("❌ No included frameworks found")
                    results.append(False)
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Framework Selection Fix Verification")
    print("=" * 60)
    
    # Run all tests
    test1 = test_linear_optimization_query()
    test2 = test_monte_carlo_query()
    test3 = test_general_query()
    test4_results = test_framework_conflict_prevention()
    
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    print(f"Linear Optimization Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Monte Carlo Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"General Query Test: {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"Conflict Prevention Tests: {'✅ PASS' if all(test4_results) else '❌ FAIL'}")
    
    overall_success = test1 and test2 and test3 and all(test4_results)
    
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("✅ Framework selection fix is working correctly!")
    else:
        print("❌ Framework selection still needs improvement") 