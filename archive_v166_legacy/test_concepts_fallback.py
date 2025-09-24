#!/usr/bin/env python3
"""
Test script to verify domain-appropriate fallback concepts functionality
"""

import sys
import os
from query_engine import generate_fallback_concepts, detect_course_concept_domains

def test_domain_fallback_concepts():
    """Test the domain-appropriate fallback concepts functionality"""
    
    print("🧪 Testing Domain-Appropriate Fallback Concepts")
    print("=" * 60)
    
    # Test queries for different domains
    test_queries = [
        ("How shall I deal with unfair critiques from my manager?", "behavioral"),
        ("How should I budget my monthly salary between different expenses?", "behavioral"),
        ("What's a good way to model production uncertainty?", "technical"),
        ("Should we expand to international markets?", "strategic"),
        ("How do I negotiate a better salary package?", "negotiation"),
        ("What tools can help me make better decisions?", "general")
    ]
    
    for query, expected_domain in test_queries:
        print(f"\n📝 Query: {query}")
        print(f"🎯 Expected Domain: {expected_domain}")
        
        # Test domain detection
        domains = detect_course_concept_domains(query)
        detected_domain = max(domains, key=domains.get) if domains else 'general'
        print(f"🔍 Detected Domain: {detected_domain}")
        
        # Test fallback concepts
        fallback_concepts = generate_fallback_concepts(query)
        print(f"📋 Fallback Concepts ({len(fallback_concepts)}):")
        for i, concept in enumerate(fallback_concepts, 1):
            print(f"  {i}. {concept}")
        
        # Validate results
        domain_match = detected_domain == expected_domain
        concept_count = len(fallback_concepts) == 2
        print(f"✅ Domain Match: {domain_match}")
        print(f"✅ Concept Count (2): {concept_count}")
        
        if domain_match and concept_count:
            print("✅ TEST PASSED")
        else:
            print("❌ TEST FAILED")
        
        print("-" * 40)

if __name__ == "__main__":
    test_domain_fallback_concepts() 