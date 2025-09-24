#!/usr/bin/env python3
"""
Test script to check decision tree detection for job offer queries
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 TESTING DECISION TREE DETECTION FOR JOB OFFERS")
print("=" * 60)

try:
    from query_engine import detect_course_concept_domains, classify_analytical_subdomain, extract_application_fields
    print("✅ Import successful")
    
    # Test queries that should trigger decision tree detection
    test_queries = [
        "I have two job offers, how do I decide?",
        "Should I accept this job offer or stay at my current job?",
        "How do I compare two job offers?",
        "I need to choose between two job offers with different salaries",
        "How do I evaluate multiple job offers?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        # Check domain detection
        domains = detect_course_concept_domains(query)
        print(f"Detected domains: {domains}")
        
        # Check analytical subdomain
        analytical_focus = classify_analytical_subdomain(query)
        print(f"Analytical focus: {analytical_focus}")
        
        # Check fields
        fields = extract_application_fields(query)
        print(f"Application fields: {fields}")
        
        # Check if decision tree should be triggered
        has_multiple_options = any(word in query.lower() for word in ["two", "multiple", "compare", "choose between", "decide between"])
        has_job_keywords = any(word in query.lower() for word in ["job", "offer", "career"])
        
        print(f"Has multiple options: {has_multiple_options}")
        print(f"Has job keywords: {has_job_keywords}")
        
        # Expected behavior
        should_have_strategy = "strategy" in domains
        should_have_analytical = "analytical_tools" in domains
        should_be_decision_tree = analytical_focus == "decision_tree"
        
        print(f"✅ Strategy domain: {should_have_strategy}")
        print(f"✅ Analytical domain: {should_have_analytical}")
        print(f"✅ Decision tree focus: {should_be_decision_tree}")
        
        print("-" * 40)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 