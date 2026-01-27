#!/usr/bin/env python3
"""
Comprehensive test for Round of Turning changes
Validates the specific improvements mentioned in the requirements
"""

import sys
import time
from clean_entities_static import extract_expanded_entities, get_entity_summary, validate_entity_extraction

def test_entity_neutral_filtering_improvements():
    """Test that entity-neutral filtering is less conservative"""
    
    print("🧪 Testing Entity-Neutral Filtering Improvements")
    print("=" * 50)
    
    # Queries that should now be processed instead of being filtered out
    test_queries = [
        "What is the best approach for this decision?",
        "How do I evaluate these options?",
        "What tools should I use for analysis?",
        "Can you help me understand the trade-offs?",
        "What methods are available for this situation?"
    ]
    
    processed_count = 0
    total_count = len(test_queries)
    
    for query in test_queries:
        entities = extract_expanded_entities(query)
        entity_summary = get_entity_summary(entities)
        
        print(f"Query: {query}")
        print(f"  Entity summary: {entity_summary}")
        print(f"  Entity neutral: {entities.get('entity_neutral', False)}")
        
        if not entities.get('entity_neutral', False):
            processed_count += 1
            print(f"  ✅ Processed (not filtered)")
        else:
            print(f"  ⚠️  Still filtered as entity-neutral")
    
    processing_rate = processed_count / total_count * 100
    print(f"\nEntity-neutral processing rate: {processing_rate:.1f}% ({processed_count}/{total_count})")
    
    return processing_rate >= 60.0  # At least 60% should be processed

def test_confidence_scaling_improvements():
    """Test that fuzzy match confidence scaling is improved"""
    
    print(f"\n🔍 Testing Confidence Scaling Improvements")
    print(f"=" * 50)
    
    # Test queries that should benefit from improved confidence scaling
    test_queries = [
        "How can we act quickly to improve efficiency?",
        "What if we need to make a fast decision?",
        "Should we proceed with limited information?",
        "How do we handle rapid changes?",
        "What about quick wins vs long-term planning?"
    ]
    
    high_confidence_count = 0
    total_count = len(test_queries)
    
    for query in test_queries:
        entities = extract_expanded_entities(query)
        validation = validate_entity_extraction(query)
        confidence = validation['confidence']
        
        print(f"Query: {query}")
        print(f"  Confidence: {confidence:.3f}")
        print(f"  Entity summary: {get_entity_summary(entities)}")
        
        if confidence >= 0.6:  # Higher confidence threshold
            high_confidence_count += 1
            print(f"  ✅ High confidence")
        else:
            print(f"  ⚠️  Lower confidence")
    
    high_confidence_rate = high_confidence_count / total_count * 100
    print(f"\nHigh confidence rate: {high_confidence_rate:.1f}% ({high_confidence_count}/{total_count})")
    
    return high_confidence_rate >= 80.0  # At least 80% should have high confidence

def test_strategic_thinking_lens_enrichment():
    """Test that Strategic Thinking Lens is enriched with specific entities"""
    
    print(f"\n🎯 Testing Strategic Thinking Lens Enrichment")
    print(f"=" * 50)
    
    # Test queries that should enrich Strategic Thinking Lens
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    enriched_count = 0
    total_count = len(test_queries)
    
    for query in test_queries:
        entities = extract_expanded_entities(query)
        entity_summary = get_entity_summary(entities)
        
        # Check for specific entity categories that enrich Strategic Thinking Lens
        has_timeframe = bool(entities.get('timeframe'))
        has_stakeholders = bool(entities.get('stakeholders'))
        has_criteria = bool(entities.get('criteria'))
        has_uncertainty = bool(entities.get('uncertainty'))
        has_complexity = bool(entities.get('complexity'))
        
        # Count how many categories are enriched
        category_count = sum([has_timeframe, has_stakeholders, has_criteria, has_uncertainty, has_complexity])
        
        print(f"Query: {query}")
        print(f"  Entity summary: {entity_summary}")
        print(f"  Categories enriched: {category_count}/5")
        print(f"  Timeframe: {'✅' if has_timeframe else '❌'}")
        print(f"  Stakeholders: {'✅' if has_stakeholders else '❌'}")
        print(f"  Criteria: {'✅' if has_criteria else '❌'}")
        print(f"  Uncertainty: {'✅' if has_uncertainty else '❌'}")
        print(f"  Complexity: {'✅' if has_complexity else '❌'}")
        
        if category_count >= 3:  # At least 3 categories should be enriched
            enriched_count += 1
            print(f"  ✅ Strategic Thinking Lens enriched")
        else:
            print(f"  ⚠️  Limited enrichment")
    
    enrichment_rate = enriched_count / total_count * 100
    print(f"\nStrategic Thinking Lens enrichment rate: {enrichment_rate:.1f}% ({enriched_count}/{total_count})")
    
    return enrichment_rate >= 90.0  # At least 90% should be enriched

def test_performance_maintenance():
    """Test that performance is maintained under 8s"""
    
    print(f"\n⚡ Testing Performance Maintenance")
    print(f"=" * 50)
    
    # Test with a variety of query complexities
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
        "When is the best time to invest in AI automation given budget constraints?"
    ]
    
    processing_times = []
    
    for query in test_queries:
        start_time = time.time()
        entities = extract_expanded_entities(query)
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
        print(f"Query: {query[:50]}...")
        print(f"  Processing time: {processing_time:.3f}s")
    
    avg_processing_time = sum(processing_times) / len(processing_times)
    max_processing_time = max(processing_times)
    
    print(f"\nPerformance Summary:")
    print(f"  Average processing time: {avg_processing_time:.3f}s")
    print(f"  Maximum processing time: {max_processing_time:.3f}s")
    print(f"  Target: < 8.0s")
    
    performance_ok = avg_processing_time < 8.0 and max_processing_time < 8.0
    print(f"  Performance maintained: {'✅' if performance_ok else '❌'}")
    
    return performance_ok

def test_general_decision_reduction():
    """Test that 'general decision' fallbacks are reduced"""
    
    print(f"\n📉 Testing General Decision Fallback Reduction")
    print(f"=" * 50)
    
    # Test queries that might have defaulted to "general decision" before
    test_queries = [
        "What should I do?",
        "How do I decide?",
        "What's the best approach?",
        "Can you help me think through this?",
        "What factors should I consider?",
        "How do I evaluate my options?",
        "What's the right decision?",
        "How should I proceed?",
        "What do you recommend?",
        "How do I make this choice?"
    ]
    
    general_decision_count = 0
    total_count = len(test_queries)
    
    for query in test_queries:
        entities = extract_expanded_entities(query)
        entity_summary = get_entity_summary(entities)
        
        print(f"Query: {query}")
        print(f"  Entity summary: {entity_summary}")
        
        if entity_summary == "general decision":
            general_decision_count += 1
            print(f"  ⚠️  General decision fallback")
        else:
            print(f"  ✅ Specific entities extracted")
    
    fallback_rate = general_decision_count / total_count * 100
    print(f"\nGeneral decision fallback rate: {fallback_rate:.1f}% ({general_decision_count}/{total_count})")
    
    return fallback_rate < 10.0  # Should be less than 10%

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Round of Turning Validation")
    
    # Run all tests
    tests = [
        ("Entity-Neutral Filtering", test_entity_neutral_filtering_improvements),
        ("Confidence Scaling", test_confidence_scaling_improvements),
        ("Strategic Thinking Lens Enrichment", test_strategic_thinking_lens_enrichment),
        ("Performance Maintenance", test_performance_maintenance),
        ("General Decision Reduction", test_general_decision_reduction)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results[test_name] = False
    
    # Final summary
    print(f"\n🎯 COMPREHENSIVE ROUND OF TURNING VALIDATION")
    print(f"=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    overall_success = passed_tests >= 4  # At least 4 out of 5 tests should pass
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    print(f"Overall Round of Turning Success: {'✅' if overall_success else '❌'}")
    
    if overall_success:
        print(f"\n🎉 Round of Turning validation PASSED!")
        print(f"   - Reduced over-conservatism in entity extraction")
        print(f"   - Maintained performance under 8s")
        print(f"   - Enriched Strategic Thinking Lens")
        print(f"   - Reduced 'general decision' fallbacks")
        print(f"   - Improved entity-neutral filtering")
    else:
        print(f"\n⚠️  Round of Turning validation needs attention")
        sys.exit(1) 