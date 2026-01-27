#!/usr/bin/env python3
"""
Debug test to understand concept selection for money-related queries
"""

import sys
import os
from query_engine import process_query, clear_concept_cache, detect_course_concept_domains, get_top_ranked_concepts

def debug_money_concept_selection():
    """Debug the concept selection for money-related queries"""
    
    # Clear cache to ensure fresh concept selection
    clear_concept_cache()
    
    # Test query
    test_query = "How should I budget my monthly salary between different expenses?"
    
    print("🔍 Debugging Money-Related Concept Selection")
    print("=" * 50)
    print(f"Query: {test_query}")
    
    # Check domain detection
    print("\n📊 Domain Detection:")
    domains = detect_course_concept_domains(test_query)
    for domain, score in domains.items():
        print(f"  {domain}: {score:.3f}")
    
    # Check if query contains money keywords
    query_lower = test_query.lower()
    money_keywords = ['money', 'financial', 'finance', 'budget', 'budgeting', 'cost', 'price', 'salary', 'salaries', 'investment', 'payment', 'expense', 'expenses', 'income', 'revenue', 'profit', 'loss', 'spending', 'spend', 'saving', 'save']
    found_money_keywords = [kw for kw in money_keywords if kw in query_lower]
    print(f"\n💰 Money Keywords Found: {found_money_keywords}")
    
    # Check concept ranking
    print("\n📋 Concept Ranking:")
    concepts = get_top_ranked_concepts(test_query, top_k=5)
    for i, (name, definition) in enumerate(concepts, 1):
        print(f"  {i}. {name}")
        print(f"     Definition: {definition[:100]}...")
    
    # Generate full response
    print("\n🔄 Generating Full Response...")
    response = process_query(test_query)
    
    print("\n📄 Full Response:")
    print("-" * 50)
    print(response)
    
    # Check for specific concepts in response
    print("\n🔍 Concept Analysis:")
    concepts_to_check = [
        "mental accounting",
        "framing bias", 
        "confirmation bias",
        "anchoring bias",
        "seasonal forecasting",
        "aggregate planning"
    ]
    
    for concept in concepts_to_check:
        present = concept in response.lower()
        status = "✅" if present else "❌"
        print(f"  {status} {concept}: {present}")

if __name__ == "__main__":
    debug_money_concept_selection() 