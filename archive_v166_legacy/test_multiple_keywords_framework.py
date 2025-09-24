#!/usr/bin/env python3
"""
Test Multiple Keywords Framework Selection
========================================

Test script to verify that multiple keywords in a question lead to
the inclusion of all relevant frameworks, and that framework selection
properly prioritizes based on keyword matches.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_multiple_keywords_framework_selection():
    """Test that multiple keywords lead to proper framework selection"""
    print("🧪 Testing Multiple Keywords Framework Selection")
    print("=" * 60)
    
    try:
        from query_engine import generate_course_domain_strategic_lens, detect_course_concept_domains
        print("✅ Imports successful")
        
        # Test cases with multiple keywords
        test_cases = [
            {
                "query": "How does linear optimization and sensitivity analysis help with production planning?",
                "expected_frameworks": ["Linear optimization modeling", "Sensitivity analysis"],
                "expected_domain": "technical",
                "description": "Multiple technical keywords"
            },
            {
                "query": "How should I use SWOT analysis and Porter's Five Forces for competitive strategy?",
                "expected_frameworks": ["SWOT analysis", "Porter's Five Forces analysis"],
                "expected_domain": "strategic",
                "description": "Multiple strategic keywords"
            },
            {
                "query": "What role do stakeholder analysis and cognitive bias assessment play in decision making?",
                "expected_frameworks": ["Stakeholder analysis", "Cognitive bias assessment"],
                "expected_domain": "behavioral",
                "description": "Multiple behavioral keywords"
            },
            {
                "query": "How does Monte Carlo simulation and decision tree analysis inform risk assessment?",
                "expected_frameworks": ["Monte Carlo simulation", "Decision tree analysis"],
                "expected_domain": "technical",
                "description": "Multiple technical keywords (simulation focus)"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['description']}")
            print(f"Query: {test_case['query']}")
            
            try:
                # Get domain detection
                domains = detect_course_concept_domains(test_case['query'])
                course_domain = domains.get('primary_domain', 'general')
                print(f"📊 Detected domain: {course_domain}")
                
                # Generate strategic lens
                result = generate_course_domain_strategic_lens(test_case['query'], course_domain)
                
                # Check for expected framework mentions
                framework_mentions = {}
                for framework in test_case['expected_frameworks']:
                    # Count mentions of key terms from the framework
                    if "linear" in framework.lower():
                        framework_mentions[framework] = result.lower().count('linear')
                    elif "sensitivity" in framework.lower():
                        framework_mentions[framework] = result.lower().count('sensitivity')
                    elif "swot" in framework.lower():
                        framework_mentions[framework] = result.lower().count('swot')
                    elif "porter" in framework.lower() or "five forces" in framework.lower():
                        framework_mentions[framework] = result.lower().count('porter') + result.lower().count('five forces')
                    elif "stakeholder" in framework.lower():
                        framework_mentions[framework] = result.lower().count('stakeholder')
                    elif "cognitive bias" in framework.lower():
                        framework_mentions[framework] = result.lower().count('cognitive bias')
                    elif "monte carlo" in framework.lower():
                        framework_mentions[framework] = result.lower().count('monte carlo')
                    elif "decision tree" in framework.lower():
                        framework_mentions[framework] = result.lower().count('decision tree')
                
                print(f"📊 Framework mentions:")
                for framework, count in framework_mentions.items():
                    print(f"  {framework}: {count}")
                
                # Check if all expected frameworks are mentioned
                all_frameworks_mentioned = all(count > 0 for count in framework_mentions.values())
                
                if all_frameworks_mentioned:
                    print("✅ All expected frameworks mentioned")
                    results.append(True)
                else:
                    print("❌ Not all expected frameworks mentioned")
                    results.append(False)
                
                # Show first 400 characters of result
                print(f"📋 Strategic Lens (first 400 chars):")
                print(result[:400] + "..." if len(result) > 400 else result)
                
            except Exception as e:
                print(f"❌ Error in test case {i}: {e}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_cases = len(test_cases)
        passed_cases = sum(results)
        
        print(f"✅ Passed: {passed_cases}/{total_cases}")
        print(f"❌ Failed: {total_cases - passed_cases}/{total_cases}")
        
        if passed_cases == total_cases:
            print("🎉 All tests passed! Multiple keywords are properly handled.")
            return True
        else:
            print("⚠️ Some tests failed. Multiple keyword handling needs improvement.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_keyword_prioritization():
    """Test that single keywords properly prioritize relevant frameworks"""
    print("\n🧪 Testing Single Keyword Prioritization")
    print("=" * 60)
    
    try:
        from query_engine import generate_course_domain_strategic_lens, detect_course_concept_domains
        
        # Test case: Linear optimization query should prioritize linear optimization over Monte Carlo
        query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
        print(f"📋 Query: {query}")
        
        # Get domain detection
        domains = detect_course_concept_domains(query)
        course_domain = domains.get('primary_domain', 'general')
        print(f"📊 Detected domain: {course_domain}")
        
        # Generate strategic lens
        result = generate_course_domain_strategic_lens(query, course_domain)
        
        # Check framework mentions
        linear_count = result.lower().count('linear')
        monte_carlo_count = result.lower().count('monte carlo')
        
        print(f"📊 Framework mentions:")
        print(f"  Linear optimization: {linear_count}")
        print(f"  Monte Carlo: {monte_carlo_count}")
        
        if linear_count > monte_carlo_count:
            print("✅ Linear optimization properly prioritized over Monte Carlo")
            return True
        else:
            print("❌ Linear optimization not properly prioritized")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Multiple Keywords Framework Selection Tests")
    print("=" * 60)
    
    # Run multiple keywords test
    test1_success = test_multiple_keywords_framework_selection()
    
    # Run single keyword prioritization test
    test2_success = test_single_keyword_prioritization()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST SUMMARY")
    print("=" * 60)
    
    if test1_success and test2_success:
        print("🎉 All framework selection tests passed!")
        print("✅ Multiple keywords are properly handled")
        print("✅ Single keywords properly prioritize relevant frameworks")
        success = True
    else:
        print("⚠️ Some framework selection tests failed")
        success = False
    
    sys.exit(0 if success else 1) 