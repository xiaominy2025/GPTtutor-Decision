#!/usr/bin/env python3
"""
Minimal Framework Selection Test
===============================

Direct test of the framework selection logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_framework_selection():
    """Test the framework selection logic directly"""
    print("🧪 Testing Framework Selection Logic")
    print("=" * 50)
    
    try:
        # Import the function
        from query_engine import generate_course_domain_strategic_lens
        print("✅ Import successful")
        
        # Test query with linear optimization
        query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
        print(f"📋 Query: {query}")
        
        # Test with technical domain
        result = generate_course_domain_strategic_lens(query, "technical")
        print(f"📊 Result length: {len(result)}")
        
        # Check for framework mentions
        linear_count = result.lower().count('linear')
        monte_carlo_count = result.lower().count('monte carlo')
        
        print(f"📊 Framework mentions:")
        print(f"  Linear optimization: {linear_count}")
        print(f"  Monte Carlo: {monte_carlo_count}")
        
        # Show first 300 characters of result
        print(f"\n📋 First 300 characters of result:")
        print(result[:300])
        
        if linear_count > monte_carlo_count:
            print("✅ Linear optimization properly emphasized")
            return True
        else:
            print("❌ Linear optimization not properly emphasized")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_framework_selection()
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 