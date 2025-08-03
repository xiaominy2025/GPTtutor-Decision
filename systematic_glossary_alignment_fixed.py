#!/usr/bin/env python3
"""
Systematic comparison of query engine concepts with course glossary
"""
import json
import os
import re

def extract_concepts_from_query_engine():
    """Extract concepts from query_engine.py using regex"""
    concepts = {}
    
    with open('query_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the CONCEPT_GLOSSARY section
    pattern = r'CONCEPT_GLOSSARY = \{([^}]+)\}'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find CONCEPT_GLOSSARY in query_engine.py")
        return concepts
    
    glossary_content = match.group(1)
    
    # Parse each concept entry
    concept_pattern = r'"([^"]+)":\s*\{([^}]+)\}'
    matches = re.findall(concept_pattern, glossary_content, re.DOTALL)
    
    for concept_name, concept_data in matches:
        # Extract definition
        definition_match = re.search(r'"definition":\s*"([^"]+)"', concept_data)
        definition = definition_match.group(1) if definition_match else "No definition"
        
        # Extract core flag
        core_match = re.search(r'"core":\s*(True|False)', concept_data)
        core = core_match.group(1) == "True" if core_match else True
        
        # Extract aliases
        aliases_match = re.search(r'"aliases":\s*\[([^\]]+)\]', concept_data)
        aliases = []
        if aliases_match:
            aliases_str = aliases_match.group(1)
            aliases = [alias.strip().strip("'\"") for alias in aliases_str.split(',') if alias.strip()]
        
        concepts[concept_name] = {
            "definition": definition,
            "core": core,
            "aliases": aliases
        }
    
    return concepts

def load_course_glossary():
    """Load the course glossary.json"""
    try:
        with open('courses/decision/glossary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading course glossary: {e}")
        return {}

def compare_and_align():
    """Compare query engine concepts with course glossary and create aligned version"""
    print("🔍 SYSTEMATIC GLOSSARY ALIGNMENT")
    print("=" * 60)
    
    # Load concepts from both sources
    query_engine_concepts = extract_concepts_from_query_engine()
    course_glossary = load_course_glossary()
    
    print(f"📊 STATISTICS:")
    print(f"   Query Engine concepts: {len(query_engine_concepts)}")
    print(f"   Course glossary concepts: {len(course_glossary)}")
    
    # Find missing concepts
    missing_concepts = {}
    for concept, data in query_engine_concepts.items():
        if concept not in course_glossary:
            missing_concepts[concept] = data
    
    print(f"\n❌ MISSING CONCEPTS ({len(missing_concepts)}):")
    print("=" * 60)
    
    for concept, data in missing_concepts.items():
        print(f"   '{concept}': {data['definition']}")
    
    # Find concepts in course but not in query engine
    extra_concepts = {}
    for concept in course_glossary:
        if concept not in query_engine_concepts:
            extra_concepts[concept] = course_glossary[concept]
    
    print(f"\n➕ EXTRA CONCEPTS IN COURSE ({len(extra_concepts)}):")
    print("=" * 60)
    
    for concept, data in extra_concepts.items():
        print(f"   '{concept}': {data.get('definition', 'No definition')}")
    
    # Create the complete aligned glossary
    print(f"\n📝 CREATING COMPLETE ALIGNED GLOSSARY...")
    
    aligned_glossary = {}
    
    # Add all concepts from query engine (this is the source of truth)
    for concept, data in query_engine_concepts.items():
        aligned_glossary[concept] = {
            "definition": data["definition"],
            "core": data["core"],
            "aliases": data["aliases"]
        }
    
    # Save the aligned glossary
    output_file = 'courses/decision/glossary.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aligned_glossary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Complete aligned glossary saved to: {output_file}")
    print(f"   Total concepts: {len(aligned_glossary)}")
    
    # Show summary of changes
    print(f"\n📋 SUMMARY:")
    print(f"   Added {len(missing_concepts)} missing concepts")
    print(f"   Removed {len(extra_concepts)} extra concepts")
    print(f"   Final count: {len(aligned_glossary)} concepts")
    
    return aligned_glossary

if __name__ == "__main__":
    compare_and_align() 