#!/usr/bin/env python3
"""
Comprehensive Stability Test
===========================

This test validates function stability and answer quality requirements:
1. Function stability (no crashes, consistent outputs)
2. Answer quality (follow-up questions, concepts, formatting)
3. Domain detection accuracy
4. Response completeness
"""

import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    process_query,
    generate_domain_aware_followup_prompt,
    generate_domain_aware_followup_questions,
    detect_course_concept_domains,
    get_top_ranked_concepts_with_lens_shifting
)

def test_function_stability():
    """Test that all functions run without crashing"""
    print("🧪 Testing Function Stability")
    print("=" * 50)
    
    test_queries = [
        "How do I optimize production using linear programming?",
        "What are the key factors in choosing between two job offers?",
        "How do personal biases affect my ethical decisions?",
        "How should I negotiate with a dominant supplier?",
        "How should I balance technical efficiency with strategic goals?",
        "What should I consider when making a decision?",
        "",  # Empty query
        "a",  # Very short query
        "This is a very long query that contains many words and should test the system's ability to handle complex inputs with multiple domains and concepts that need to be processed correctly",  # Very long query
    ]
    
    stability_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:50]}...")
        
        try:
            # Test main process_query function
            result = process_query(query)
            print("✅ process_query: No crash")
            
            # Test domain detection
            domains = detect_course_concept_domains(query)
            print("✅ detect_course_concept_domains: No crash")
            
            # Test follow-up prompt generation
            prompt = generate_domain_aware_followup_prompt(query)
            print("✅ generate_domain_aware_followup_prompt: No crash")
            
            # Test fallback questions
            fallback_questions = generate_domain_aware_followup_questions(query)
            print("✅ generate_domain_aware_followup_questions: No crash")
            
            # Test concept extraction
            concepts = get_top_ranked_concepts_with_lens_shifting(query, top_k=4, is_followup=False)
            print("✅ get_top_ranked_concepts_with_lens_shifting: No crash")
            
            stability_results.append(True)
            
        except Exception as e:
            print(f"❌ CRASH: {type(e).__name__}: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            stability_results.append(False)
    
    success_rate = sum(stability_results) / len(stability_results) * 100
    print(f"\n📊 Function Stability: {success_rate:.1f}% ({sum(stability_results)}/{len(stability_results)})")
    
    return success_rate >= 90  # Require 90% stability

def test_answer_quality():
    """Test answer quality requirements"""
    print("\n🧪 Testing Answer Quality")
    print("=" * 50)
    
    test_queries = [
        "How do I optimize production using linear programming?",
        "What are the key factors in choosing between two job offers?",
        "How do personal biases affect my ethical decisions?",
        "How should I negotiate with a dominant supplier?"
    ]
    
    quality_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:50]}...")
        
        try:
            result = process_query(query)
            
            # Check response length
            if len(result) > 500:
                print("✅ Response length: Adequate")
            else:
                print("❌ Response length: Too short")
            
            # Check for required sections
            required_sections = [
                "**Strategic Framing**",
                "**Story in Action**", 
                "**Follow-up Prompts**",
                "**Concepts/Tools**"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section in result:
                    print(f"✅ {section}: Present")
                else:
                    print(f"❌ {section}: Missing")
                    missing_sections.append(section)
            
            # Check follow-up questions count
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
            
            print(f"📊 Follow-up questions found: {question_count}")
            
            if 2 <= question_count <= 4:
                print("✅ Follow-up questions: Correct count")
            else:
                print(f"❌ Follow-up questions: Incorrect count ({question_count})")
            
            # Check concepts count
            concepts_section = False
            concept_count = 0
            
            for line in lines:
                if "**Concepts/Tools**" in line:
                    concepts_section = True
                elif concepts_section and line.strip().startswith('- '):
                    concept_count += 1
                elif concepts_section and line.strip().startswith('**'):
                    break
            
            print(f"📊 Concepts found: {concept_count}")
            
            if 2 <= concept_count <= 4:
                print("✅ Concepts: Correct count")
            else:
                print(f"❌ Concepts: Incorrect count ({concept_count})")
            
            # Overall quality assessment
            quality_score = 0
            if len(result) > 500:
                quality_score += 25
            if len(missing_sections) == 0:
                quality_score += 25
            if 2 <= question_count <= 4:
                quality_score += 25
            if 2 <= concept_count <= 4:
                quality_score += 25
            
            print(f"📊 Quality Score: {quality_score}/100")
            
            if quality_score >= 75:
                print("✅ Answer Quality: Good")
                quality_results.append(True)
            else:
                print("❌ Answer Quality: Poor")
                quality_results.append(False)
                
        except Exception as e:
            print(f"❌ Error testing answer quality: {e}")
            quality_results.append(False)
    
    success_rate = sum(quality_results) / len(quality_results) * 100
    print(f"\n📊 Answer Quality: {success_rate:.1f}% ({sum(quality_results)}/{len(quality_results)})")
    
    return success_rate >= 75  # Require 75% quality

def test_domain_detection_accuracy():
    """Test domain detection accuracy"""
    print("\n🧪 Testing Domain Detection Accuracy")
    print("=" * 50)
    
    test_cases = [
        ("Technical query", "How do I optimize production using linear programming?", ["technical"]),
        ("Strategic query", "What are the key factors in choosing between two job offers?", ["strategic"]),
        ("Behavioral query", "How do personal biases affect my ethical decisions?", ["behavioral"]),
        ("Negotiation query", "How should I negotiate with a dominant supplier?", ["negotiation"]),
        ("Multi-domain query", "How should I balance technical efficiency with strategic goals?", ["technical", "strategic"]),
    ]
    
    accuracy_results = []
    
    for test_name, query, expected_domains in test_cases:
        print(f"\n📋 {test_name}")
        
        try:
            domains = detect_course_concept_domains(query)
            
            # Find primary domain (highest score)
            if domains:
                primary_domain = max(domains.items(), key=lambda x: x[1])
                detected_domain = primary_domain[0]
                score = primary_domain[1]
                
                print(f"📊 Detected primary domain: {detected_domain} (score: {score:.2f})")
                
                if detected_domain in expected_domains:
                    print("✅ Domain detection: Correct")
                    accuracy_results.append(True)
                else:
                    print(f"❌ Domain detection: Expected {expected_domains}, got {detected_domain}")
                    accuracy_results.append(False)
            else:
                print("❌ Domain detection: No domains detected")
                accuracy_results.append(False)
                
        except Exception as e:
            print(f"❌ Error in domain detection: {e}")
            accuracy_results.append(False)
    
    success_rate = sum(accuracy_results) / len(accuracy_results) * 100
    print(f"\n📊 Domain Detection Accuracy: {success_rate:.1f}% ({sum(accuracy_results)}/{len(accuracy_results)})")
    
    return success_rate >= 80  # Require 80% accuracy

def test_response_completeness():
    """Test response completeness and formatting"""
    print("\n🧪 Testing Response Completeness")
    print("=" * 50)
    
    test_queries = [
        "How do I optimize production using linear programming?",
        "What are the key factors in choosing between two job offers?"
    ]
    
    completeness_results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:50]}...")
        
        try:
            result = process_query(query)
            
            # Check for proper markdown formatting
            if "**" in result and "##" in result:
                print("✅ Markdown formatting: Good")
            else:
                print("❌ Markdown formatting: Poor")
            
            # Check for logical flow
            sections = result.split("**")
            if len(sections) >= 4:
                print("✅ Logical flow: Good")
            else:
                print("❌ Logical flow: Poor")
            
            # Check for content relevance
            if any(word in result.lower() for word in query.lower().split()):
                print("✅ Content relevance: Good")
            else:
                print("❌ Content relevance: Poor")
            
            # Overall completeness assessment
            completeness_score = 0
            if "**" in result and "##" in result:
                completeness_score += 33
            if len(sections) >= 4:
                completeness_score += 33
            if any(word in result.lower() for word in query.lower().split()):
                completeness_score += 34
            
            print(f"📊 Completeness Score: {completeness_score}/100")
            
            if completeness_score >= 66:
                print("✅ Response Completeness: Good")
                completeness_results.append(True)
            else:
                print("❌ Response Completeness: Poor")
                completeness_results.append(False)
                
        except Exception as e:
            print(f"❌ Error testing completeness: {e}")
            completeness_results.append(False)
    
    success_rate = sum(completeness_results) / len(completeness_results) * 100
    print(f"\n📊 Response Completeness: {success_rate:.1f}% ({sum(completeness_results)}/{len(completeness_results)})")
    
    return success_rate >= 75  # Require 75% completeness

def run_comprehensive_stability_test():
    """Run all comprehensive stability tests"""
    print("🚀 Comprehensive Stability and Quality Test")
    print("=" * 80)
    
    tests = [
        ("Function Stability", test_function_stability),
        ("Answer Quality", test_answer_quality),
        ("Domain Detection Accuracy", test_domain_detection_accuracy),
        ("Response Completeness", test_response_completeness)
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
    print("\n📊 COMPREHENSIVE STABILITY SUMMARY")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 System is stable and meets quality requirements!")
        return True
    else:
        print("⚠️ Some stability or quality issues need attention.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_stability_test()
    sys.exit(0 if success else 1) 