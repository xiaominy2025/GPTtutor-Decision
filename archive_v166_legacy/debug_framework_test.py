#!/usr/bin/env python3
"""
Debug Framework Selection Test
=============================

Simple test to debug the framework selection logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_framework_selection():
    """Test the framework selection logic"""
    print("🧪 Testing Framework Selection")
    print("=" * 40)
    
    try:
        from query_engine import detect_course_concept_domains, generate_course_domain_strategic_lens
        print("✅ Imports successful")
        
        # Test query
        query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
        print(f"📋 Query: {query}")
        
        # Get domain
        domains = detect_course_concept_domains(query)
        course_domain = domains.get('primary_domain', 'general')
        print(f"📊 Detected domain: {course_domain}")
        
        # Generate lens
        result = generate_course_domain_strategic_lens(query, course_domain)
        print(f"📊 Result length: {len(result)}")
        
        # Check mentions
        linear_count = result.lower().count('linear')
        monte_carlo_count = result.lower().count('monte carlo')
        
        print(f"📊 Mentions:")
        print(f"  Linear: {linear_count}")
        print(f"  Monte Carlo: {monte_carlo_count}")
        
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