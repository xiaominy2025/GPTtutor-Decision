#!/usr/bin/env python3
"""
Fix the three key issues:
1. Improve keyword identification by relaxing cluster logic
2. Tighten hybrid cluster logic to filter out weak semantic results
3. Fix negotiation false positives by improving semantic detection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'Repeatability'))

from query_engine import hybrid_domain_detection, detect_domain_semantic, detect_course_concept_domains

def test_fixes():
    """Test the proposed fixes."""
    
    # The problematic queries
    problem_queries = [
        # Query 1: (T + S) - NO NEGOTIATION
        ("A demand forecasting model shows high error variance across product categories. How should this influence strategic capacity planning?", 
         ['technical', 'strategic']),
        
        # Query 12: (T + S) - NO NEGOTIATION  
        ("A simulation model suggests two different investment strategies have similar expected returns but different risk profiles. How should executives choose?", 
         ['technical', 'strategic']),
        
        # Query 17: (S + T + H) - NO NEGOTIATION
        ("A company must choose between investing in new technology or improving existing processes. How should they evaluate this strategic trade-off?", 
         ['strategic', 'technical', 'behavioral'])
    ]
    
    print("🔧 TESTING PROPOSED FIXES")
    print("=" * 50)
    print()
    
    for i, query_num in enumerate([1, 12, 17], 1):
        query_text, expected_domains = problem_queries[i-1]
        print(f"🔍 QUERY {query_num}: {query_text[:80]}...")
        print(f"Expected: {expected_domains}")
        print()
        
        # Get current results
        semantic_result = detect_domain_semantic(query_text)
        keyword_result = detect_course_concept_domains(query_text)
        hybrid_result = hybrid_domain_detection(query_text)
        
        print("📊 CURRENT RESULTS:")
        print(f"Semantic: {list(semantic_result.keys())} - Scores: {semantic_result}")
        print(f"Keyword:  {list(keyword_result.keys())} - Scores: {keyword_result}")
        print(f"Hybrid:   {list(hybrid_result.keys())} - Scores: {hybrid_result}")
        print()
        
        # Check issues
        hybrid_domains = list(hybrid_result.keys())
        extra_domains = [d for d in hybrid_domains if d not in expected_domains]
        missing_domains = [d for d in expected_domains if d not in hybrid_domains]
        
        if extra_domains:
            print(f"❌ Extra domains: {extra_domains}")
        if missing_domains:
            print(f"❌ Missing domains: {missing_domains}")
        if not extra_domains and not missing_domains:
            print("✅ Perfect match!")
        
        print("-" * 60)
        print()

def propose_fixes():
    """Propose specific fixes for each issue."""
    
    print("🔧 PROPOSED FIXES")
    print("=" * 50)
    print()
    
    print("ISSUE 1: Keyword Under-Identification")
    print("-" * 40)
    print("Problem: Keyword method misses domains even when keywords are present")
    print("Root Cause: 15% inclusion band is too restrictive")
    print("Fix: Relax keyword cluster logic to 25% inclusion band")
    print("Impact: Will catch more domains but may include some noise")
    print()
    
    print("ISSUE 2: Hybrid Cluster Logic Too Lenient")
    print("-" * 40)
    print("Problem: 5% inclusion band lets weak semantic results through")
    print("Root Cause: Final threshold too permissive")
    print("Fix: Tighten hybrid cluster logic to 2% inclusion band")
    print("Impact: Will filter out weak domains like negotiation false positives")
    print()
    
    print("ISSUE 3: Negotiation False Positives")
    print("-" * 40)
    print("Problem: Semantic method finds weak negotiation similarities (~0.32)")
    print("Root Cause: Semantic reference queries too broad")
    print("Fix: Add negotiation bias - require higher threshold for negotiation")
    print("Impact: Will reduce false positives while preserving true positives")
    print()
    
    print("IMPLEMENTATION STRATEGY:")
    print("1. Modify select_domains_with_rules function")
    print("2. Add negotiation-specific bias logic")
    print("3. Test with problem queries")
    print("4. Validate on full 20-query set")

def analyze_keyword_keywords():
    """Analyze why keywords are being missed."""
    
    print("🔍 KEYWORD ANALYSIS")
    print("=" * 50)
    print()
    
    # Test specific keywords
    test_queries = [
        ("strategic planning", "Should identify strategic"),
        ("investment decision", "Should identify strategic"), 
        ("cognitive bias", "Should identify behavioral"),
        ("machine learning model", "Should identify technical")
    ]
    
    for query, expected in test_queries:
        print(f"Query: '{query}' - {expected}")
        result = detect_course_concept_domains(query)
        print(f"Result: {result}")
        print()

if __name__ == "__main__":
    test_fixes()
    print("\n" + "="*60 + "\n")
    propose_fixes()
    print("\n" + "="*60 + "\n")
    analyze_keyword_keywords()
