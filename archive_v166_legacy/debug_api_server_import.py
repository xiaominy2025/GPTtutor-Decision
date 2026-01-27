#!/usr/bin/env python3
"""
Debug script to check what the API server is actually importing
"""
import sys
import os

print("🔍 DEBUGGING API SERVER IMPORTS")
print("=" * 60)

# Simulate exactly what the API server does
try:
    # Import query_engine exactly like the API server
    import query_engine
    print(f"✅ Imported query_engine from: {query_engine.__file__}")
    
    # Check file size
    file_size = os.path.getsize(query_engine.__file__)
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # Test the exact same call as the API server
    test_query = "my team members are reluctant to give up his legacy projects, how shall I convience him to think differently?"
    
    print(f"\n📝 Testing query: {test_query}")
    
    # Call process_query exactly like the API server does
    answer = query_engine.process_query(test_query, course_config={})
    
    print(f"\n📝 Generated answer:")
    print(f"'{answer}'")
    
    # Check for specific content
    answer_lower = answer.lower()
    
    print(f"\n🔍 CONTENT ANALYSIS:")
    print(f"   Word count: {len(answer.split())} words")
    
    # Check for specific content indicators
    has_behavior_content = any(term in answer_lower for term in ["escalation", "commitment", "prospect theory", "psychological", "bias"])
    print(f"   Human behavior content: {'✅' if has_behavior_content else '❌'}")
    
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
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n✅ Debug complete!") 