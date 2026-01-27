#!/usr/bin/env python3
"""
Test script to verify semantic application field detection
"""

import sys
import os
from query_engine import process_query, load_data_lazily, extract_application_field_semantic, extract_application_field

def test_semantic_application_field():
    """Test semantic application field detection"""
    
    print("🧪 Testing Semantic Application Field Detection")
    print("=" * 60)
    
    # Test queries for different application fields
    test_queries = [
        ("How should I manage my team during a crisis?", "leadership"),
        ("Should I start my own business?", "startup"),
        ("How do I market my new product?", "marketing"),
        ("How can I optimize my production process?", "operations"),
        ("Should I invest in stocks or bonds?", "finance"),
        ("How do I negotiate a better contract?", "negotiation")
    ]
    
    try:
        # Load data lazily to get the model
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        for query, expected_field in test_queries:
            print(f"\n📝 Query: {query}")
            print(f"🎯 Expected Field: {expected_field}")
            
            # Test semantic detection
            try:
                semantic_field = extract_application_field_semantic(query, model)
                print(f"🔍 Semantic Field: {semantic_field}")
            except Exception as e:
                print(f"❌ Semantic detection failed: {e}")
                semantic_field = "error"
            
            # Test keyword-based detection for comparison
            keyword_field = extract_application_field(query)
            print(f"🔍 Keyword Field: {keyword_field}")
            
            # Validate results
            semantic_match = semantic_field == expected_field
            keyword_match = keyword_field == expected_field
            
            print(f"✅ Semantic Match: {semantic_match}")
            print(f"✅ Keyword Match: {keyword_match}")
            
            if semantic_match:
                print("✅ SEMANTIC DETECTION PASSED")
            elif keyword_match:
                print("⚠️ SEMANTIC FAILED, KEYWORD WORKED")
            else:
                print("❌ BOTH FAILED")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_semantic_application_field() 