#!/usr/bin/env python3
"""
Generate comprehensive concept library list
"""

import query_engine

def generate_concept_list():
    print("COMPREHENSIVE CONCEPT LIBRARY")
    print("=" * 60)
    print()
    
    concepts = query_engine.CONCEPT_GLOSSARY
    
    # Sort concepts alphabetically
    sorted_concepts = sorted(concepts.items())
    
    for i, (concept, details) in enumerate(sorted_concepts, 1):
        core_status = 'CORE' if details.get('core', False) else 'NON-CORE'
        print(f"{i:2d}. {concept.upper()} ({core_status})")
        print(f"    Definition: {details['definition']}")
        print(f"    Keywords: {', '.join(details['aliases'])}")
        print()

if __name__ == "__main__":
    generate_concept_list() 