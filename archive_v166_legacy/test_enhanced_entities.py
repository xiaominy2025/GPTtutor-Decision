#!/usr/bin/env python3
"""
Test script to demonstrate enhanced entity extraction and its impact on answer generation.
"""

from query_engine import (
    extract_enhanced_entities, 
    enhance_strategic_lens_with_entities,
    process_query,
    detect_course_concept_domains,
    extract_application_field
)

def test_enhanced_entity_extraction():
    """Test enhanced entity extraction with various query types."""
    
    print("🧪 Enhanced Entity Extraction Test")
    print("=" * 60)
    
    # Test queries with different entity types
    test_queries = [
        {
            "query": "How can I optimize production with 50 employees while considering budget constraints and team dynamics?",
            "description": "Quantitative + Stakeholders + Constraints"
        },
        {
            "query": "Should I invest in AI technology for my manufacturing business with 3 locations next year?",
            "description": "Technology + Industry + Quantitative + Time"
        },
        {
            "query": "What are the risks and opportunities of expanding to 5 new markets with 100 employees over the next 2 years?",
            "description": "Risks + Quantitative + Time + Stakeholders"
        },
        {
            "query": "How do I reduce groupthink in my team of 25 people while maintaining efficiency and quality standards?",
            "description": "Behavioral + Quantitative + Constraints + Stakeholders"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        # Extract entities
        entities = extract_enhanced_entities(test_case['query'])
        
        print("Extracted entities:")
        for category, values in entities.items():
            if values:
                print(f"  {category}: {values}")
        
        # Show domain and application field detection
        domains = detect_course_concept_domains(test_case['query'])
        app_field = extract_application_field(test_case['query'])
        
        print(f"\nDomain detection: {domains}")
        print(f"Application field: {app_field}")
        
        # Test strategic lens enhancement
        base_lens = "This requires strategic analysis and decision-making."
        enhanced_lens = enhance_strategic_lens_with_entities(base_lens, entities)
        
        print(f"\nBase strategic lens: {base_lens}")
        print(f"Enhanced strategic lens: {enhanced_lens}")
        
        print("=" * 50)
    
    print("\n📊 SUMMARY")
    print("=" * 60)
    print("Enhanced entity extraction adds the following nuances:")
    print("✅ Time periods (short-term, next year, etc.)")
    print("✅ Quantitative terms (50 employees, 3 locations, etc.)")
    print("✅ Stakeholders (team, employees, customers, etc.)")
    print("✅ Constraints (budget, time, resources, etc.)")
    print("✅ Risks and uncertainties")
    print("✅ Technologies (AI, automation, etc.)")
    print("✅ Industries (manufacturing, healthcare, etc.)")
    print("✅ And more...")

def test_entity_impact_on_answers():
    """Test how entity extraction impacts full answer generation."""
    
    print("\n🎯 Entity Impact on Answer Generation Test")
    print("=" * 60)
    
    test_query = "How can I optimize production with 50 employees while considering budget constraints and team dynamics?"
    
    print(f"Test Query: {test_query}")
    print("-" * 50)
    
    # Extract entities
    entities = extract_enhanced_entities(test_query)
    print("Extracted entities:")
    for category, values in entities.items():
        if values:
            print(f"  {category}: {values}")
    
    # Process query
    try:
        response = process_query(test_query)
        
        # Check if strategic lens contains entity-specific content
        if "Strategic Thinking Lens" in response:
            strategic_lens = response.split("Strategic Thinking Lens")[1].split("##")[0].strip()
            
            # Check for entity-specific terms in the strategic lens
            entity_terms_found = []
            for category, values in entities.items():
                for value in values:
                    if value.lower() in strategic_lens.lower():
                        entity_terms_found.append(f"{category}: {value}")
            
            if entity_terms_found:
                print(f"\n✅ Strategic lens contains entity-specific content:")
                for term in entity_terms_found:
                    print(f"  - {term}")
            else:
                print("\n⚠️ Strategic lens may not contain entity-specific content")
            
            print(f"\nStrategic lens length: {len(strategic_lens)} characters")
            print(f"Full response length: {len(response)} characters")
            
        else:
            print("❌ Strategic Thinking Lens not found in response")
            
    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")

if __name__ == "__main__":
    # Test enhanced entity extraction
    test_enhanced_entity_extraction()
    
    # Test entity impact on answers
    test_entity_impact_on_answers()
    
    print("\n🎯 Enhanced Entity Extraction Test Complete!") 