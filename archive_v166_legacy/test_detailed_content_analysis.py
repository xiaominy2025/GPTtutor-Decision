#!/usr/bin/env python3
"""
Detailed content analysis to show actual generated content and identify specific issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 DETAILED CONTENT ANALYSIS")
print("=" * 60)

try:
    from query_engine import (
        detect_course_concept_domains, 
        extract_application_fields, 
        extract_enhanced_entities,
        generate_strategy_or_explanation,
        generate_story_or_analogy,
        generate_reflection_prompts,
        get_top_ranked_concepts,
        process_query
    )
    print("✅ Import successful")
    
    # Test with a specific case to see actual content
    test_query = "How should I negotiate a better salary with my boss?"
    
    print(f"\n📝 TESTING: {test_query}")
    print("=" * 60)
    
    # Extract all information
    domains = detect_course_concept_domains(test_query)
    fields = extract_application_fields(test_query)
    entities = extract_enhanced_entities(test_query)
    
    print(f"📋 EXTRACTED INFORMATION:")
    print(f"   Domains: {domains}")
    print(f"   Fields: {fields}")
    print(f"   Entities: {entities}")
    
    # Generate each section
    strategy_lens = generate_strategy_or_explanation(domains, entities, fields, test_query)
    story = generate_story_or_analogy(fields, domains, test_query)
    prompts = generate_reflection_prompts(domains, entities, test_query)
    concepts = get_top_ranked_concepts(test_query, domains)
    
    print(f"\n📝 ACTUAL GENERATED CONTENT:")
    print(f"\n🔍 Strategic Thinking Lens ({len(strategy_lens.split())} words):")
    print(f"'{strategy_lens}'")
    
    print(f"\n🔍 Story in Action ({len(story.split())} words):")
    print(f"'{story}'")
    
    print(f"\n🔍 Follow-up Prompts ({len(prompts)} prompts):")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt}")
    
    print(f"\n🔍 Concept & Tool ({len(concepts)} concepts):")
    for i, concept in enumerate(concepts, 1):
        print(f"   {i}. {concept['term']}: {concept['definition']}")
    
    # Analyze specific issues
    print(f"\n🔍 DETAILED ANALYSIS:")
    
    # Check if domains are mentioned in strategy lens
    domain_mentions = []
    for domain in domains:
        if domain in strategy_lens.lower():
            domain_mentions.append(domain)
    print(f"   Domains mentioned in strategy lens: {domain_mentions}")
    
    # Check if fields are mentioned in story
    field_mentions = []
    for field in fields:
        if field in story.lower():
            field_mentions.append(field)
    print(f"   Fields mentioned in story: {field_mentions}")
    
    # Check if entities are mentioned in strategy lens
    entity_mentions = []
    for entity_type in entities.keys():
        if entity_type in strategy_lens.lower():
            entity_mentions.append(entity_type)
    print(f"   Entity types mentioned in strategy lens: {entity_mentions}")
    
    # Check if keywords are mentioned
    keywords = entities.get('keywords', [])
    keyword_mentions = []
    for keyword in keywords:
        if keyword in strategy_lens.lower():
            keyword_mentions.append(keyword)
    print(f"   Keywords mentioned in strategy lens: {keyword_mentions}")
    
    print(f"\n🎯 SPECIFIC ISSUES IDENTIFIED:")
    
    if not domain_mentions:
        print("   ❌ No detected domains are mentioned in strategy lens")
    if not field_mentions:
        print("   ❌ No detected fields are mentioned in story")
    if not entity_mentions:
        print("   ❌ No detected entities are mentioned in strategy lens")
    if not keyword_mentions:
        print("   ❌ No detected keywords are mentioned in strategy lens")
    
    if domain_mentions and field_mentions and entity_mentions and keyword_mentions:
        print("   ✅ All extracted information is being utilized")
    
    print(f"\n✅ Analysis complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 