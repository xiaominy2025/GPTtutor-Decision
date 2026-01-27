#!/usr/bin/env python3
"""
Test script to verify the new application fields are working correctly.
Tests all 7 new application fields: risk_management, project_management, sustainability, 
innovation, human_capital, marketing, and globalization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import extract_application_field, process_query

def test_new_application_fields():
    """Test all new application fields with sample queries."""
    
    test_cases = [
        # Risk Management
        ("How should I assess and mitigate supply chain risks?", "risk_management"),
        ("What contingency plans should I develop for crisis scenarios?", "risk_management"),
        ("How do I evaluate regulatory compliance risks?", "risk_management"),
        
        # Project Management
        ("How should I allocate resources across multiple project milestones?", "project_management"),
        ("What's the critical path for this software development project?", "project_management"),
        ("How do I manage stakeholder expectations in project delivery?", "project_management"),
        
        # Sustainability & ESG
        ("How should I implement ESG initiatives in my business strategy?", "sustainability"),
        ("What carbon footprint reduction strategies should I consider?", "sustainability"),
        ("How do I balance environmental responsibility with profitability?", "sustainability"),
        
        # Innovation & R&D
        ("How should I prioritize competing R&D projects?", "innovation"),
        ("What's the best approach for prototyping new product features?", "innovation"),
        ("How do I evaluate intellectual property protection strategies?", "innovation"),
        
        # Human Capital Strategy
        ("How should I develop a talent pipeline for critical roles?", "human_capital"),
        ("What strategies will improve employee retention and engagement?", "human_capital"),
        ("How do I implement diversity and inclusion initiatives?", "human_capital"),
        
        # Marketing & Customer Strategy
        ("How should I position our brand in a competitive market?", "marketing"),
        ("What customer acquisition strategies should I prioritize?", "marketing"),
        ("How do I optimize marketing spend across multiple channels?", "marketing"),
        
        # Globalization & International Trade
        ("How should I evaluate market entry strategies for emerging economies?", "globalization"),
        ("What factors should I consider when expanding internationally?", "globalization"),
        ("How do I manage currency risk in global operations?", "globalization"),
    ]
    
    print("Testing New Application Fields")
    print("=" * 50)
    
    results = []
    for i, (query, expected) in enumerate(test_cases, 1):
        detected = extract_application_field(query)
        status = "✅" if detected == expected else "❌"
        results.append((i, query, expected, detected, status))
        
        print(f"{i:2d}. {status} | Expected: {expected:15s} | Detected: {detected:15s}")
        print(f"    Query: {query}")
        print()
    
    # Summary
    correct = sum(1 for _, _, _, _, status in results if status == "✅")
    total = len(results)
    
    print("=" * 50)
    print(f"SUMMARY: {correct}/{total} tests passed ({correct/total*100:.1f}%)")
    
    if correct == total:
        print("🎉 All new application fields are working correctly!")
    else:
        print("⚠️  Some tests failed. Check the results above.")
    
    return correct == total

def test_process_query_with_new_fields():
    """Test that process_query works with the new application fields."""
    
    test_queries = [
        "How should I assess and mitigate supply chain risks?",
        "How should I allocate resources across multiple project milestones?",
        "How should I implement ESG initiatives in my business strategy?",
        "How should I prioritize competing R&D projects?",
        "How should I develop a talent pipeline for critical roles?",
        "How should I position our brand in a competitive market?",
        "How should I evaluate market entry strategies for emerging economies?"
    ]
    
    print("\nTesting process_query with new application fields")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 40)
        
        try:
            # Extract application field first
            app_field = extract_application_field(query)
            print(f"Application Field: {app_field}")
            
            # Test process_query
            result = process_query(query)
            if result and "Strategic Thinking Lens" in result:
                print("✅ Process query succeeded")
            else:
                print("❌ Process query failed or returned incomplete result")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ process_query tests completed")

if __name__ == "__main__":
    print("Testing New Application Fields Implementation")
    print("=" * 60)
    
    # Test 1: Application field detection
    success1 = test_new_application_fields()
    
    # Test 2: Process query functionality
    test_process_query_with_new_fields()
    
    if success1:
        print("\n🎉 All tests passed! New application fields are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the results above.") 