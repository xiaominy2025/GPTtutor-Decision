#!/usr/bin/env python3
"""
Comprehensive analysis of answer generation logic
Tests how well the system uses all extracted information
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 COMPREHENSIVE ANSWER GENERATION ANALYSIS")
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
    
    # Test cases covering different scenarios
    test_cases = [
        {
            "query": "How should I negotiate a better salary with my boss?",
            "expected_domains": ["negotiation", "human_behaviors"],
            "expected_fields": ["leadership", "finance"],
            "expected_entities": ["people", "money", "organizations"]
        },
        {
            "query": "I have two job offers, how do I decide between them?",
            "expected_domains": ["strategy", "analytical_tools"],
            "expected_fields": ["leadership", "finance"],
            "expected_entities": ["organizations", "money", "timeframes"]
        },
        {
            "query": "How do I optimize our production process to reduce costs?",
            "expected_domains": ["analytical_tools", "strategy"],
            "expected_fields": ["operations", "finance"],
            "expected_entities": ["organizations", "money", "metrics"]
        },
        {
            "query": "What's the best way to tell my team about budget cuts?",
            "expected_domains": ["human_behaviors"],
            "expected_fields": ["leadership", "finance"],
            "expected_entities": ["people", "organizations", "money"]
        },
        {
            "query": "How should we position our product against competitors?",
            "expected_domains": ["strategy"],
            "expected_fields": ["marketing", "strategy"],
            "expected_entities": ["organizations", "concepts"]
        }
    ]
    
    print(f"\n📊 ANALYZING {len(test_cases)} TEST CASES")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        # Extract all information
        domains = detect_course_concept_domains(query)
        fields = extract_application_fields(query)
        entities = extract_enhanced_entities(query)
        
        print(f"📋 EXTRACTED INFORMATION:")
        print(f"   Domains: {domains}")
        print(f"   Fields: {fields}")
        print(f"   Entities: {entities}")
        
        # Generate each section
        strategy_lens = generate_strategy_or_explanation(domains, entities, fields, query)
        story = generate_story_or_analogy(fields, domains, query)
        prompts = generate_reflection_prompts(domains, entities, query)
        concepts = get_top_ranked_concepts(query, domains)
        
        print(f"\n📝 GENERATED CONTENT ANALYSIS:")
        
        # Analyze Strategy Thinking Lens
        print(f"   Strategic Thinking Lens ({len(strategy_lens.split())} words):")
        print(f"     - Uses domains: {'✅' if any(domain in strategy_lens.lower() for domain in domains) else '❌'}")
        print(f"     - Uses fields: {'✅' if any(field in strategy_lens.lower() for field in fields) else '❌'}")
        print(f"     - Uses entities: {'✅' if any(entity_type in strategy_lens.lower() for entity_type in entities.keys()) else '❌'}")
        
        # Analyze Story in Action
        print(f"   Story in Action ({len(story.split())} words):")
        print(f"     - Uses fields: {'✅' if any(field in story.lower() for field in fields) else '❌'}")
        print(f"     - Uses domains: {'✅' if any(domain in story.lower() for domain in domains) else '❌'}")
        print(f"     - Context relevant: {'✅' if any(word in story.lower() for word in query.lower().split()) else '❌'}")
        
        # Analyze Follow-up Prompts
        print(f"   Follow-up Prompts ({len(prompts)} prompts):")
        print(f"     - Domain allocation: {'✅' if len(prompts) <= 4 else '❌'}")
        print(f"     - Domain relevant: {'✅' if any(domain in ' '.join(prompts).lower() for domain in domains) else '❌'}")
        
        # Analyze Concept & Tool
        print(f"   Concept & Tool ({len(concepts)} concepts):")
        print(f"     - Domain allocation: {'✅' if len(concepts) <= 4 else '❌'}")
        print(f"     - Domain relevant: {'✅' if any(domain in str(concepts).lower() for domain in domains) else '❌'}")
        
        # Check for information utilization gaps
        gaps = []
        if not any(domain in strategy_lens.lower() for domain in domains):
            gaps.append("Strategy lens doesn't use detected domains")
        if not any(field in story.lower() for field in fields):
            gaps.append("Story doesn't use detected fields")
        if not any(entity_type in strategy_lens.lower() for entity_type in entities.keys()):
            gaps.append("Strategy lens doesn't use detected entities")
        
        if gaps:
            print(f"   ⚠️  GAPS IDENTIFIED:")
            for gap in gaps:
                print(f"     - {gap}")
        else:
            print(f"   ✅ NO MAJOR GAPS DETECTED")
        
        print("-" * 50)
    
    # Test specific allocation rules
    print(f"\n📋 TESTING ALLOCATION RULES")
    print("=" * 60)
    
    allocation_tests = [
        {
            "name": "Single Domain (3 prompts, 3 concepts)",
            "query": "How do I improve team communication?",
            "expected_prompts": 3,
            "expected_concepts": 3
        },
        {
            "name": "Multiple Domains (4 prompts, 4 concepts)",
            "query": "How should I negotiate a job offer with multiple options?",
            "expected_prompts": 4,
            "expected_concepts": 4
        }
    ]
    
    for test in allocation_tests:
        print(f"\n🔍 {test['name']}")
        print(f"Query: {test['query']}")
        
        domains = detect_course_concept_domains(test['query'])
        entities = extract_enhanced_entities(test['query'])
        fields = extract_application_fields(test['query'])
        
        prompts = generate_reflection_prompts(domains, entities, test['query'])
        concepts = get_top_ranked_concepts(test['query'], domains)
        
        print(f"   Domains: {domains}")
        print(f"   Prompts: {len(prompts)} (expected: {test['expected_prompts']})")
        print(f"   Concepts: {len(concepts)} (expected: {test['expected_concepts']})")
        
        if len(prompts) == test['expected_prompts']:
            print(f"   ✅ Prompts allocation correct")
        else:
            print(f"   ❌ Prompts allocation incorrect")
            
        if len(concepts) == test['expected_concepts']:
            print(f"   ✅ Concepts allocation correct")
        else:
            print(f"   ❌ Concepts allocation incorrect")
    
    print(f"\n🎯 SUMMARY RECOMMENDATIONS:")
    print("=" * 60)
    print("1. Strategy Thinking Lens should better utilize:")
    print("   - Extracted entities (people, organizations, money, etc.)")
    print("   - Specific keywords from the query")
    print("   - Application fields for context")
    
    print("\n2. Story in Action should:")
    print("   - Be more tightly coupled to the specific query context")
    print("   - Use detected domains more explicitly")
    print("   - Incorporate entity information when relevant")
    
    print("\n3. Follow-up Prompts should:")
    print("   - Better reflect the specific query context")
    print("   - Use entity information to create more targeted questions")
    
    print("\n4. Concept & Tool should:")
    print("   - Implement proper scoring thresholds (0.50, 0.40, 0.35)")
    print("   - Better domain allocation logic")
    print("   - Include fallback mechanisms")
    
    print("\n✅ Analysis complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 