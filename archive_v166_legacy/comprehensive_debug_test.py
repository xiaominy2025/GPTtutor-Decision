#!/usr/bin/env python3
"""
Comprehensive debug test to identify all issues in the query engine.
"""

import traceback
import sys

def test_entity_extraction_step_by_step():
    """Test entity extraction step by step to identify the exact issue."""
    
    print("🔍 Testing entity extraction step by step...")
    
    try:
        # Test 1: Import the function
        from query_engine import extract_enhanced_entities
        print("✅ Import successful")
        
        # Test 2: Create a simple query
        test_query = "How can I optimize production with 50 employees?"
        print(f"✅ Test query created: {test_query}")
        
        # Test 3: Call the function
        entities = extract_enhanced_entities(test_query)
        print("✅ Entity extraction successful")
        print(f"Entities: {entities}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_process_query_step_by_step():
    """Test process_query step by step to identify the exact issue."""
    
    print("\n🔍 Testing process_query step by step...")
    
    try:
        # Test 1: Import the function
        from query_engine import process_query
        print("✅ Import successful")
        
        # Test 2: Create a simple query
        test_query = "How can I optimize production?"
        print(f"✅ Test query created: {test_query}")
        
        # Test 3: Call the function
        result = process_query(test_query)
        print("✅ Process query successful")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Process query failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_basic_functions():
    """Test basic functions to ensure they work."""
    
    print("\n🔍 Testing basic functions...")
    
    try:
        from query_engine import detect_course_concept_domains, extract_application_field
        
        test_query = "How can I optimize production?"
        
        # Test domain detection
        domains = detect_course_concept_domains(test_query)
        print(f"✅ Domain detection: {domains}")
        
        # Test application field detection
        app_field = extract_application_field(test_query)
        print(f"✅ Application field: {app_field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functions failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive debug tests."""
    
    print("🔍 COMPREHENSIVE DEBUG TEST SUITE")
    print("=" * 60)
    
    # Test basic functions first
    if not test_basic_functions():
        print("\n❌ Basic functions failed. Stopping here.")
        return
    
    # Test entity extraction
    if not test_entity_extraction_step_by_step():
        print("\n❌ Entity extraction failed. This is likely the root cause.")
        return
    
    # Test full process_query
    if not test_process_query_step_by_step():
        print("\n❌ Process query failed. There may be additional issues.")
        return
    
    print("\n✅ All tests passed! The system should be working correctly.")

if __name__ == "__main__":
    main() 