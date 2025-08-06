#!/usr/bin/env python3
"""
Check available entities and why they're not matching failed queries.
"""

import json

def check_entities():
    """Check available entities and test matching."""
    
    # Load entities
    with open('clean_entities.json', 'r') as f:
        entities = json.load(f)
    
    print(f"Total entities: {len(entities)}")
    
    # Test queries that are failing
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    print("\n=== Testing Entity Matching ===")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        query_lower = query.lower()
        
        # Find exact matches
        exact_matches = []
        for entity in entities:
            entity_text = entity['entity'].lower()
            if entity_text in query_lower:
                exact_matches.append({
                    'entity': entity['entity'],
                    'category': entity['category'],
                    'relevance': entity['relevance']
                })
        
        if exact_matches:
            print(f"Exact matches found: {len(exact_matches)}")
            for match in exact_matches[:3]:
                print(f"  - {match['entity']} ({match['category']}, relevance: {match['relevance']})")
        else:
            print("No exact matches found")
            
            # Find partial matches
            query_words = query_lower.split()
            partial_matches = []
            for entity in entities:
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
            else:
                print("No partial matches found")
    
    # Show some sample entities by category
    print("\n=== Sample Entities by Category ===")
    
    categories = {}
    for entity in entities:
        cat = entity['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entity['entity'])
    
    for cat, entity_list in categories.items():
        print(f"\n{cat} ({len(entity_list)} entities):")
        for entity in entity_list[:5]:  # Show first 5
            print(f"  - {entity}")
        if len(entity_list) > 5:
            print(f"  ... and {len(entity_list) - 5} more")

if __name__ == "__main__":
    check_entities() 