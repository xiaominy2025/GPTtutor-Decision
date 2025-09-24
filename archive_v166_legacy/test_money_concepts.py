#!/usr/bin/env python3
"""
Test script to verify mental accounting selection for money-related queries
"""

import sys
import os
from query_engine import process_query, clear_concept_cache

def test_money_concept_selection():
    """Test the concept selection for money-related queries"""
    
    # Clear cache to ensure fresh concept selection
    clear_concept_cache()
    
    # Test query that should prioritize mental accounting
    test_query = "How should I budget my monthly salary between different expenses?"
    
    print("🧪 Testing Money-Related Concept Selection")
    print("=" * 50)
    print(f"Query: {test_query}")
    print("\nGenerating response...")
    
    try:
        response = process_query(test_query)
        
        print("\n✅ Response generated successfully!")
        print("\n📋 Response Analysis:")
        
        # Check for mental accounting (should be present)
        has_mental_accounting = "mental accounting" in response.lower()
        print(f"✅ Mental Accounting present: {has_mental_accounting}")
        
        # Check for framing bias (should NOT be prioritized)
        has_framing_bias = "framing bias" in response.lower()
        print(f"❌ Framing Bias present: {has_framing_bias}")
        
        # Check for other financial concepts
        has_budget = "budget" in response.lower()
        print(f"✅ Budget mentioned: {has_budget}")
        
        print("\n📄 Full Response:")
        print("-" * 50)
        print(response)
        
        # Summary
        print("\n📊 Summary:")
        if has_mental_accounting and not has_framing_bias:
            print("✅ FIX SUCCESSFUL: Mental accounting prioritized for money queries, framing bias not selected")
        elif not has_mental_accounting and has_framing_bias:
            print("❌ FIX FAILED: Mental accounting missing, framing bias incorrectly selected")
        else:
            print("⚠️ PARTIAL SUCCESS: Some improvements but not complete")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_money_concept_selection() 