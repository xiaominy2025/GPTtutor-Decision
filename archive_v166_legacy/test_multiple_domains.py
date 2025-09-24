#!/usr/bin/env python3
"""
Test script to demonstrate multiple course concept domain detection.
"""

from query_engine import detect_course_concept_domains, extract_application_field

def test_multiple_domain_detection():
    """Test queries that should trigger multiple course concept domains."""
    
    print("🧪 Multiple Course Concept Domain Detection Test")
    print("=" * 60)
    
    # Test cases that should trigger multiple domains
    test_cases = [
        {
            "query": "How can I use linear programming to optimize production while considering team dynamics?",
            "description": "Technical + Behavioral (optimization + team dynamics)",
            "expected_domains": ["technical", "behavioral"]
        },
        {
            "query": "What's the best strategy to negotiate with suppliers while optimizing our supply chain?",
            "description": "Strategic + Negotiation + Technical (strategy + negotiation + optimization)",
            "expected_domains": ["strategic", "negotiation", "technical"]
        },
        {
            "query": "How do I choose between job offers using data analysis and considering my career goals?",
            "description": "Strategic + Technical + Behavioral (career + analysis + decision-making)",
            "expected_domains": ["strategic", "technical", "behavioral"]
        },
        {
            "query": "Should I start a business using AI algorithms while considering market competition?",
            "description": "Strategic + Technical (business strategy + AI algorithms)",
            "expected_domains": ["strategic", "technical"]
        },
        {
            "query": "How can I reduce groupthink in team decisions using statistical analysis?",
            "description": "Behavioral + Technical (team dynamics + statistical analysis)",
            "expected_domains": ["behavioral", "technical"]
        },
        {
            "query": "What's the best way to negotiate a contract while optimizing our operations?",
            "description": "Negotiation + Technical (contract negotiation + operations optimization)",
            "expected_domains": ["negotiation", "technical"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}")
        print(f"Query: {test_case['query']}")
        print(f"Description: {test_case['description']}")
        print("-" * 50)
        
        # Detect domains
        detected_domains = detect_course_concept_domains(test_case['query'])
        application_field = extract_application_field(test_case['query'])
        
        print(f"Detected domains: {detected_domains}")
        print(f"Application field: {application_field}")
        
        # Find primary domain (highest score)
        if detected_domains:
            primary_domain = max(detected_domains.items(), key=lambda x: x[1])[0]
            print(f"Primary domain: {primary_domain}")
            
            # Show all domains with scores > 0
            active_domains = {k: v for k, v in detected_domains.items() if v > 0}
            print(f"Active domains: {active_domains}")
            
            # Check if expected domains are detected
            expected_domains = test_case['expected_domains']
            detected_expected = [domain for domain in expected_domains if domain in active_domains]
            print(f"Expected domains: {expected_domains}")
            print(f"Detected expected domains: {detected_expected}")
            
            if len(detected_expected) >= 2:
                print("✅ Multiple domains detected successfully!")
            else:
                print("⚠️ Expected multiple domains but detected fewer")
        else:
            print("❌ No domains detected")
        
        print("=" * 50)
    
    print("\n📊 SUMMARY")
    print("=" * 60)
    print("The system can detect multiple course concept domains for a single query.")
    print("This allows for more nuanced and comprehensive strategic lens generation.")
    print("The primary domain (highest score) is used for the main strategic lens,")
    print("while secondary domains can influence the content and approach.")

if __name__ == "__main__":
    test_multiple_domain_detection() 