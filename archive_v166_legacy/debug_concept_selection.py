#!/usr/bin/env python3
"""
Debug script to test concept selection and output structure
"""

from query_engine import process_query, get_top_ranked_concepts

def debug_concept_selection():
    """Debug concept selection for the specific query"""
    
    query = "How to convey bad news to my boss?"
    
    print("🔍 DEBUGGING CONCEPT SELECTION")
    print("=" * 50)
    print(f"Query: {query}")
    print()
    
    # Test concept selection directly
    print("📋 DIRECT CONCEPT SELECTION:")
    concepts = get_top_ranked_concepts(query, top_k=3)
    print(f"Selected {len(concepts)} concepts:")
    for i, (name, definition) in enumerate(concepts, 1):
        print(f"  {i}. {name}")
        print(f"     Definition: {definition[:100]}...")
        print()
    
    # Test full process_query
    print("🚀 FULL PROCESS_QUERY OUTPUT:")
    print("=" * 50)
    result = process_query(query)
    print(result)
    
    # Analyze the output structure
    print("\n📊 OUTPUT ANALYSIS:")
    print("=" * 30)
    
    # Check for duplicate headers
    strategic_lens_count = result.count("**Strategic Thinking Lens**")
    story_count = result.count("**Story in Action**")
    followup_count = result.count("**Follow-up Prompts**")
    concepts_count = result.count("**Concepts/Tools**")
    
    print(f"Strategic Thinking Lens headers: {strategic_lens_count}")
    print(f"Story in Action headers: {story_count}")
    print(f"Follow-up Prompts headers: {followup_count}")
    print(f"Concepts/Tools headers: {concepts_count}")
    
    # Check for "For example" headers
    for_example_count = result.count("**For example**")
    print(f"'For example' headers: {for_example_count}")
    
    # Count concepts in the output
    concepts_section = ""
    if "**Concepts/Tools**" in result:
        start_idx = result.find("**Concepts/Tools**")
        end_idx = result.find("\n\n", start_idx)
        if end_idx == -1:
            end_idx = len(result)
        concepts_section = result[start_idx:end_idx]
    
    concept_lines = [line.strip() for line in concepts_section.split('\n') if line.strip().startswith('-')]
    print(f"Concepts found in output: {len(concept_lines)}")
    for line in concept_lines:
        print(f"  {line}")

if __name__ == "__main__":
    debug_concept_selection() 