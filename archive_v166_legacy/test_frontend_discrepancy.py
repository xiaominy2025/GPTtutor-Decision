#!/usr/bin/env python3
"""
Test script to compare frontend vs direct query_engine output
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 FRONTEND vs DIRECT QUERY_ENGINE COMPARISON")
print("=" * 60)

try:
    from query_engine import process_query
    print("✅ Import successful")
    
    # Test the specific query from the frontend
    test_query = "my team members are reluctant to give up his legacy projects, how shall I convience him to think differently?"
    
    print(f"\n📝 TESTING QUERY: {test_query}")
    print("=" * 60)
    
    # Get direct query_engine output
    direct_answer = process_query(test_query)
    
    print(f"\n📝 DIRECT QUERY_ENGINE OUTPUT:")
    print(f"'{direct_answer}'")
    
    # Analyze the content
    print(f"\n🔍 CONTENT ANALYSIS:")
    print(f"   Word count: {len(direct_answer.split())} words")
    
    # Check for specific content indicators
    answer_lower = direct_answer.lower()
    
    # Check for human behavior content
    has_behavior_content = any(term in answer_lower for term in ["escalation", "commitment", "prospect theory", "psychological", "bias"])
    print(f"   Human behavior content: {'✅' if has_behavior_content else '❌'}")
    
    # Check for scenario planning content (from frontend)
    has_scenario_content = any(term in answer_lower for term in ["scenario planning", "monte carlo", "simulation"])
    print(f"   Scenario planning content: {'✅' if has_scenario_content else '❌'}")
    
    # Check for specific concepts mentioned
    if "escalation of commitment" in answer_lower:
        print(f"   ✅ Mentions 'Escalation of Commitment'")
    if "prospect theory" in answer_lower:
        print(f"   ✅ Mentions 'Prospect Theory'")
    if "scenario planning" in answer_lower:
        print(f"   ✅ Mentions 'Scenario Planning'")
    if "monte carlo" in answer_lower:
        print(f"   ✅ Mentions 'Monte Carlo'")
    
    print(f"\n✅ Analysis complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 