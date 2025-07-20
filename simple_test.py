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

print("✅ Test completed") 