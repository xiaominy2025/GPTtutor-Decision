#!/usr/bin/env python3
"""
Test to verify the entity extraction fix.
"""

def test_entity_extraction():
    """Test the fixed entity extraction function."""
    
    print("🧪 Testing entity extraction fix...")
    
    try:
        from query_engine import extract_enhanced_entities
        
        test_query = "How can I optimize production with 50 employees while considering budget constraints?"
        print(f"Test query: {test_query}")
        
        entities = extract_enhanced_entities(test_query)
        print(f"✅ Entity extraction successful!")
        print(f"Extracted entities: {entities}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_process_query():
    """Test the full process_query function."""
    
    print("\n🧪 Testing full query processing...")
    
    try:
        from query_engine import process_query
        
        test_query = "How can I optimize production with 50 employees?"
        print(f"Test query: {test_query}")
        
        result = process_query(test_query)
        print(f"✅ Query processing successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 ENTITY EXTRACTION FIX TEST")
    print("=" * 50)
    
    # Test entity extraction
    if test_entity_extraction():
        print("✅ Entity extraction fix working")
    else:
        print("❌ Entity extraction still failing")
        exit(1)
    
    # Test full query processing
    if test_process_query():
        print("✅ Full query processing working")
    else:
        print("❌ Full query processing failing")
        exit(1)
    
    print("\n🎯 All tests passed! The fix is working correctly.") 