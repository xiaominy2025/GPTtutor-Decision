#!/usr/bin/env python3
"""
Clean Entities Static Module for V1.6.5.1
Entity extraction using static clean_entities.json file with fuzzy matching
Replaces runtime stoplist filtering for production use
"""

import json
import re
from typing import Dict, List, Any, Optional
from functools import lru_cache
try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    from difflib import SequenceMatcher
    RAPIDFUZZ_AVAILABLE = False

# ============================================================================
# STATIC ENTITIES LOADING
# ============================================================================

def load_clean_entities() -> List[Dict[str, Any]]:
    """Load the static clean entities from JSON file"""
    try:
        with open("clean_entities.json", "r", encoding="utf-8") as f:
            entities = json.load(f)
        print(f"✅ Loaded {len(entities)} clean entities from static file")
        return entities
    except Exception as e:
        print(f"❌ Error loading clean entities: {e}")
        return []

# Load entities at module level
CLEAN_ENTITIES = load_clean_entities()

# ============================================================================
# FUZZY MATCHING FUNCTIONS
# ============================================================================

def fuzzy_match_ratio(str1: str, str2: str) -> float:
    """
    Calculate fuzzy match ratio between two strings using RapidFuzz for performance.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if RAPIDFUZZ_AVAILABLE:
        # PRODUCTION OPTIMIZATION: Use RapidFuzz for faster fuzzy matching
        return fuzz.partial_ratio(str1.lower(), str2.lower()) / 100.0
    else:
        # Fallback to difflib for compatibility
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def find_fuzzy_matches(query: str, entities: List[Dict[str, Any]], 
                      min_ratio: float = 0.6, max_matches: int = 5) -> List[Dict[str, Any]]:
    """
    Find fuzzy matches between query and entities.
    
    Args:
        query: The input query
        entities: List of entity dictionaries
        min_ratio: Minimum similarity ratio (0.0 to 1.0)
        max_matches: Maximum number of matches to return per category
        
    Returns:
        List of matched entities with similarity scores
    """
    query_lower = query.lower()
    query_words = query_lower.split()
    
    matches = []
    
    for entity_data in entities:
        entity_text = entity_data["entity"].lower()
        entity_words = entity_text.split()
        
        # Check for exact matches first (highest priority)
        if entity_text in query_lower:
            matches.append({
                "entity": entity_data["entity"],
                "category": entity_data["category"],
                "relevance": entity_data["relevance"],
                "match_type": "exact",
                "similarity": 1.0
            })
            continue
        
        # Check for word-level matches
        word_matches = 0
        total_words = len(entity_words)
        
        for entity_word in entity_words:
            if entity_word in query_lower:
                word_matches += 1
        
        # Calculate word-level similarity
        if total_words > 0:
            word_similarity = word_matches / total_words
            if word_similarity >= 0.5:  # At least 50% of words match
                matches.append({
                    "entity": entity_data["entity"],
                    "category": entity_data["category"],
                    "relevance": entity_data["relevance"],
                    "match_type": "word_level",
                    "similarity": word_similarity
                })
                continue
        
        # Check for fuzzy string similarity
        similarity = fuzzy_match_ratio(entity_text, query_lower)
        # ROUND OF TURNING: Further lower min_ratio threshold to allow more borderline matches
        if similarity >= (min_ratio - 0.10):  # Allow 0.50 as cutoff instead of 0.6
            matches.append({
                "entity": entity_data["entity"],
                "category": entity_data["category"],
                "relevance": entity_data["relevance"],
                "match_type": "fuzzy",
                "similarity": similarity
            })
    
    # Sort by similarity and relevance, then limit results
    matches.sort(key=lambda x: (x["similarity"], x["relevance"]), reverse=True)
    
    # Group by category and limit per category
    category_matches = {}
    for match in matches:
        category = match["category"]
        if category not in category_matches:
            category_matches[category] = []
        if len(category_matches[category]) < max_matches:
            category_matches[category].append(match)
    
    # Flatten results
    final_matches = []
    for category_matches_list in category_matches.values():
        final_matches.extend(category_matches_list)
    
    return final_matches

# ============================================================================
# ENTITY EXTRACTION FUNCTIONS
# ============================================================================

@lru_cache(maxsize=200)
def extract_expanded_entities(query: str) -> Dict[str, Any]:
    """
    Extract entities from a decision-making query using static clean entities with fuzzy matching.
    
    Args:
        query: The input query string
        
    Returns:
        Dictionary containing extracted entities with confidence scores
    """
    query_lower = query.lower()
    
    # Enhanced entity-neutral detection with ROUND OF TURNING improvements
    entity_neutral_indicators = [
        "what is", "how do i", "what are", "how to", "what tools", "what methods",
        "what techniques", "what frameworks", "what approach", "what is the best",
        "how do you", "what should", "what would", "what could", "explain", "describe",
        "tell me about", "what does", "how does", "why does", "when does", "where does",
        "can you", "could you", "would you", "please", "help me", "guide me",
        "show me", "give me", "provide", "suggest", "recommend", "advise"
    ]
    
    # ROUND OF TURNING: Define decision keywords for better entity-neutral filtering
    decision_keywords = [
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
    
    # ROUND OF TURNING: Loosen entity-neutral filtering - require BOTH conditions AND fallback
    if any(indicator in query_lower for indicator in entity_neutral_indicators) \
       and not any(word in query_lower for word in decision_keywords) \
       and len(query.split()) < 6:
        return {
            "timeframe": {}, "stakeholders": {}, "criteria": {},
            "uncertainty": {}, "complexity": {}, "confidence": 0.0,
            "entity_neutral": True
        }

    # Lazy loading: Only process entities if query has sufficient complexity
    if len(query.split()) < 5 and not any(word in query_lower for word in decision_keywords):
        return {
            "timeframe": {}, "stakeholders": {}, "criteria": {},
            "uncertainty": {}, "complexity": {}, "confidence": 0.0,
            "entity_neutral": True
        }

    # Initialize result structure
    extracted_entities = {
        "timeframe": {},
        "stakeholders": {},
        "criteria": {},
        "uncertainty": {},
        "complexity": {},
        "confidence": 0.0,
        "entity_neutral": False
    }
    
    # Category mapping
    category_mapping = {
        "Timeframe": "timeframe",
        "Stakeholder": "stakeholders", 
        "Criteria": "criteria",
        "Uncertainty": "uncertainty",
        "Complexity": "complexity"
    }
    
    # Find fuzzy matches with ROUND OF TURNING: Lower min_ratio threshold
    fuzzy_matches = find_fuzzy_matches(query, CLEAN_ENTITIES, min_ratio=0.6, max_matches=3)
    
    # ROUND OF TURNING: Add match distribution tracking
    match_distribution = {
        "exact": 0,
        "word_level": 0,
        "fuzzy": 0
    }
    
    # Process matches and adjust confidence based on match type
    for match in fuzzy_matches:
        entity_text = match["entity"]
        category = match["category"]
        base_relevance = match["relevance"]
        match_type = match["match_type"]
        similarity = match["similarity"]
        
        # Track match distribution
        match_distribution[match_type] += 1
        
        # ROUND OF TURNING: Adjust confidence scaling for fuzzy matches
        if match_type == "exact":
            confidence_multiplier = 1.0
        elif match_type == "word_level":
            confidence_multiplier = 0.9
        else:  # fuzzy
            # ROUND OF TURNING: Boost fuzzy match confidence from 0.8 to 0.9
            confidence_multiplier = similarity * 0.9  # Increased from 0.8 to 0.9
        
        adjusted_confidence = base_relevance * confidence_multiplier
        
        # Map category to internal structure
        internal_category = category_mapping.get(category, "criteria")
        
        # Create entity entry
        entity_entry = {
            "confidence": adjusted_confidence,
            "examples": [entity_text],
            "match_type": match_type,
            "similarity": similarity
        }
        
        # Use entity text as key (simplified)
        entity_key = entity_text.replace(" ", "_").replace("-", "_")
        
        if internal_category not in extracted_entities:
            extracted_entities[internal_category] = {}
        
        extracted_entities[internal_category][entity_key] = entity_entry
    
    # Add match distribution to results
    extracted_entities["match_distribution"] = match_distribution
    
    # Calculate overall confidence
    entity_categories = ["timeframe", "stakeholders", "criteria", "uncertainty", "complexity"]
    total_entities = sum(len(extracted_entities.get(cat, {})) for cat in entity_categories)
    if total_entities > 0:
        total_confidence = sum(
            entity["confidence"] 
            for cat in entity_categories
            for entity in extracted_entities.get(cat, {}).values()
        )
        extracted_entities["confidence"] = total_confidence / total_entities
    
    return extracted_entities

def get_entity_summary(entities: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of extracted entities.
    
    Args:
        entities: Dictionary of extracted entities
        
    Returns:
        String summary of entities
    """
    summary_parts = []
    
    # Add timeframe
    if entities.get("timeframe"):
        timeframe = max(entities["timeframe"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"timeframe: {timeframe[0]}")
    
    # Add stakeholders
    if entities.get("stakeholders"):
        stakeholders = [k for k, v in entities["stakeholders"].items() if v["confidence"] > 0.1]
        if stakeholders:
            summary_parts.append(f"stakeholders: {', '.join(stakeholders)}")
    
    # Add criteria
    if entities.get("criteria"):
        criteria = [k for k, v in entities["criteria"].items() if v["confidence"] > 0.1]
        if criteria:
            summary_parts.append(f"criteria: {', '.join(criteria)}")
    
    # Add uncertainty
    if entities.get("uncertainty"):
        uncertainty = max(entities["uncertainty"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"uncertainty: {uncertainty[0]}")
    
    # Add complexity
    if entities.get("complexity"):
        complexity = max(entities["complexity"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"complexity: {complexity[0]}")
    
    # Return partial summary if any entities found, otherwise "general decision"
    if summary_parts:
        return "; ".join(summary_parts)
    else:
        return "general decision"

def validate_entity_extraction(query: str) -> Dict[str, Any]:
    """
    Validate entity extraction and provide debugging information.
    
    Args:
        query: The query to validate
        
    Returns:
        Dictionary with validation results
    """
    entities = extract_expanded_entities(query)
    
    validation_result = {
        "query": query,
        "entities_found": sum(len(entities.get(key, {})) for key in ["timeframe", "stakeholders", "criteria", "uncertainty", "complexity"]),
        "confidence": entities.get("confidence", 0.0),
        "entity_summary": get_entity_summary(entities),
        "detailed_entities": entities,
        "is_valid": entities.get("confidence", 0.0) > 0.1,
        "match_distribution": entities.get("match_distribution", {})
    }
    
    return validation_result

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_fuzzy_matching():
    """Test fuzzy matching functionality"""
    test_queries = [
        "Should we expand into international markets?",
        "How do we evaluate different pricing strategies for our new product?",
        "How can we improve our production capacity planning?",
        "What forecasting method should we use for seasonal demand?",
        "How can I create value in a zero-sum negotiation?"
    ]
    
    print("🧪 Testing Fuzzy Entity Matching")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        
        # Test fuzzy matching
        fuzzy_matches = find_fuzzy_matches(query, CLEAN_ENTITIES, min_ratio=0.6, max_matches=3)
        
        print(f"Fuzzy matches found: {len(fuzzy_matches)}")
        for match in fuzzy_matches[:3]:
            print(f"  - {match['entity']} ({match['category']}, relevance: {match['relevance']:.3f}, match_type: {match['match_type']}, similarity: {match['similarity']:.3f})")
        
        # Test full extraction
        entities = extract_expanded_entities(query)
        confidence = entities.get('confidence', 0.0)
        summary = get_entity_summary(entities)
        
        print(f"Extraction confidence: {confidence:.3f}")
        print(f"Entity summary: {summary}")
        print(f"Match distribution: {entities.get('match_distribution', {})}")

if __name__ == "__main__":
    test_fuzzy_matching() 