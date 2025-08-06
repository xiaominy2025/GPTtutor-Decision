#!/usr/bin/env python3
"""
Analyze entity extraction issues to understand low extraction rates.
"""

import json
import sys
sys.path.append('.')

from clean_entities_static import extract_expanded_entities, get_entity_summary

def analyze_entity_extraction():
    """Analyze why entity extraction is failing for many queries."""
    
    # Test queries from the comprehensive test that had 0% confidence
    failed_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "What are the risks and opportunities of entering a new market segment?",
        "How do I optimize our supply chain to reduce costs?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "What are the risks of investing in emerging market stocks?",
        "How do I model the uncertainty in my investment portfolio?",
        "How do I negotiate better terms with a dominant supplier?",
        "How can I create value in a zero-sum negotiation?",
        "How do I assess the risks of launching a new product?",
        "What are the worst-case scenarios for our business plan?",
        "How do cognitive biases affect our team's decision-making?",
        "How do anchoring effects influence our pricing decisions?",
        "How do we evaluate competing technology platforms?",
        "How should we prioritize our innovation projects?",
        "What are the risks of ignoring climate change in our strategy?",
        "How do we manage currency risk in international operations?",
        "What are the trade-offs of outsourcing vs. local production?",
        "How should we approach market entry in emerging economies?",
        "What are the political risks of investing in foreign markets?"
    ]
    
    # Load clean entities to understand what's available
    with open('clean_entities.json', 'r') as f:
        clean_entities = json.load(f)
    
    print("=== Entity Extraction Analysis ===")
    print(f"Total entities available: {len(clean_entities)}")
    
    # Analyze entity categories
    categories = {}
    for entity in clean_entities:
        cat = entity['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entity['entity'])
    
    print("\nEntity categories:")
    for cat, entities in categories.items():
        print(f"- {cat}: {len(entities)} entities")
    
    # Test failed queries
    print("\n=== Testing Failed Queries ===")
    
    for i, query in enumerate(failed_queries[:5], 1):  # Test first 5
        print(f"\nQuery {i}: {query}")
        
        # Extract entities
        entities = extract_expanded_entities(query)
        confidence = entities.get('confidence', 0.0)
        summary = get_entity_summary(entities)
        
        print(f"Confidence: {confidence:.3f}")
        print(f"Summary: {summary}")
        
        # Check what entities should have been found
        query_lower = query.lower()
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
            for match in potential_matches[:3]:  # Show first 3
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
    
    # Analyze the entity extraction logic
    print("\n=== Entity Extraction Logic Analysis ===")
    
    # Check entity-neutral detection
    entity_neutral_indicators = [
        "what is", "how do i", "what are", "how to", "what tools", "what methods",
        "what techniques", "what frameworks", "what approach", "what is the best",
        "how do you", "what should", "what would", "what could", "explain", "describe",
        "tell me about", "what does", "how does", "why does", "when does", "where does",
        "can you", "could you", "would you", "please", "help me", "guide me",
        "show me", "give me", "provide", "suggest", "recommend", "advise"
    ]
    
    print("Entity-neutral indicators that trigger 0% confidence:")
    for indicator in entity_neutral_indicators:
        print(f"- '{indicator}'")
    
    # Check minimum word count requirement
    print(f"\nMinimum word count requirement: 5 words")
    
    # Test some queries that should work
    print("\n=== Testing Queries That Should Work ===")
    
    working_queries = [
        "I need to decide between two job offers with different salaries",
        "Should I accept a promotion that requires relocation?",
        "How do I choose between staying at my current company or joining a startup?",
        "What factors should I consider when negotiating my salary?",
        "How should our company position itself against new competitors?"
    ]
    
    for i, query in enumerate(working_queries, 1):
        print(f"\nQuery {i}: {query}")
        entities = extract_expanded_entities(query)
        confidence = entities.get('confidence', 0.0)
        summary = get_entity_summary(entities)
        print(f"Confidence: {confidence:.3f}")
        print(f"Summary: {summary}")
    
    return {
        "total_entities": len(clean_entities),
        "categories": categories,
        "entity_neutral_indicators": entity_neutral_indicators
    }

if __name__ == "__main__":
    results = analyze_entity_extraction() 