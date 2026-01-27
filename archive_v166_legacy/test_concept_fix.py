#!/usr/bin/env python3
"""
Test script to verify the concept selection fix for critique-related queries
"""

import sys
import os
from query_engine import process_query, clear_concept_cache

def test_concept_selection_fix():
    """Test the concept selection fix for critique-related queries"""
    
    # Clear cache to ensure fresh concept selection
    clear_concept_cache()
    
    # Test query that should prioritize framing bias over mental accounting
    test_query = "How shall I deal with unfair critiques from my manager?"
    
    print("🧪 Testing Concept Selection Fix")
    print("=" * 50)
    print(f"Query: {test_query}")
    print("\nGenerating response...")
    
    try:
        response = process_query(test_query)
        
        print("\n✅ Response generated successfully!")
        print("\n📋 Response Analysis:")
        
        # Check for mental accounting (should NOT be present)
        has_mental_accounting = "mental accounting" in response.lower()
        print(f"❌ Mental Accounting present: {has_mental_accounting}")
        
        # Check for framing bias (should be present)
        has_framing_bias = "framing bias" in response.lower()
        print(f"✅ Framing Bias present: {has_framing_bias}")
        
        # Check for confirmation bias (should be present)
        has_confirmation_bias = "confirmation bias" in response.lower()
        print(f"✅ Confirmation Bias present: {has_confirmation_bias}")
        
        # Check for anchoring bias (should be present)
        has_anchoring_bias = "anchoring bias" in response.lower()
        print(f"✅ Anchoring Bias present: {has_anchoring_bias}")
        
        print("\n📄 Full Response:")
        print("-" * 50)
        print(response)
        
        # Summary
        print("\n📊 Summary:")
        if not has_mental_accounting and has_framing_bias:
            print("✅ FIX SUCCESSFUL: Mental accounting filtered out, framing bias prioritized")
        elif has_mental_accounting and not has_framing_bias:
            print("❌ FIX FAILED: Mental accounting still present, framing bias missing")
        else:
            print("⚠️ PARTIAL SUCCESS: Some improvements but not complete")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_concept_selection_fix() 