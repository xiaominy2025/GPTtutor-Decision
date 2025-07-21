#!/usr/bin/env python3
"""
Simple test to check if query_engine.py can run without syntax errors
"""

try:
    import query_engine
    print("✅ query_engine.py imported successfully - no syntax errors")
except SyntaxError as e:
    print(f"❌ Syntax error in query_engine.py: {e}")
except Exception as e:
    print(f"❌ Error importing query_engine.py: {e}")

from query_engine import process_query

if __name__ == "__main__":
    question = "I'm offered a new job. How to decide to accept it or not?"
    output = process_query(question)
    print(output)

print("✅ Test completed") 