#!/usr/bin/env python3
"""
Test Linear Optimization Framework Selection
==========================================

Test script to verify that framework selection properly prioritizes
linear optimization when the query contains relevant keywords and
excludes Monte Carlo simulation when simulation keywords are absent.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query, generate_course_domain_strategic_lens, detect_course_concept_domains

def test_linear_optimization_framework_selection():
    """Test that linear optimization is properly prioritized over Monte Carlo"""
    print("🧪 Testing Linear Optimization Framework Selection")
    print("=" * 60)
    
    # Test case 1: Query with linear optimization keywords
    query1 = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    print(f"📋 Test Case 1: {query1}")
    
    try:
        # Get domain detection
        domains = detect_course_concept_domains(query1)
        course_domain = domains.get('primary_domain', 'general')
        print(f"📊 Detected domain: {course_domain}")
        
        # Generate strategic lens
        result1 = generate_course_domain_strategic_lens(query1, course_domain)
        
        # Check framework mentions
        linear_mentions = result1.lower().count('linear')
        monte_carlo_mentions = result1.lower().count('monte carlo')
        
        print(f"📊 Framework mentions in result:")
        print(f"  Linear optimization: {linear_mentions}")
        print(f"  Monte Carlo: {monte_carlo_mentions}")
        
        if linear_mentions > monte_carlo_mentions:
            print("✅ Linear optimization properly emphasized")
            case1_success = True
        else:
            print("❌ Linear optimization not properly emphasized")
            case1_success = False
        
        print(f"\n📋 Strategic Lens Content:")
        print(result1[:500] + "..." if len(result1) > 500 else result1)
        
    except Exception as e:
        print(f"❌ Error in test case 1: {e}")
        case1_success = False
    
    print("\n" + "=" * 60)
    
    # Test case 2: Query with simulation keywords
    query2 = "How does Monte Carlo simulation help with risk assessment in project planning?"
    print(f"📋 Test Case 2: {query2}")
    
    try:
        # Get domain detection
        domains = detect_course_concept_domains(query2)
        course_domain = domains.get('primary_domain', 'general')
        print(f"📊 Detected domain: {course_domain}")
        
        # Generate strategic lens
        result2 = generate_course_domain_strategic_lens(query2, course_domain)
        
        # Check framework mentions
        linear_mentions = result2.lower().count('linear')
        monte_carlo_mentions = result2.lower().count('monte carlo')
        
        print(f"📊 Framework mentions in result:")
        print(f"  Linear optimization: {linear_mentions}")
        print(f"  Monte Carlo: {monte_carlo_mentions}")
        
        if monte_carlo_mentions > linear_mentions:
            print("✅ Monte Carlo properly emphasized")
            case2_success = True
        else:
            print("❌ Monte Carlo not properly emphasized")
            case2_success = False
        
        print(f"\n📋 Strategic Lens Content:")
        print(result2[:500] + "..." if len(result2) > 500 else result2)
        
    except Exception as e:
        print(f"❌ Error in test case 2: {e}")
        case2_success = False
    
    print("\n" + "=" * 60)
    
    # Test case 3: Query with multiple keywords
    query3 = "How should I use linear optimization and sensitivity analysis for production planning?"
    print(f"📋 Test Case 3: {query3}")
    
    try:
        # Get domain detection
        domains = detect_course_concept_domains(query3)
        course_domain = domains.get('primary_domain', 'general')
        print(f"📊 Detected domain: {course_domain}")
        
        # Generate strategic lens
        result3 = generate_course_domain_strategic_lens(query3, course_domain)
        
        # Check framework mentions
        linear_mentions = result3.lower().count('linear')
        sensitivity_mentions = result3.lower().count('sensitivity')
        monte_carlo_mentions = result3.lower().count('monte carlo')
        
        print(f"📊 Framework mentions in result:")
        print(f"  Linear optimization: {linear_mentions}")
        print(f"  Sensitivity analysis: {sensitivity_mentions}")
        print(f"  Monte Carlo: {monte_carlo_mentions}")
        
        # Both linear and sensitivity should be mentioned, Monte Carlo should not
        if linear_mentions > 0 and sensitivity_mentions > 0 and monte_carlo_mentions == 0:
            print("✅ Multiple keywords properly handled")
            case3_success = True
        else:
            print("❌ Multiple keywords not properly handled")
            case3_success = False
        
        print(f"\n📋 Strategic Lens Content:")
        print(result3[:500] + "..." if len(result3) > 500 else result3)
        
    except Exception as e:
        print(f"❌ Error in test case 3: {e}")
        case3_success = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_cases = 3
    passed_cases = sum([case1_success, case2_success, case3_success])
    
    print(f"✅ Passed: {passed_cases}/{total_cases}")
    print(f"❌ Failed: {total_cases - passed_cases}/{total_cases}")
    
    if passed_cases == total_cases:
        print("🎉 All tests passed! Framework selection is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Framework selection needs improvement.")
        return False

if __name__ == "__main__":
    success = test_linear_optimization_framework_selection()
    sys.exit(0 if success else 1) 