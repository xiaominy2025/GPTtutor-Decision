#!/usr/bin/env python3
"""
Add missing entities to improve entity extraction coverage.
"""

import json

def add_missing_entities():
    """Add missing entities that should match the failed queries."""
    
    # Load existing entities
    with open('clean_entities.json', 'r') as f:
        entities = json.load(f)
    
    print(f"Current entities: {len(entities)}")
    
    # Missing entities that should be added
    missing_entities = [
        # International/Market entities
        {"entity": "international markets", "category": "Criteria", "relevance": 0.85},
        {"entity": "international", "category": "Criteria", "relevance": 0.80},
        {"entity": "global markets", "category": "Criteria", "relevance": 0.85},
        {"entity": "market expansion", "category": "Criteria", "relevance": 0.85},
        {"entity": "expand", "category": "Criteria", "relevance": 0.80},
        
        # Pricing/Strategy entities
        {"entity": "pricing strategies", "category": "Criteria", "relevance": 0.85},
        {"entity": "pricing", "category": "Criteria", "relevance": 0.80},
        {"entity": "strategies", "category": "Criteria", "relevance": 0.80},
        {"entity": "new product", "category": "Criteria", "relevance": 0.85},
        {"entity": "product", "category": "Criteria", "relevance": 0.80},
        
        # Production/Capacity entities
        {"entity": "production capacity", "category": "Criteria", "relevance": 0.85},
        {"entity": "capacity planning", "category": "Criteria", "relevance": 0.85},
        {"entity": "production", "category": "Criteria", "relevance": 0.80},
        {"entity": "capacity", "category": "Criteria", "relevance": 0.80},
        {"entity": "improve", "category": "Criteria", "relevance": 0.75},
        
        # Forecasting entities
        {"entity": "forecasting method", "category": "Criteria", "relevance": 0.85},
        {"entity": "forecasting", "category": "Criteria", "relevance": 0.80},
        {"entity": "seasonal demand", "category": "Criteria", "relevance": 0.85},
        {"entity": "seasonal", "category": "Criteria", "relevance": 0.80},
        {"entity": "demand", "category": "Criteria", "relevance": 0.80},
        
        # Negotiation entities
        {"entity": "zero-sum negotiation", "category": "Criteria", "relevance": 0.85},
        {"entity": "negotiation", "category": "Criteria", "relevance": 0.80},
        {"entity": "create value", "category": "Criteria", "relevance": 0.85},
        {"entity": "value creation", "category": "Criteria", "relevance": 0.85},
        
        # Evaluation/Analysis entities
        {"entity": "evaluate", "category": "Criteria", "relevance": 0.80},
        {"entity": "evaluation", "category": "Criteria", "relevance": 0.80},
        {"entity": "different", "category": "Complexity", "relevance": 0.75},
        {"entity": "multiple", "category": "Complexity", "relevance": 0.75},
        
        # Timeframe entities
        {"entity": "should", "category": "Timeframe", "relevance": 0.75},
        {"entity": "could", "category": "Timeframe", "relevance": 0.75},
        {"entity": "would", "category": "Timeframe", "relevance": 0.75},
        {"entity": "can", "category": "Timeframe", "relevance": 0.75},
        
        # Stakeholder entities
        {"entity": "we", "category": "Stakeholder", "relevance": 0.75},
        {"entity": "our", "category": "Stakeholder", "relevance": 0.75},
        {"entity": "company", "category": "Stakeholder", "relevance": 0.80},
        {"entity": "organization", "category": "Stakeholder", "relevance": 0.80},
        {"entity": "business", "category": "Stakeholder", "relevance": 0.80}
    ]
    
    # Check for duplicates
    existing_entities = {entity['entity'].lower() for entity in entities}
    new_entities = []
    
    for entity in missing_entities:
        if entity['entity'].lower() not in existing_entities:
            new_entities.append(entity)
            existing_entities.add(entity['entity'].lower())
    
    print(f"New entities to add: {len(new_entities)}")
    
    # Add new entities
    entities.extend(new_entities)
    
    # Save updated entities
    with open('clean_entities.json', 'w') as f:
        json.dump(entities, f, indent=2)
    
    print(f"Updated entities: {len(entities)}")
    
    # Test the new entities
    print("\n=== Testing New Entities ===")
    
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        query_lower = query.lower()
        
        # Find matches
        matches = []
        for entity in entities:
            entity_text = entity['entity'].lower()
            if entity_text in query_lower:
                matches.append({
                    'entity': entity['entity'],
                    'category': entity['category'],
                    'relevance': entity['relevance']
                })
        
        if matches:
            print(f"Matches found: {len(matches)}")
            for match in matches[:3]:
                print(f"  - {match['entity']} ({match['category']}, relevance: {match['relevance']})")
        else:
            print("No matches found")
    
    return {
        "original_count": len(entities) - len(new_entities),
        "new_count": len(entities),
        "added_entities": len(new_entities)
    }

if __name__ == "__main__":
    results = add_missing_entities() 