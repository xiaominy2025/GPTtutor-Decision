#!/usr/bin/env python3
"""
Test script for tariff uncertainty domain detection
"""

from query_engine import detect_course_concept_domains, extract_application_fields, extract_enhanced_entities

def test_tariff_uncertainty():
    """Test the tariff uncertainty case"""
    query = "Under tariff uncertainty, how do I plan my production?"
    
    print("🧪 Testing Tariff Uncertainty Detection")
    print("=" * 50)
    print(f"Query: '{query}'")
    
    # Test domain detection
    domains = detect_course_concept_domains(query)
    print(f"Detected Domains: {domains}")
    
    # Test field detection
    fields = extract_application_fields(query)
    print(f"Detected Fields: {fields}")
    
    # Test entity extraction
    entities = extract_enhanced_entities(query)
    print(f"Detected Keywords: {entities.get('keywords', [])}")
    
    # Validate results
    print("\n📊 Validation:")
    
    # Check if analytical_tools is detected
    analytical_detected = "analytical_tools" in domains
    print(f"✅ Analytical Tools detected: {analytical_detected}")
    
    # Check if operations is detected (should be detected by GPT)
    operations_detected = "operations" in fields
    print(f"✅ Operations field detected: {operations_detected}")
    
    # Check if strategy is detected (should be detected by GPT)
    strategy_detected = "strategy" in domains
    print(f"✅ Strategy domain detected: {strategy_detected}")
    
    # Overall validation
    expected_domains = ["strategy", "analytical_tools"]
    expected_fields = ["operations"]
    
    domain_validation = any(d in domains for d in expected_domains)
    field_validation = any(f in fields for f in expected_fields)
    
    print(f"\n🎯 Overall Validation:")
    print(f"Domain validation: {domain_validation}")
    print(f"Field validation: {field_validation}")
    
    if domain_validation and field_validation:
        print("✅ PASS: Tariff uncertainty detection working correctly!")
    else:
        print("❌ FAIL: Tariff uncertainty detection needs improvement")
    
    return domain_validation and field_validation

if __name__ == "__main__":
    test_tariff_uncertainty() 