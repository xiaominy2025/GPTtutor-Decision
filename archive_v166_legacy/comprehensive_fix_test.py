#!/usr/bin/env python3
"""
Comprehensive test to identify and fix remaining issues.
"""

def test_basic_imports():
    """Test basic imports."""
    
    print("🔍 Testing basic imports...")
    
    try:
        import query_engine
        print("✅ query_engine imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_entity_extraction():
    """Test entity extraction."""
    
    print("\n🔍 Testing entity extraction...")
    
    try:
        from query_engine import extract_enhanced_entities
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        entities = extract_enhanced_entities(test_query)
        
        print(f"✅ Entity extraction successful: {entities}")
        return True
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return False

def test_domain_detection():
    """Test domain detection."""
    
    print("\n🔍 Testing domain detection...")
    
    try:
        from query_engine import detect_course_concept_domains
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        domains = detect_course_concept_domains(test_query)
        
        print(f"✅ Domain detection successful: {domains}")
        return True
    except Exception as e:
        print(f"❌ Domain detection failed: {e}")
        return False

def test_followup_prompt_generation():
    """Test follow-up prompt generation."""
    
    print("\n🔍 Testing follow-up prompt generation...")
    
    try:
        from query_engine import generate_domain_aware_followup_prompt, extract_enhanced_entities
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        entities = extract_enhanced_entities(test_query)
        
        prompt = generate_domain_aware_followup_prompt(test_query, entities)
        
        print(f"✅ Follow-up prompt generation successful")
        print(f"Prompt length: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"❌ Follow-up prompt generation failed: {e}")
        return False

def test_api_call():
    """Test API call."""
    
    print("\n🔍 Testing API call...")
    
    try:
        from query_engine import client, SYSTEM_PROMPT_ANALYTICS
        
        test_query = "How can I optimize production?"
        user_message = f"Question: {test_query}\n\nPlease answer using the required structure."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ANALYTICS},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        print(f"✅ API call successful: {len(response.choices[0].message.content)} characters")
        return True
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

def test_process_query_step_by_step():
    """Test process_query step by step."""
    
    print("\n🔍 Testing process_query step by step...")
    
    try:
        from query_engine import process_query
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        # Test the full process
        result = process_query(test_query)
        
        print(f"✅ Process query successful: {len(result)} characters")
        
        # Check if it's an error message
        if "I encountered an error" in result:
            print("⚠️ Process query returned error message")
            return False
        else:
            print("✅ Process query returned valid response")
            return True
            
    except Exception as e:
        print(f"❌ Process query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simplified_test():
    """Create a simplified test to isolate the issue."""
    
    print("\n🔍 Creating simplified test...")
    
    try:
        # Test the exact query that was working before
        test_query = "How can I optimize production?"
        
        from query_engine import process_query
        result = process_query(test_query)
        
        print(f"✅ Simplified test successful: {len(result)} characters")
        return True
    except Exception as e:
        print(f"❌ Simplified test failed: {e}")
        return False

def main():
    """Run comprehensive tests."""
    
    print("🎯 COMPREHENSIVE FIX TEST")
    print("=" * 60)
    
    # Test basic imports
    import_success = test_basic_imports()
    
    # Test entity extraction
    entity_success = test_entity_extraction()
    
    # Test domain detection
    domain_success = test_domain_detection()
    
    # Test follow-up prompt generation
    prompt_success = test_followup_prompt_generation()
    
    # Test API call
    api_success = test_api_call()
    
    # Test simplified process query
    simple_success = create_simplified_test()
    
    # Test full process query
    full_success = test_process_query_step_by_step()
    
    # Summary
    print("\n📊 TEST RESULTS")
    print("=" * 50)
    print(f"Basic Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"Entity Extraction: {'✅ PASS' if entity_success else '❌ FAIL'}")
    print(f"Domain Detection: {'✅ PASS' if domain_success else '❌ FAIL'}")
    print(f"Follow-up Prompt Generation: {'✅ PASS' if prompt_success else '❌ FAIL'}")
    print(f"API Call: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"Simplified Process Query: {'✅ PASS' if simple_success else '❌ FAIL'}")
    print(f"Full Process Query: {'✅ PASS' if full_success else '❌ FAIL'}")
    
    if all([import_success, entity_success, domain_success, prompt_success, api_success, simple_success, full_success]):
        print("\n🎉 ALL TESTS PASSED!")
        print("The query engine is working correctly with enhanced entity integration.")
    else:
        print("\n⚠️ Some tests failed.")
        print("Please check the error messages above for specific issues.")
    
    return all([import_success, entity_success, domain_success, prompt_success, api_success, simple_success, full_success])

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Comprehensive test completed successfully!")
    else:
        print("\n❌ Comprehensive test failed!") 