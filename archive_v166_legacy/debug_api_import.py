#!/usr/bin/env python3
"""
Debug script to check what the API server is actually importing
"""
import sys
import os

print("🔍 DEBUGGING API SERVER IMPORTS")
print("=" * 60)

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check Python path
print(f"Python path: {sys.path}")

# Try to import query_engine and check its content
try:
    import query_engine
    print(f"✅ Successfully imported query_engine from: {query_engine.__file__}")
    
    # Check if process_query function exists
    if hasattr(query_engine, 'process_query'):
        print("✅ process_query function exists")
        
        # Test the function directly
        test_query = "my team members are reluctant to give up his legacy projects, how shall I convience him to think differently?"
        print(f"Testing query: {test_query}")
        
        answer = query_engine.process_query(test_query)
        print(f"Direct answer: {answer[:200]}...")
        
        # Check for specific content
        answer_lower = answer.lower()
        if "escalation of commitment" in answer_lower:
            print("✅ Contains 'Escalation of Commitment'")
        if "prospect theory" in answer_lower:
            print("✅ Contains 'Prospect Theory'")
        if "scenario planning" in answer_lower:
            print("✅ Contains 'Scenario Planning'")
        if "monte carlo" in answer_lower:
            print("✅ Contains 'Monte Carlo'")
            
    else:
        print("❌ process_query function does not exist")
        
except Exception as e:
    print(f"❌ Error importing query_engine: {e}")
    import traceback
    traceback.print_exc()

print(f"\n✅ Debug complete!") 