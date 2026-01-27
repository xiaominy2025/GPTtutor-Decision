#!/usr/bin/env python3
"""
Debug remaining queries that still have 0% confidence after the fix.
"""

import sys
sys.path.append('.')

from clean_entities_static import extract_expanded_entities, get_entity_summary

def debug_remaining_queries():
    """Debug queries that still have 0% confidence."""
    
    # Queries that still have 0% confidence
    remaining_failed_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    print("=== Debugging Remaining Failed Queries ===")
    
    for i, query in enumerate(remaining_failed_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        # Check word count
        word_count = len(query.split())
        print(f"Word count: {word_count}")
        
        # Check for entity-neutral indicators
        entity_neutral_indicators = [
            "what is", "how do i", "what are", "how to", "what tools", "what methods",
            "what techniques", "what frameworks", "what approach", "what is the best",
            "how do you", "what should", "what would", "what could", "explain", "describe",
            "tell me about", "what does", "how does", "why does", "when does", "where does",
            "can you", "could you", "would you", "please", "help me", "guide me",
            "show me", "give me", "provide", "suggest", "recommend", "advise"
        ]
        
        query_lower = query.lower()
        found_indicators = [indicator for indicator in entity_neutral_indicators if indicator in query_lower]
        print(f"Entity-neutral indicators found: {found_indicators}")
        
        # Check for exception words
        exception_words = [
            "job offer", "job offers", "career", "choose", "select", "decision",
            "should", "could", "would", "might", "may", "will",
            "expand", "enter", "launch", "invest", "optimize", "improve",
            "evaluate", "assess", "analyze", "consider", "examine", "review",
            "risk", "opportunity", "strategy", "planning", "approach",
            "market", "product", "business", "company", "organization",
            "negotiate", "negotiation", "supply", "chain", "production",
            "forecast", "forecasting", "capacity", "demand", "supply",
            "portfolio", "investment", "stocks", "financial", "uncertainty",
            "international", "global", "pricing", "competitive", "advantage"
        ]
        
        found_exceptions = [word for word in exception_words if word in query_lower]
        print(f"Exception words found: {found_exceptions}")
        
        # Check the logic conditions
        has_entity_neutral = len(found_indicators) > 0
        has_exceptions = len(found_exceptions) > 0
        condition1 = has_entity_neutral and not has_exceptions
        condition2 = word_count < 5 and not has_exceptions
        
        print(f"Condition 1 (entity-neutral): {condition1}")
        print(f"Condition 2 (word count < 5): {condition2}")
        
        # Test actual extraction
        entities = extract_expanded_entities(query)
        confidence = entities.get('confidence', 0.0)
        summary = get_entity_summary(entities)
        
        print(f"Actual confidence: {confidence:.3f}")
        print(f"Actual summary: {summary}")
        
        # Check what entities should be found
        import json
        with open('clean_entities.json', 'r') as f:
            clean_entities = json.load(f)
        
        potential_matches = []
        for entity in clean_entities:
            entity_text = entity['entity'].lower()
            if entity_text in query_lower:
                potential_matches.append({
                    'entity': entity['entity'],
                    'category': entity['category'],
                    'relevance': entity['relevance']
                })
        
        if potential_matches:
            print(f"Potential matches found: {len(potential_matches)}")
            for match in potential_matches[:3]:
                print(f"  - {match['entity']} ({match['category']}, relevance: {match['relevance']})")
        else:
            print("No potential matches found")
            
            # Check for partial matches
            partial_matches = []
            query_words = query_lower.split()
            for entity in clean_entities:
                entity_words = entity['entity'].lower().split()
                if any(word in query_words for word in entity_words):
                    partial_matches.append({
                        'entity': entity['entity'],
                        'category': entity['category'],
                        'relevance': entity['relevance']
                    })
            
            if partial_matches:
                print(f"Partial matches found: {len(partial_matches)}")
                for match in partial_matches[:3]:
                    print(f"  - {match['entity']} ({match['category']}, relevance: {match['relevance']})")
    
    print("\n=== Analysis ===")
    print("The remaining failed queries seem to be missing from the exception list.")
    print("We need to add more business decision keywords to the exception list.")
    
    return {
        "remaining_failed_queries": remaining_failed_queries
    }

if __name__ == "__main__":
    results = debug_remaining_queries() 