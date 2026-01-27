#!/usr/bin/env python3
"""
Comprehensive test for semantic application field detection
"""

import sys
import os
from query_engine import process_query, load_data_lazily, extract_application_field_semantic, extract_application_field

def test_comprehensive_semantic():
    """Comprehensive test for semantic application field detection"""
    
    print("🧪 Comprehensive Semantic Application Field Testing")
    print("=" * 70)
    
    # Test queries covering all application fields
    test_queries = [
        # Leadership queries
        ("How should I manage my team during a crisis?", "leadership"),
        ("What leadership style should I adopt?", "leadership"),
        ("How do I motivate my employees?", "leadership"),
        
        # Startup queries
        ("Should I start my own business?", "startup"),
        ("How do I validate my startup idea?", "startup"),
        ("What funding options are available for startups?", "startup"),
        
        # Marketing queries
        ("How do I market my new product?", "marketing"),
        ("What's the best pricing strategy?", "marketing"),
        ("How can I improve my brand awareness?", "marketing"),
        
        # Operations queries
        ("How can I optimize my production process?", "operations"),
        ("What's the best way to manage inventory?", "operations"),
        ("How do I improve supply chain efficiency?", "operations"),
        
        # Finance queries
        ("Should I invest in stocks or bonds?", "finance"),
        ("How do I create a budget?", "finance"),
        ("What's the best way to manage cash flow?", "finance"),
        
        # Negotiation queries
        ("How do I negotiate a better contract?", "negotiation"),
        ("What's the best approach for salary negotiation?", "negotiation"),
        ("How do I handle difficult negotiations?", "negotiation"),
        
        # Risk management queries
        ("How do I assess project risks?", "risk_management"),
        ("What risk mitigation strategies should I use?", "risk_management"),
        ("How do I create a risk management plan?", "risk_management"),
        
        # General queries
        ("What tools can help me make better decisions?", "general"),
        ("How do I improve my decision-making skills?", "general"),
        ("What frameworks should I use for analysis?", "general")
    ]
    
    try:
        # Load data lazily to get the model
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        semantic_success = 0
        keyword_success = 0
        total_tests = len(test_queries)
        
        print(f"📊 Testing {total_tests} queries across all application fields...\n")
        
        for i, (query, expected_field) in enumerate(test_queries, 1):
            print(f"🔍 Test {i}/{total_tests}: {query[:50]}...")
            print(f"🎯 Expected: {expected_field}")
            
            # Test semantic detection
            try:
                semantic_field = extract_application_field_semantic(query, model)
                semantic_match = semantic_field == expected_field
                print(f"🔍 Semantic: {semantic_field} {'✅' if semantic_match else '❌'}")
                if semantic_match:
                    semantic_success += 1
            except Exception as e:
                print(f"❌ Semantic failed: {e}")
                semantic_field = "error"
            
            # Test keyword-based detection for comparison
            keyword_field = extract_application_field(query)
            keyword_match = keyword_field == expected_field
            print(f"🔍 Keyword: {keyword_field} {'✅' if keyword_match else '❌'}")
            if keyword_match:
                keyword_success += 1
            
            print("-" * 50)
        
        # Summary statistics
        print("\n📈 COMPREHENSIVE TEST RESULTS")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Semantic Success Rate: {semantic_success}/{total_tests} ({semantic_success/total_tests*100:.1f}%)")
        print(f"Keyword Success Rate: {keyword_success}/{total_tests} ({keyword_success/total_tests*100:.1f}%)")
        
        if semantic_success > keyword_success:
            print("✅ SEMANTIC DETECTION IS SUPERIOR!")
        elif semantic_success == keyword_success:
            print("⚠️ BOTH METHODS PERFORM EQUALLY")
        else:
            print("❌ KEYWORD DETECTION IS BETTER")
        
        # Test full process_query integration
        print("\n🔧 Testing Full Integration...")
        test_integration_queries = [
            "How should I manage my team during a crisis?",
            "Should I start my own business?",
            "How do I market my new product?"
        ]
        
        for query in test_integration_queries:
            print(f"\n📝 Testing: {query}")
            try:
                result = process_query(query)
                print("✅ Full integration test passed")
            except Exception as e:
                print(f"❌ Integration test failed: {e}")
        
        print("\n🎉 Comprehensive testing completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_semantic() 