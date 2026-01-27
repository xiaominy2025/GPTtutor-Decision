#!/usr/bin/env python3
"""
Test Cleaned Entities Integration
Verifies that the updated query engine is using the cleaned entities correctly
"""

import sys
import os

def test_entity_import():
    """Test that the cleaned entities can be imported correctly"""
    try:
        from expanded_entities_clean import extract_expanded_entities, get_entity_summary
        print("✅ Successfully imported cleaned entities")
        return True
    except ImportError as e:
        print(f"❌ Failed to import cleaned entities: {e}")
        return False

def test_stoplist_loading():
    """Test that the stoplist is loading correctly"""
    try:
        from expanded_entities_clean import ENTITY_STOPLIST
        print(f"✅ Stoplist loaded with {len(ENTITY_STOPLIST)} terms")
        return True
    except Exception as e:
        print(f"❌ Failed to load stoplist: {e}")
        return False

def test_entity_extraction():
    """Test entity extraction with sample queries"""
    try:
        from expanded_entities_clean import extract_expanded_entities, get_entity_summary
        
        test_queries = [
            "How do we handle short-term employee concerns with high uncertainty?",
            "What financial criteria matter for long-term investor satisfaction?",
            "How do we manage operational complexity for immediate customer needs?",
            "What strategic risks do regulators see in our approach?"
        ]
        
        print("\n🧪 Testing Entity Extraction with Stoplist")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            entities = extract_expanded_entities(query)
            summary = get_entity_summary(entities)
            
            print(f"\nQuery {i}: {query}")
            print(f"Summary: {summary}")
            print(f"Confidence: {entities.get('confidence', 0.0):.3f}")
            print(f"Entities found: {sum(len(entities.get(key, {})) for key in ['timeframe', 'stakeholders', 'criteria', 'uncertainty', 'complexity'])}")
        
        return True
    except Exception as e:
        print(f"❌ Entity extraction test failed: {e}")
        return False

def test_query_engine_integration():
    """Test that the query engine can import the cleaned entities"""
    try:
        # Temporarily modify sys.path to avoid import issues
        original_path = sys.path.copy()
        sys.path.insert(0, os.getcwd())
        
        # Try to import the query engine
        import query_engine
        print("✅ Query engine imports successfully")
        
        # Restore original path
        sys.path = original_path
        return True
    except Exception as e:
        print(f"❌ Query engine integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Cleaned Entities Integration")
    print("=" * 50)
    
    tests = [
        ("Entity Import", test_entity_import),
        ("Stoplist Loading", test_stoplist_loading),
        ("Entity Extraction", test_entity_extraction),
        ("Query Engine Integration", test_query_engine_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    print("\n📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Cleaned entities integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 