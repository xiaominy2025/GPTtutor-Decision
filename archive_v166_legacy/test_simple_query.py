#!/usr/bin/env python3
"""
Simple test to check if the query engine works without enhanced entity extraction.
"""

def test_basic_query():
    """Test basic query processing without entity extraction."""
    
    print("🧪 Testing basic query processing...")
    
    try:
        # Import the basic functions without entity extraction
        from query_engine import detect_course_concept_domains, extract_application_field
        
        # Test query
        test_query = "How can I optimize production?"
        print(f"Test query: {test_query}")
        
        # Test domain detection
        domains = detect_course_concept_domains(test_query)
        print(f"Detected domains: {domains}")
        
        # Test application field detection
        app_field = extract_application_field(test_query)
        print(f"Application field: {app_field}")
        
        print("✅ Basic functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Basic functions failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_without_entities():
    """Test query processing without entity extraction."""
    
    print("\n🧪 Testing query processing without entities...")
    
    try:
        # Import process_query but temporarily disable entity extraction
        import query_engine
        
        # Test with a simple query
        test_query = "How can I optimize production?"
        print(f"Test query: {test_query}")
        
        # Call process_query directly
        result = query_engine.process_query(test_query)
        print(f"✅ Query processed successfully")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 SIMPLE QUERY TEST")
    print("=" * 50)
    
    # Test basic functions
    if test_basic_query():
        print("✅ Basic functions working")
    else:
        print("❌ Basic functions failed")
        exit(1)
    
    # Test query processing
    if test_without_entities():
        print("✅ Query processing working")
    else:
        print("❌ Query processing failed")
        exit(1)
    
    print("\n🎯 All tests passed!") 