#!/usr/bin/env python3
"""
Comprehensive 7 queries test with full responses for manual review
"""

import sys
import os
from query_engine import process_query, load_data_lazily

def test_comprehensive_7_queries_full():
    """Test 7 diverse queries and document full answers for manual review"""
    
    print("🧪 Comprehensive 7 Queries Test - Full Responses for Manual Review")
    print("=" * 80)
    
    # 7 diverse test queries covering different domains and application fields
    test_queries = [
        "How should I deal with unfair critiques from my manager?",
        "Should I invest in stocks or bonds for my retirement?",
        "How do I negotiate a better salary package?",
        "What's the best way to optimize my production process?",
        "How can I market my new product effectively?",
        "Should I start my own business or stay employed?",
        "What tools can help me make better decisions?"
    ]
    
    try:
        print("📊 Testing 7 diverse queries for manual review...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 QUERY {i}/7: {query}")
            print("=" * 80)
            
            try:
                result = process_query(query)
                
                # Document the full response
                print(f"📝 QUERY: {query}")
                print(f"🎯 FULL RESPONSE:")
                print(result)
                print("\n" + "="*80 + "\n")
                
            except Exception as e:
                print(f"❌ Query {i} failed: {e}")
                print("="*80 + "\n")
        
        print("🎉 Comprehensive 7 queries test completed!")
        print("📋 Full responses documented above for manual review")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_7_queries_full() 