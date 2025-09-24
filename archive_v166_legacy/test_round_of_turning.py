#!/usr/bin/env python3
"""
Test script for Round of Turning changes in entity extraction
Validates the reduced over-conservatism improvements
"""

import sys
import time
from clean_entities_static import extract_expanded_entities, get_entity_summary, validate_entity_extraction

def test_round_of_turning_changes():
    """Test the round of turning changes in entity extraction"""
    
    print("🧪 Testing Round of Turning Changes")
    print("=" * 50)
    
    # Test queries that should benefit from reduced over-conservatism
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?",
        "How should a firm balance capacity planning with regulatory risk?",
        "What if customers demand faster delivery while investors expect higher returns?",
        "How do we handle supplier relationships during a policy shift?",
        "What trade-offs exist between work-life balance and career advancement?",
        "When is the best time to invest in AI automation given budget constraints?",
        "How do we manage operational efficiency while maintaining safety standards?",
        "Should we delay international expansion until regulatory uncertainty clears?"
    ]
    
    results = {
        "total_queries": len(test_queries),
        "enriched_queries": 0,
        "general_decision_fallbacks": 0,
        "borderline_fuzzy_matches": 0,
        "processing_times": [],
        "entity_summaries": [],
        "match_distributions": []
    }
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        start_time = time.time()
        
        # Extract entities
        entities = extract_expanded_entities(query)
        entity_summary = get_entity_summary(entities)
        match_distribution = entities.get('match_distribution', {})
        
        processing_time = time.time() - start_time
        results["processing_times"].append(processing_time)
        
        # Count borderline fuzzy matches (similarity >= 0.50)
        borderline_count = 0
        for cat, ents in entities.items():
            if isinstance(ents, dict) and cat != 'match_distribution':
                for ent in ents.values():
                    if ent.get("match_type") == "fuzzy" and ent.get("similarity", 0) >= 0.50:
                        borderline_count += 1
        
        results["borderline_fuzzy_matches"] += borderline_count
        
        # Track entity summaries and match distributions
        results["entity_summaries"].append(entity_summary)
        results["match_distributions"].append(match_distribution)
        
        # Check for enrichment vs general decision
        if entity_summary != "general decision":
            results["enriched_queries"] += 1
            print(f"✅ Enriched: {entity_summary}")
        else:
            results["general_decision_fallbacks"] += 1
            print(f"⚠️  General decision fallback")
        
        print(f"   Processing time: {processing_time:.3f}s")
        print(f"   Match distribution: {match_distribution}")
        print(f"   Borderline fuzzy matches: {borderline_count}")
        
        # Validate entity extraction
        validation = validate_entity_extraction(query)
        print(f"   Validation confidence: {validation['confidence']:.3f}")
        print(f"   Entities found: {validation['entities_found']}")
    
    # Calculate success metrics
    enrichment_rate = results["enriched_queries"] / results["total_queries"] * 100
    fallback_rate = results["general_decision_fallbacks"] / results["total_queries"] * 100
    avg_processing_time = sum(results["processing_times"]) / len(results["processing_times"])
    
    print(f"\n" + "=" * 50)
    print(f"📊 ROUND OF TURNING RESULTS")
    print(f"=" * 50)
    print(f"Total queries: {results['total_queries']}")
    print(f"Enriched queries: {results['enriched_queries']} ({enrichment_rate:.1f}%)")
    print(f"General decision fallbacks: {results['general_decision_fallbacks']} ({fallback_rate:.1f}%)")
    print(f"Borderline fuzzy matches: {results['borderline_fuzzy_matches']}")
    print(f"Average processing time: {avg_processing_time:.3f}s")
    
    # Success criteria validation
    print(f"\n🎯 SUCCESS CRITERIA VALIDATION")
    print(f"=" * 50)
    
    # Check performance < 8s
    performance_ok = avg_processing_time < 8.0
    print(f"Performance < 8s: {'✅' if performance_ok else '❌'} ({avg_processing_time:.3f}s)")
    
    # Check enrichment rate ≥ 90%
    enrichment_ok = enrichment_rate >= 90.0
    print(f"Enrichment rate ≥ 90%: {'✅' if enrichment_ok else '❌'} ({enrichment_rate:.1f}%)")
    
    # Check fallback rate < 10%
    fallback_ok = fallback_rate < 10.0
    print(f"Fallback rate < 10%: {'✅' if fallback_ok else '❌'} ({fallback_rate:.1f}%)")
    
    # Check for borderline fuzzy matches
    borderline_ok = results["borderline_fuzzy_matches"] > 0
    print(f"Borderline fuzzy matches found: {'✅' if borderline_ok else '❌'} ({results['borderline_fuzzy_matches']})")
    
    # Overall success
    overall_success = performance_ok and enrichment_ok and fallback_ok and borderline_ok
    print(f"\nOverall Round of Turning Success: {'✅' if overall_success else '❌'}")
    
    return overall_success

def test_fuzzy_matching_improvements():
    """Test specific fuzzy matching improvements"""
    
    print(f"\n🔍 Testing Fuzzy Matching Improvements")
    print(f"=" * 50)
    
    # Test queries that should benefit from lowered threshold
    borderline_queries = [
        "How can we act quickly to improve efficiency?",
        "What if we need to make a fast decision?",
        "Should we proceed with limited information?",
        "How do we handle rapid changes?",
        "What about quick wins vs long-term planning?"
    ]
    
    borderline_successes = 0
    
    for query in borderline_queries:
        entities = extract_expanded_entities(query)
        match_distribution = entities.get('match_distribution', {})
        fuzzy_count = match_distribution.get('fuzzy', 0)
        
        print(f"Query: {query}")
        print(f"  Fuzzy matches: {fuzzy_count}")
        print(f"  Entity summary: {get_entity_summary(entities)}")
        
        if fuzzy_count > 0:
            borderline_successes += 1
    
    borderline_rate = borderline_successes / len(borderline_queries) * 100
    print(f"\nBorderline fuzzy match rate: {borderline_rate:.1f}% ({borderline_successes}/{len(borderline_queries)})")
    
    return borderline_rate >= 60.0  # At least 60% should have fuzzy matches

if __name__ == "__main__":
    print("🚀 Starting Round of Turning Validation")
    
    # Test main round of turning changes
    main_success = test_round_of_turning_changes()
    
    # Test fuzzy matching improvements
    fuzzy_success = test_fuzzy_matching_improvements()
    
    # Final summary
    print(f"\n🎯 FINAL ROUND OF TURNING VALIDATION")
    print(f"=" * 50)
    print(f"Main improvements: {'✅' if main_success else '❌'}")
    print(f"Fuzzy matching improvements: {'✅' if fuzzy_success else '❌'}")
    
    overall_success = main_success and fuzzy_success
    print(f"Overall Round of Turning Success: {'✅' if overall_success else '❌'}")
    
    if overall_success:
        print(f"\n🎉 Round of Turning validation PASSED!")
        print(f"   - Reduced over-conservatism in entity extraction")
        print(f"   - Maintained performance under 8s")
        print(f"   - Enriched Strategic Thinking Lens")
        print(f"   - Reduced 'general decision' fallbacks")
    else:
        print(f"\n⚠️  Round of Turning validation needs attention")
        sys.exit(1) 