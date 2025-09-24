#!/usr/bin/env python3
"""
Test Keyword-Based Framework Selection
=====================================

Test script to verify that framework selection is now truly keyword-based
and prioritizes frameworks based on keyword matches in the query.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query, detect_course_concept_domains

def test_keyword_framework_selection():
    """Test that framework selection is keyword-based"""
    print("🧪 Testing Keyword-Based Framework Selection")
    print("=" * 60)
    
    # Test cases with expected keyword matches
    test_cases = [
        # Technical domain tests
        {
            "query": "How does linear optimization inform your approach to balancing efficiency with flexibility?",
            "expected_keywords": ["linear", "optimization"],
            "expected_frameworks": ["Linear optimization modeling"],
            "domain": "technical"
        },
        {
            "query": "What are the benefits of Monte Carlo simulation in risk analysis?",
            "expected_keywords": ["monte carlo", "simulation", "risk"],
            "expected_frameworks": ["Monte Carlo simulation"],
            "domain": "technical"
        },
        {
            "query": "How do I perform sensitivity analysis on my decision variables?",
            "expected_keywords": ["sensitivity", "analysis"],
            "expected_frameworks": ["Sensitivity analysis"],
            "domain": "technical"
        },
        {
            "query": "Should I use decision tree analysis for this multi-stage problem?",
            "expected_keywords": ["decision tree", "tree"],
            "expected_frameworks": ["Decision tree analysis"],
            "domain": "technical"
        },
        
        # Strategic domain tests
        {
            "query": "How do Porter's Five Forces affect my competitive strategy?",
            "expected_keywords": ["porter", "five forces", "competitive"],
            "expected_frameworks": ["Porter's Five Forces analysis"],
            "domain": "strategic"
        },
        {
            "query": "What are my company's strengths and weaknesses in this SWOT analysis?",
            "expected_keywords": ["swot", "strength", "weakness"],
            "expected_frameworks": ["SWOT analysis"],
            "domain": "strategic"
        },
        {
            "query": "How does value chain analysis help optimize operations?",
            "expected_keywords": ["value chain", "chain"],
            "expected_frameworks": ["Value Chain analysis"],
            "domain": "strategic"
        },
        
        # Behavioral domain tests
        {
            "query": "How do cognitive biases affect my decision making process?",
            "expected_keywords": ["cognitive", "bias", "decision making"],
            "expected_frameworks": ["Cognitive bias assessment"],
            "domain": "behavioral"
        },
        {
            "query": "What stakeholder analysis should I conduct for this project?",
            "expected_keywords": ["stakeholder", "analysis"],
            "expected_frameworks": ["Stakeholder analysis"],
            "domain": "behavioral"
        },
        
        # Negotiation domain tests
        {
            "query": "What is my BATNA in this negotiation situation?",
            "expected_keywords": ["batna", "negotiation"],
            "expected_frameworks": ["BATNA analysis"],
            "domain": "negotiation"
        },
        {
            "query": "How do I find the ZOPA in this bargaining scenario?",
            "expected_keywords": ["zopa", "bargaining"],
            "expected_frameworks": ["Zone of Possible Agreement (ZOPA) mapping"],
            "domain": "negotiation"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['query'][:60]}...")
        
        try:
            # Get domain detection
            domains = detect_course_concept_domains(test_case['query'])
            if domains:
                primary_domain = max(domains.items(), key=lambda x: x[1])
                detected_domain = primary_domain[0]
                print(f"📊 Detected domain: {detected_domain} (expected: {test_case['domain']})")
                
                # Check domain accuracy
                domain_correct = detected_domain == test_case['domain']
                if domain_correct:
                    print("✅ Domain detection: Correct")
                else:
                    print(f"❌ Domain detection: Expected {test_case['domain']}, got {detected_domain}")
            
            # Get response
            result = process_query(test_case['query'])
            
            # Extract Strategic Thinking Lens section
            lines = result.split('\n')
            strategic_lens_section = False
            lens_content = []
            
            for line in lines:
                if "**Strategic Thinking Lens**" in line:
                    strategic_lens_section = True
                elif strategic_lens_section and line.strip().startswith('**'):
                    break
                elif strategic_lens_section:
                    lens_content.append(line)
            
            lens_text = '\n'.join(lens_content)
            
            # Check for expected keywords in the lens content
            keyword_matches = []
            for keyword in test_case['expected_keywords']:
                if keyword in lens_text.lower():
                    keyword_matches.append(keyword)
            
            print(f"📊 Expected keywords found: {keyword_matches}")
            
            # Check for expected frameworks in the lens content
            framework_matches = []
            for framework in test_case['expected_frameworks']:
                if framework.lower() in lens_text.lower():
                    framework_matches.append(framework)
            
            print(f"📊 Expected frameworks found: {framework_matches}")
            
            # Evaluate results
            keyword_score = len(keyword_matches) / len(test_case['expected_keywords'])
            framework_score = len(framework_matches) / len(test_case['expected_frameworks'])
            
            if keyword_score >= 0.5 and framework_score >= 0.5:
                print("✅ Keyword-based framework selection: Working")
                results.append(True)
            else:
                print(f"❌ Keyword-based framework selection: Needs improvement")
                print(f"   Keyword score: {keyword_score:.2f}, Framework score: {framework_score:.2f}")
                results.append(False)
            
        except Exception as e:
            print(f"❌ Error testing keyword framework selection: {e}")
            results.append(False)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Keyword-based framework selection is working well!")
    elif success_rate >= 60:
        print("⚠️ Keyword-based framework selection needs some improvement.")
    else:
        print("❌ Keyword-based framework selection needs significant improvement.")
    
    return success_rate >= 70

if __name__ == "__main__":
    success = test_keyword_framework_selection()
    sys.exit(0 if success else 1) 