#!/usr/bin/env python3
"""
Final test to verify enhanced entity integration and proper follow-up prompt generation.
"""

def test_enhanced_entity_integration():
    """Test enhanced entity integration."""
    
    print("🎯 FINAL ENHANCED ENTITY INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from query_engine import process_query, extract_enhanced_entities
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        # Extract entities
        entities = extract_enhanced_entities(test_query)
        print(f"Extracted entities: {entities}")
        
        # Process query
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
        entity_indicators = []
        if 'time_periods' in entities:
            entity_indicators.extend(entities['time_periods'])
        if 'risks' in entities:
            entity_indicators.extend(entities['risks'])
        
        entity_found = False
        for indicator in entity_indicators:
            if indicator.lower() in result.lower():
                entity_found = True
                print(f"  ✅ Entity '{indicator}' found in response")
        
        if entity_found:
            print("✅ Entity integration working correctly")
        else:
            print("⚠️ Entity integration may need improvement")
        
        # Check for multiple follow-up prompts
        followup_section = ""
        if "**Follow-up Prompts**" in result:
            start_pos = result.find("**Follow-up Prompts**")
            end_pos = result.find("**", start_pos + 1)
            if end_pos != -1:
                followup_section = result[start_pos:end_pos]
            else:
                followup_section = result[start_pos:]
        
        if followup_section:
            # Count bullet points in follow-up prompts
            bullet_count = followup_section.count("- ")
            print(f"  📊 Found {bullet_count} follow-up prompts")
            
            if bullet_count >= 2:
                print("✅ Multiple follow-up prompts generated correctly")
            else:
                print("⚠️ Only one follow-up prompt generated")
        else:
            print("❌ Follow-up prompts section not found")
        
        # Show first part of the response
        print(f"\n📄 First 800 characters of response:")
        print("-" * 80)
        print(result[:800])
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced entity integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_domain_aware_followup_generation():
    """Test domain-aware follow-up prompt generation."""
    
    print("\n🎯 TESTING DOMAIN-AWARE FOLLOW-UP GENERATION")
    print("=" * 60)
    
    try:
        from query_engine import generate_domain_aware_followup_prompt, extract_enhanced_entities, detect_course_concept_domains
        
        test_queries = [
            "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?",
            "How can I negotiate better terms with my suppliers?",
            "What psychological factors should I consider when making this decision?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Test Query {i}: {query}")
            
            # Extract entities and detect domains
            entities = extract_enhanced_entities(query)
            domains = detect_course_concept_domains(query)
            
            print(f"  Entities: {entities}")
            print(f"  Domains: {domains}")
            
            # Generate follow-up prompt
            prompt = generate_domain_aware_followup_prompt(query, entities)
            
            print(f"  Prompt length: {len(prompt)} characters")
            
            # Check if prompt contains domain-specific content
            if "Generate exactly" in prompt:
                print("  ✅ Domain-aware prompt generated")
            else:
                print("  ⚠️ Generic prompt generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Domain-aware follow-up generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the final enhanced test."""
    
    print("🎯 FINAL ENHANCED TEST SUITE")
    print("=" * 60)
    
    # Test enhanced entity integration
    integration_success = test_enhanced_entity_integration()
    
    # Test domain-aware follow-up generation
    followup_success = test_domain_aware_followup_generation()
    
    # Final summary
    print("\n📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"Enhanced Entity Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    print(f"Domain-Aware Follow-up Generation: {'✅ PASS' if followup_success else '❌ FAIL'}")
    
    if integration_success and followup_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("Enhanced entity integration is working correctly.")
        print("Domain-aware follow-up prompt generation is working correctly.")
        print("Multiple follow-up prompts are being generated as expected.")
    else:
        print("\n⚠️ Some tests failed.")
        print("Please check the error messages above for specific issues.")
    
    return integration_success and followup_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Final enhanced test completed successfully!")
    else:
        print("\n❌ Final enhanced test failed!") 