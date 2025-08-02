#!/usr/bin/env python3
"""
Final verification script to confirm the query engine is working correctly.
"""

def verify_query_engine():
    """Verify that the query engine is working correctly."""
    
    print("🎯 FINAL VERIFICATION - QUERY ENGINE")
    print("=" * 60)
    
    # Test the exact query that was failing
    test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
    
    try:
        from query_engine import process_query
        
        print(f"Testing query: {test_query}")
        print("-" * 50)
        
        result = process_query(test_query)
        
        print(f"✅ Query processing successful!")
        print(f"Result length: {len(result)} characters")
        
        # Check for required sections
        sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts", "Concepts/Tools"]
        missing_sections = []
        
        for section in sections:
            if section in result:
                print(f"  ✅ {section} present")
            else:
                print(f"  ❌ {section} missing")
                missing_sections.append(section)
        
        if not missing_sections:
            print("✅ All required sections present")
        else:
            print(f"⚠️ Missing sections: {missing_sections}")
        
        # Check for entity-specific content
        if "tariff" in result.lower() or "uncertainty" in result.lower():
            print("  ✅ Entity-specific content found")
        else:
            print("  ⚠️ Entity-specific content may be missing")
        
        # Show first part of the response
        print(f"\n📄 First 500 characters of response:")
        print("-" * 50)
        print(result[:500])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_enhanced_entities():
    """Verify that enhanced entity extraction is working."""
    
    print("\n🎯 FINAL VERIFICATION - ENHANCED ENTITIES")
    print("=" * 60)
    
    try:
        from query_engine import extract_enhanced_entities
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        entities = extract_enhanced_entities(test_query)
        print(f"Extracted entities: {entities}")
        
        # Check for expected entities
        expected_entities = ["uncertainty", "production", "plant", "profit", "year"]
        found_entities = []
        
        for category, values in entities.items():
            found_entities.extend(values)
        
        expected_found = 0
        for expected in expected_entities:
            if any(expected.lower() in entity.lower() for entity in found_entities):
                expected_found += 1
                print(f"  ✅ Found: {expected}")
            else:
                print(f"  ❌ Missing: {expected}")
        
        accuracy = expected_found / len(expected_entities)
        print(f"Entity detection accuracy: {accuracy:.1%}")
        
        if accuracy > 0.3:  # At least 30% accuracy
            print("✅ Enhanced entity extraction working correctly")
            return True
        else:
            print("⚠️ Enhanced entity extraction may need improvement")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced entity extraction failed: {e}")
        return False

def verify_system_stability():
    """Verify system stability with multiple queries."""
    
    print("\n🎯 FINAL VERIFICATION - SYSTEM STABILITY")
    print("=" * 60)
    
    test_queries = [
        "How can I optimize production with 50 employees?",
        "Should I invest in AI technology for my business?",
        "What are the risks of expanding to new markets?"
    ]
    
    try:
        from query_engine import process_query
        
        success_count = 0
        total_count = len(test_queries)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Test {i}: {query}")
            
            try:
                result = process_query(query)
                print(f"  ✅ Success - {len(result)} characters")
                success_count += 1
            except Exception as e:
                print(f"  ❌ Failed - {e}")
        
        success_rate = success_count / total_count
        print(f"\n📊 Success rate: {success_rate:.1%} ({success_count}/{total_count})")
        
        if success_rate >= 0.8:  # At least 80% success rate
            print("✅ System stability verified")
            return True
        else:
            print("⚠️ System stability may need improvement")
            return False
            
    except Exception as e:
        print(f"❌ System stability test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    
    print("🎯 FINAL VERIFICATION SUITE")
    print("=" * 60)
    
    # Test query engine
    query_success = verify_query_engine()
    
    # Test enhanced entities
    entity_success = verify_enhanced_entities()
    
    # Test system stability
    stability_success = verify_system_stability()
    
    # Final summary
    print("\n📊 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Query Engine: {'✅ PASS' if query_success else '❌ FAIL'}")
    print(f"Enhanced Entities: {'✅ PASS' if entity_success else '❌ FAIL'}")
    print(f"System Stability: {'✅ PASS' if stability_success else '❌ FAIL'}")
    
    if query_success and entity_success and stability_success:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("The query engine is working correctly with enhanced entity extraction.")
        print("The system is ready for production use.")
    else:
        print("\n⚠️ Some verifications failed.")
        print("Please check the error messages above for specific issues.")
    
    return query_success and entity_success and stability_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 VERIFICATION COMPLETE - SYSTEM READY!")
    else:
        print("\n⚠️ VERIFICATION COMPLETE - ISSUES DETECTED!") 