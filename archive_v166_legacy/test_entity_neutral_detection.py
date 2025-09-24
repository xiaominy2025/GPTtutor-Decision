#!/usr/bin/env python3
"""
Test entity-neutral detection logic to understand why queries get 0% confidence.
"""

import sys
sys.path.append('.')

from clean_entities_static import extract_expanded_entities, get_entity_summary

def test_entity_neutral_detection():
    """Test the entity-neutral detection logic."""
    
    # Entity-neutral indicators that trigger 0% confidence
    entity_neutral_indicators = [
        "what is", "how do i", "what are", "how to", "what tools", "what methods",
        "what techniques", "what frameworks", "what approach", "what is the best",
        "how do you", "what should", "what would", "what could", "explain", "describe",
        "tell me about", "what does", "how does", "why does", "when does", "where does",
        "can you", "could you", "would you", "please", "help me", "guide me",
        "show me", "give me", "provide", "suggest", "recommend", "advise"
    ]
    
    # Exception words that should allow entity extraction
    exception_words = ["job offer", "job offers", "career", "choose", "select", "decision"]
    
    print("=== Entity-Neutral Detection Analysis ===")
    
    # Test queries that are being incorrectly flagged as entity-neutral
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "What are the risks and opportunities of entering a new market segment?",
        "How do I optimize our supply chain to reduce costs?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "What are the risks of investing in emerging market stocks?",
        "How do I model the uncertainty in my investment portfolio?",
        "How do I negotiate better terms with a dominant supplier?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    print("\n=== Testing Failed Queries ===")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        # Check if query contains entity-neutral indicators
        query_lower = query.lower()
        found_indicators = [indicator for indicator in entity_neutral_indicators if indicator in query_lower]
        
        # Check if query contains exception words
        found_exceptions = [word for word in exception_words if word in query_lower]
        
        print(f"Entity-neutral indicators found: {found_indicators}")
        print(f"Exception words found: {found_exceptions}")
        
        # Check the logic condition
        has_entity_neutral = len(found_indicators) > 0
        has_exceptions = len(found_exceptions) > 0
        
        # The problematic condition:
        # if any(indicator in query_lower for indicator in entity_neutral_indicators) and not any(word in query_lower for word in exception_words):
        condition_result = has_entity_neutral and not has_exceptions
        
        print(f"Has entity-neutral indicators: {has_entity_neutral}")
        print(f"Has exception words: {has_exceptions}")
        print(f"Condition result (triggers 0% confidence): {condition_result}")
        
        # Test actual extraction
        entities = extract_expanded_entities(query)
        confidence = entities.get('confidence', 0.0)
        summary = get_entity_summary(entities)
        
        print(f"Actual confidence: {confidence:.3f}")
        print(f"Actual summary: {summary}")
        
        if condition_result and confidence == 0.0:
            print("✅ CONFIRMED: Query incorrectly flagged as entity-neutral")
        elif confidence > 0.0:
            print("✅ Query correctly processed")
        else:
            print("❓ Other issue causing 0% confidence")
    
    print("\n=== Root Cause Analysis ===")
    print("The issue is in the entity-neutral detection logic:")
    print("1. Many legitimate decision queries contain 'how do', 'what are', 'should we'")
    print("2. These are flagged as entity-neutral indicators")
    print("3. The exception list only includes: ['job offer', 'job offers', 'career', 'choose', 'select', 'decision']")
    print("4. This is too restrictive - many business decision queries don't contain these exception words")
    print("5. Result: 50% of queries get 0% confidence even when they contain relevant entities")
    
    print("\n=== Recommended Fix ===")
    print("Expand the exception list to include more decision-related keywords:")
    print("- 'should', 'could', 'would', 'might', 'may'")
    print("- 'expand', 'enter', 'launch', 'invest', 'optimize'")
    print("- 'evaluate', 'assess', 'analyze', 'consider'")
    print("- 'risk', 'opportunity', 'strategy', 'planning'")
    print("- 'market', 'product', 'business', 'company'")
    
    return {
        "entity_neutral_indicators": entity_neutral_indicators,
        "exception_words": exception_words,
        "test_queries": test_queries
    }

if __name__ == "__main__":
    results = test_entity_neutral_detection() 