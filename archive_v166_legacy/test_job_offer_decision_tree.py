#!/usr/bin/env python3
"""
Test script to check job offer queries generate decision tree content
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 TESTING JOB OFFER DECISION TREE CONTENT")
print("=" * 60)

try:
    from query_engine import process_query, classify_analytical_subdomain
    print("✅ Import successful")
    
    # Test job offer queries that should trigger decision tree content
    test_queries = [
        "I have two job offers, how do I decide?",
        "How do I compare two job offers?",
        "I need to choose between two job offers with different salaries"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        # Check analytical subdomain
        analytical_focus = classify_analytical_subdomain(query)
        print(f"Analytical focus: {analytical_focus}")
        
        # Generate full answer
        answer = process_query(query)
        
        print(f"\nGenerated Answer:")
        print(f"'{answer}'")
        
        # Check for decision tree content
        answer_lower = answer.lower()
        has_decision_tree = "decision tree" in answer_lower or "decision trees" in answer_lower
        has_comparison = "compare" in answer_lower or "comparing" in answer_lower
        has_structured = "structured framework" in answer_lower
        has_benefits_costs = "benefits and costs" in answer_lower or "benefits and costs" in answer_lower
        
        print(f"\nContent Analysis:")
        print(f"✅ Decision tree mentioned: {has_decision_tree}")
        print(f"✅ Comparison language: {has_comparison}")
        print(f"✅ Structured framework: {has_structured}")
        print(f"✅ Benefits/costs evaluation: {has_benefits_costs}")
        
        # Check for simulation content (should be minimal for job offers)
        has_simulation = "simulation" in answer_lower or "monte carlo" in answer_lower
        print(f"⚠️  Simulation content: {has_simulation} (should be minimal for job offers)")
        
        print("-" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 