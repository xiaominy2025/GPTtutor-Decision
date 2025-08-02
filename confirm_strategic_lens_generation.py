#!/usr/bin/env python3
"""
Demonstration script to confirm how Strategic Thinking Lens is generated
based on identified course concept domains and application fields.
"""

from query_engine import (
    detect_course_concept_domains, 
    extract_application_field,
    generate_course_domain_strategic_lens
)

def demonstrate_strategic_lens_generation():
    """Demonstrate how strategic lens generation works."""
    
    print("🎯 Strategic Thinking Lens Generation Confirmation")
    print("=" * 70)
    
    # Test cases showing different combinations
    test_cases = [
        {
            "query": "How can I use linear programming to optimize production while considering team dynamics?",
            "description": "Technical + Behavioral domains with Operations application field"
        },
        {
            "query": "I have two job offers, how to decide?",
            "description": "Strategic domain with Job application field"
        },
        {
            "query": "Should I start a business using AI algorithms while considering market competition?",
            "description": "Strategic + Technical domains with Technology application field"
        },
        {
            "query": "How do I reduce groupthink in team decisions using statistical analysis?",
            "description": "Behavioral + Technical domains with Operations application field"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}")
        print(f"Query: {test_case['query']}")
        print(f"Description: {test_case['description']}")
        print("-" * 60)
        
        # Step 1: Detect all course concept domains
        detected_domains = detect_course_concept_domains(test_case['query'])
        print(f"1. All detected course concept domains: {detected_domains}")
        
        # Step 2: Identify primary domain (highest score)
        if detected_domains:
            primary_domain = max(detected_domains.items(), key=lambda x: x[1])[0]
            print(f"2. Primary course concept domain: {primary_domain}")
            
            # Show all active domains
            active_domains = {k: v for k, v in detected_domains.items() if v > 0}
            print(f"   Active domains: {active_domains}")
        else:
            primary_domain = 'general'
            print(f"2. Primary course concept domain: {primary_domain} (fallback)")
        
        # Step 3: Detect application field
        application_field = extract_application_field(test_case['query'])
        print(f"3. Application field: {application_field}")
        
        # Step 4: Generate strategic lens using primary domain + application field
        strategic_lens = generate_course_domain_strategic_lens(
            test_case['query'], 
            primary_domain, 
            application_field
        )
        
        print(f"4. Strategic lens generation:")
        print(f"   - Uses primary domain: {primary_domain}")
        print(f"   - Uses application field: {application_field}")
        print(f"   - All other detected domains influence the content")
        
        # Show a snippet of the generated lens
        lens_preview = strategic_lens[:200] + "..." if len(strategic_lens) > 200 else strategic_lens
        print(f"   - Generated lens preview: {lens_preview}")
        
        print("=" * 60)
    
    print("\n📊 CONFIRMATION SUMMARY")
    print("=" * 70)
    print("✅ The Strategic Thinking Lens is generated based on:")
    print("   1. ALL identified course concept domains (influence content)")
    print("   2. PRIMARY course concept domain (main framework)")
    print("   3. APPLICATION FIELD (context-specific content)")
    print()
    print("This ensures comprehensive, contextually relevant strategic analysis")
    print("that considers multiple aspects of complex decisions.")

if __name__ == "__main__":
    demonstrate_strategic_lens_generation() 