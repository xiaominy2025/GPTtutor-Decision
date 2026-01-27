#!/usr/bin/env python3
"""
Test script for entity extraction improvements
"""

from expanded_entities import extract_expanded_entities, get_entity_summary, EXPANDED_ENTITIES, calculate_entity_confidence
import re

def test_job_offer_entities():
    query = "I have two job offers, how to choose?"
    entities = extract_expanded_entities(query)
    
    print("=== ENTITY EXTRACTION TEST ===")
    print(f"Query: {query}")
    print(f"Summary: {get_entity_summary(entities)}")
    print(f"Stakeholders: {entities.get('stakeholders', {})}")
    print(f"Criteria: {entities.get('criteria', {})}")
    print(f"Confidence: {entities.get('confidence', 0.0)}")
    
    # Test confidence calculation directly
    print("\n=== DIRECT CONFIDENCE TEST ===")
    query_lower = query.lower()
    
    # Test career_individual stakeholder
    career_patterns = EXPANDED_ENTITIES["stakeholders"]["career_individual"]["patterns"]
    confidence = calculate_entity_confidence(query_lower, career_patterns)
    print(f"Career individual confidence: {confidence}")
    
    # Test career criteria
    career_criteria_patterns = EXPANDED_ENTITIES["criteria"]["career"]["patterns"]
    confidence = calculate_entity_confidence(query_lower, career_criteria_patterns)
    print(f"Career criteria confidence: {confidence}")
    
    # Debug: Test patterns manually
    print("\n=== PATTERN DEBUGGING ===")
    
    # Test stakeholder patterns
    print("Testing stakeholder patterns:")
    for stakeholder_type, stakeholder_data in EXPANDED_ENTITIES["stakeholders"].items():
        for pattern in stakeholder_data["patterns"]:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                print(f"  ✓ {stakeholder_type}: {pattern} -> '{match.group()}'")
            else:
                print(f"  ✗ {stakeholder_type}: {pattern}")
    
    # Test criteria patterns
    print("\nTesting criteria patterns:")
    for criteria_type, criteria_data in EXPANDED_ENTITIES["criteria"].items():
        for pattern in criteria_data["patterns"]:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                print(f"  ✓ {criteria_type}: {pattern} -> '{match.group()}'")
            else:
                print(f"  ✗ {criteria_type}: {pattern}")

if __name__ == "__main__":
    test_job_offer_entities() 