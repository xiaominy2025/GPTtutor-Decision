#!/usr/bin/env python3
"""
Systematic comparison of query engine concepts with course glossary
"""
import json
import os

def load_query_engine_concepts():
    """Extract concepts from query_engine.py"""
    concepts = {}
    
    # Read query_engine.py and extract CONCEPT_GLOSSARY
    with open('query_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the CONCEPT_GLOSSARY section
    start_marker = "CONCEPT_GLOSSARY = {"
    end_marker = "}\n\n# Domain categorization"
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ Could not find CONCEPT_GLOSSARY in query_engine.py")
        return concepts
    
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        print("❌ Could not find end marker in query_engine.py")
        return concepts
    
    # Extract the glossary section
    glossary_section = content[start_idx + len(start_marker):end_idx].strip()
    
    # Parse the concepts (this is a simplified parser)
    lines = glossary_section.split('\n')
    current_concept = None
    current_definition = ""
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Check if this is a new concept (starts with quote)
        if line.startswith('"') and '":' in line:
            # Save previous concept if exists
            if current_concept:
                concepts[current_concept] = current_definition.strip()
            
            # Start new concept
            concept_name = line.split('":')[0].strip('"')
            current_concept = concept_name
            current_definition = line.split('":')[1].strip()
        elif current_concept and line:
            # Continue definition
            current_definition += " " + line
    
    # Add the last concept
    if current_concept:
        concepts[current_concept] = current_definition.strip()
    
    return concepts

def load_course_glossary():
    """Load the course glossary.json"""
    try:
        with open('courses/decision/glossary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading course glossary: {e}")
        return {}

def compare_concepts():
    """Compare query engine concepts with course glossary"""
    print("🔍 SYSTEMATIC GLOSSARY ALIGNMENT")
    print("=" * 60)
    
    # Load concepts from both sources
    query_engine_concepts = load_query_engine_concepts()
    course_glossary = load_course_glossary()
    
    print(f"📊 STATISTICS:")
    print(f"   Query Engine concepts: {len(query_engine_concepts)}")
    print(f"   Course glossary concepts: {len(course_glossary)}")
    
    # Find missing concepts
    missing_concepts = {}
    for concept, definition in query_engine_concepts.items():
        if concept not in course_glossary:
            missing_concepts[concept] = definition
    
    print(f"\n❌ MISSING CONCEPTS ({len(missing_concepts)}):")
    print("=" * 60)
    
    for concept, definition in missing_concepts.items():
        print(f"   '{concept}': {definition}")
    
    # Find concepts in course but not in query engine
    extra_concepts = {}
    for concept in course_glossary:
        if concept not in query_engine_concepts:
            extra_concepts[concept] = course_glossary[concept]
    
    print(f"\n➕ EXTRA CONCEPTS IN COURSE ({len(extra_concepts)}):")
    print("=" * 60)
    
    for concept, data in extra_concepts.items():
        print(f"   '{concept}': {data.get('definition', 'No definition')}")
    
    # Generate the complete aligned glossary
    print(f"\n📝 GENERATING COMPLETE ALIGNED GLOSSARY...")
    
    aligned_glossary = {}
    
    # Add all concepts from query engine
    for concept, definition in query_engine_concepts.items():
        # Parse the definition to extract core and aliases
        if '"core": True' in definition:
            core = True
        elif '"core": False' in definition:
            core = False
        else:
            core = True  # Default to True
        
        # Extract aliases
        aliases = []
        if '"aliases":' in definition:
            aliases_start = definition.find('"aliases":') + len('"aliases":')
            aliases_end = definition.find(']', aliases_start)
            if aliases_end > aliases_start:
                aliases_section = definition[aliases_start:aliases_end]
                # Simple parsing of aliases
                aliases = [alias.strip().strip("'\"") for alias in aliases_section.split(',') if alias.strip()]
        
        # Extract clean definition
        clean_definition = definition.split('"definition":')[1].split('"core":')[0].strip().strip('",')
        
        aligned_glossary[concept] = {
            "definition": clean_definition,
            "core": core,
            "aliases": aliases
        }
    
    # Save the aligned glossary
    output_file = 'courses/decision/glossary_aligned.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aligned_glossary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Complete aligned glossary saved to: {output_file}")
    print(f"   Total concepts: {len(aligned_glossary)}")
    
    return aligned_glossary

if __name__ == "__main__":
    compare_concepts() 