#!/usr/bin/env python3
import sys
sys.path.insert(0, r'.\Repeatability')
import query_engine

queries = [
    "Under tariff uncertainty, how do I plan my production?",
    "I have two job offers, how to choose?",
    "How to convey bad news to my boss?",
    "How do I negotiate a better salary package with my boss?",
    "How to negotiate with a dealership?",
    "How shall I deal with unfair critiques from my manager?"
]

print("=== QUICK QUERY ASSESSMENT ===")
print()

for i, query in enumerate(queries, 1):
    print(f"Query {i}: {query}")
    try:
        result = query_engine.unified_semantic_extraction(query)
        print(f"  Primary: {result['domain']}")
        print(f"  Selected: {result['domains_selected']}")
        print(f"  Field: {result['application_field']}")
        
        # Quick answer test
        answer = query_engine.process_query(query)
        print(f"  Answer length: {len(answer)} chars")
        print(f"  Has concepts: {'**Concepts/Tools**' in answer}")
        print()
    except Exception as e:
        print(f"  Error: {e}")
        print()

print("=== ASSESSMENT COMPLETE ===")