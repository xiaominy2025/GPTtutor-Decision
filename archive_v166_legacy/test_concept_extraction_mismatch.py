#!/usr/bin/env python3
"""
Test script to investigate the mismatch between Strategic Thinking Lens frameworks and extracted concepts.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    generate_course_domain_strategic_lens, 
    get_top_ranked_concepts_with_lens_shifting,
    detect_course_concept_domains,
    extract_application_field,
    CONCEPT_GLOSSARY
)

def test_concept_extraction_for_linear_optimization():
    """Test concept extraction for linear optimization query."""
    
    print("🔍 Testing Concept Extraction for Linear Optimization")
    print("=" * 60)
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    
    try:
        # Get domain and application field
        domains = detect_course_concept_domains(query)
        application_field = extract_application_field(query)
        course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
        
        print(f"Query: {query}")
        print(f"Detected domains: {domains}")
        print(f"Course domain: {course_domain}")
        print(f"Application field: {application_field}")
        
        # Generate strategic lens
        strategic_lens = generate_course_domain_strategic_lens(query, course_domain, application_field)
        print(f"\nStrategic Thinking Lens:")
        print("-" * 50)
        print(strategic_lens)
        print("-" * 50)
        
        # Extract concepts
        concepts = get_top_ranked_concepts_with_lens_shifting(query, top_k=4)
        print(f"\nExtracted Concepts:")
        print("-" * 50)
        for i, (concept_name, definition) in enumerate(concepts, 1):
            print(f"{i}. {concept_name}: {definition}")
        print("-" * 50)
        
        # Check for expected concepts
        expected_concepts = ["linear optimization", "sensitivity analysis"]
        found_expected = []
        missing_expected = []
        
        for expected in expected_concepts:
            found = False
            for concept_name, _ in concepts:
                if expected.lower() in concept_name.lower():
                    found_expected.append(concept_name)
                    found = True
                    break
            if not found:
                missing_expected.append(expected)
        
        print(f"\nExpected concepts found: {found_expected}")
        print(f"Expected concepts missing: {missing_expected}")
        
        # Check what's in the CONCEPT_GLOSSARY
        print(f"\nAvailable concepts in CONCEPT_GLOSSARY:")
        print("-" * 50)
        for concept_name in CONCEPT_GLOSSARY.keys():
            if "linear" in concept_name.lower() or "sensitivity" in concept_name.lower():
                print(f"- {concept_name}")
        print("-" * 50)
        
        return len(missing_expected) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_concept_glossary_mapping():
    """Test the mapping between framework names and concept glossary."""
    
    print(f"\n🔧 Testing Concept Glossary Mapping")
    print("=" * 50)
    
    # Framework names from Strategic Thinking Lens
    framework_names = [
        "Linear optimization modeling",
        "Sensitivity analysis",
        "Monte Carlo simulation",
        "Decision tree analysis",
        "Expected value calculations"
    ]
    
    # Concept names in CONCEPT_GLOSSARY
    concept_names = list(CONCEPT_GLOSSARY.keys())
    
    print("Framework names in Strategic Thinking Lens:")
    for framework in framework_names:
        print(f"  - {framework}")
    
    print(f"\nConcept names in CONCEPT_GLOSSARY:")
    for concept in concept_names:
        if any(keyword in concept.lower() for keyword in ["linear", "sensitivity", "monte", "decision", "expected"]):
            print(f"  - {concept}")
    
    # Check for exact matches
    print(f"\nExact matches:")
    for framework in framework_names:
        framework_lower = framework.lower()
        matches = []
        for concept in concept_names:
            if framework_lower in concept.lower() or concept.lower() in framework_lower:
                matches.append(concept)
        if matches:
            print(f"  {framework} -> {matches}")
        else:
            print(f"  {framework} -> NO MATCH")
    
    # Check for partial matches
    print(f"\nPartial matches:")
    for framework in framework_names:
        framework_words = framework.lower().split()
        matches = []
        for concept in concept_names:
            concept_words = concept.lower().split()
            if any(word in concept_words for word in framework_words):
                matches.append(concept)
        if matches:
            print(f"  {framework} -> {matches}")

def test_concept_extraction_scoring():
    """Test the scoring mechanism for concept extraction."""
    
    print(f"\n🔧 Testing Concept Extraction Scoring")
    print("=" * 50)
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    query_lower = query.lower()
    
    print(f"Query: {query}")
    print(f"Query (lowercase): {query_lower}")
    
    # Check which concepts should match
    relevant_concepts = []
    for concept_name, concept_data in CONCEPT_GLOSSARY.items():
        if isinstance(concept_data, dict):
            definition = concept_data["definition"]
            aliases = concept_data.get("aliases", [])
        else:
            definition = concept_data
            aliases = []
        
        # Check if concept name appears in query
        if concept_name.lower() in query_lower:
            relevant_concepts.append((concept_name, "name_match"))
        # Check if any alias appears in query
        elif any(alias.lower() in query_lower for alias in aliases):
            relevant_concepts.append((concept_name, "alias_match"))
        # Check if definition keywords appear in query
        elif any(word in query_lower for word in definition.lower().split() if len(word) > 3):
            relevant_concepts.append((concept_name, "definition_match"))
    
    print(f"\nRelevant concepts found:")
    for concept_name, match_type in relevant_concepts:
        print(f"  - {concept_name} ({match_type})")
    
    if not relevant_concepts:
        print("  No relevant concepts found!")
    
    return len(relevant_concepts) > 0

if __name__ == "__main__":
    print("🚀 Starting Concept Extraction Mismatch Investigation")
    print("=" * 70)
    
    # Run tests
    test1_result = test_concept_extraction_for_linear_optimization()
    test_concept_glossary_mapping()
    test2_result = test_concept_extraction_scoring()
    
    print(f"\n📊 INVESTIGATION RESULTS")
    print("=" * 50)
    
    print(f"Concept extraction test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Concept scoring test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("✅ Concept extraction is working correctly")
    else:
        print("❌ Concept extraction needs investigation")
        
        if not test1_result:
            print("  - Issue: Expected concepts not being extracted")
        if not test2_result:
            print("  - Issue: Concept scoring not finding relevant concepts") 