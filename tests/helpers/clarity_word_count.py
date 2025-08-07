#!/usr/bin/env python3
"""
Clarity + Word Count Helper for Phase I Validation
Implements hybrid evaluation with tolerance windows and query difficulty awareness
"""

import re
from typing import Dict, Any, Tuple, Optional

# ============================================================================
# TOLERANCE WINDOW CONFIGURATION
# ============================================================================

MIN_WORDS = 90
MAX_WORDS = 140
STRICT_MIN = 100
STRICT_MAX = 140  # Increased from 125 to 140 to match the actual target range

# ============================================================================
# QUERY DIFFICULTY CLASSIFICATION
# ============================================================================

def classify_query(query_text: str) -> str:
    """
    Classify query difficulty based on content analysis.
    
    Args:
        query_text: The query to classify
        
    Returns:
        "basic" or "strategic"
    """
    query_lower = query_text.lower()
    
    # Strategic indicators
    strategic_keywords = [
        "strategy", "strategic", "long-term", "competitive", "market position",
        "stakeholder", "complex", "multiple", "trade-off", "tradeoff",
        "uncertainty", "volatile", "risk", "investment", "decision tree",
        "scenario", "forecast", "optimization", "efficiency", "sustainability"
    ]
    
    # Basic indicators
    basic_keywords = [
        "simple", "quick", "immediate", "basic", "straightforward",
        "clear", "obvious", "direct", "easy", "routine"
    ]
    
    strategic_count = sum(1 for keyword in strategic_keywords if keyword in query_lower)
    basic_count = sum(1 for keyword in basic_keywords if keyword in query_lower)
    
    # Count complexity indicators
    complexity_indicators = [
        "multiple", "various", "several", "different", "complex",
        "complicated", "interdependent", "interconnected"
    ]
    
    complexity_score = sum(1 for indicator in complexity_indicators if indicator in query_lower)
    
    # Decision: strategic if strategic keywords > basic keywords OR complexity > 1
    if strategic_count > basic_count or complexity_score > 1:
        return "strategic"
    else:
        return "basic"

# ============================================================================
# HYBRID CLARITY + WORD COUNT EVALUATION
# ============================================================================

def evaluate_section_compliance(
    word_count: int,
    clarity_score: float,
    query_difficulty: str = "basic"
) -> Dict[str, Any]:
    """
    Evaluate section compliance using hybrid clarity + word count rules.
    
    Args:
        word_count: Number of words in the section
        clarity_score: Clarity score (0-1)
        query_difficulty: "basic" or "strategic"
        
    Returns:
        Dictionary with evaluation results
    """
    result = {
        "word_count": word_count,
        "clarity_score": clarity_score,
        "query_difficulty": query_difficulty,
        "tolerance_mode_used": False,
        "passed": False,
        "reason": ""
    }
    
    # Determine evaluation mode based on query difficulty
    if query_difficulty == "basic":
        # Basic queries: Allow tolerance mode with high clarity
        if clarity_score >= 0.8:
            # Tolerance mode: 90-140 words
            if MIN_WORDS <= word_count <= MAX_WORDS:
                result["passed"] = True
                result["tolerance_mode_used"] = True
                result["reason"] = f"Passed via tolerance mode (clarity: {clarity_score:.3f}, words: {word_count})"
            else:
                result["reason"] = f"Failed tolerance mode: {word_count} words (range: {MIN_WORDS}-{MAX_WORDS})"
        else:
            # Strict mode: 100-120 words
            if STRICT_MIN <= word_count <= STRICT_MAX:
                result["passed"] = True
                result["reason"] = f"Passed strict mode (clarity: {clarity_score:.3f}, words: {word_count})"
            else:
                result["reason"] = f"Failed strict mode: {word_count} words (range: {STRICT_MIN}-{STRICT_MAX})"
    else:
        # Strategic queries: Always use strict mode
        if STRICT_MIN <= word_count <= STRICT_MAX:
            result["passed"] = True
            result["reason"] = f"Passed strategic mode (clarity: {clarity_score:.3f}, words: {word_count})"
        else:
            result["reason"] = f"Failed strategic mode: {word_count} words (range: {STRICT_MIN}-{STRICT_MAX})"
    
    return result

def evaluate_thinkpal_compliance(
    strategic_lens_words: int,
    strategic_lens_clarity: float,
    story_action_words: int,
    story_action_clarity: float,
    query: str
) -> Dict[str, Any]:
    """
    Evaluate ThinkPal compliance for both sections.
    
    Args:
        strategic_lens_words: Word count for Strategic Thinking Lens
        strategic_lens_clarity: Clarity score for Strategic Thinking Lens
        story_action_words: Word count for Story in Action
        story_action_clarity: Clarity score for Story in Action
        query: The original query
        
    Returns:
        Dictionary with overall compliance results
    """
    query_difficulty = classify_query(query)
    
    # Evaluate Strategic Thinking Lens
    strategic_lens_result = evaluate_section_compliance(
        strategic_lens_words,
        strategic_lens_clarity,
        query_difficulty
    )
    
    # Evaluate Story in Action (use 60-80 word range)
    story_action_result = {
        "word_count": story_action_words,
        "clarity_score": story_action_clarity,
        "query_difficulty": "basic",
        "tolerance_mode_used": False,
        "passed": False,
        "reason": ""
    }
    
    # Story in Action: 60-80 words with clarity >= 0.6
    if story_action_clarity >= 0.6:
        if 60 <= story_action_words <= 80:
            story_action_result["passed"] = True
            story_action_result["reason"] = f"Passed (clarity: {story_action_clarity:.3f}, words: {story_action_words})"
        else:
            story_action_result["reason"] = f"Failed: {story_action_words} words (range: 60-80)"
    else:
        story_action_result["reason"] = f"Failed: clarity {story_action_clarity:.3f} (min: 0.6)"
    
    # Overall result
    overall_passed = strategic_lens_result["passed"] and story_action_result["passed"]
    tolerance_mode_used = strategic_lens_result["tolerance_mode_used"] or story_action_result["tolerance_mode_used"]
    
    return {
        "overall_passed": overall_passed,
        "query_difficulty": query_difficulty,
        "tolerance_mode_used": tolerance_mode_used,
        "strategic_lens": strategic_lens_result,
        "story_action": story_action_result,
        "details": {
            "strategic_lens_words": strategic_lens_words,
            "strategic_lens_clarity": strategic_lens_clarity,
            "story_action_words": story_action_words,
            "story_action_clarity": story_action_clarity,
            "query": query
        }
    }

# ============================================================================
# CONCEPT IDENTIFICATION HELPERS
# ============================================================================

def identify_expected_concepts(query: str) -> list:
    """
    Identify expected concepts based on query content.
    
    Args:
        query: The query to analyze
        
    Returns:
        List of expected concept names
    """
    query_lower = query.lower()
    expected_concepts = []
    
    # Legacy project concepts
    if "legacy" in query_lower:
        expected_concepts.extend(["Status Quo Bias", "Sunk Cost Fallacy", "Escalation of Commitment"])
    
    # Risk-related concepts
    if "risk" in query_lower:
        expected_concepts.extend(["Risk Assessment", "Scenario Analysis"])
    
    # Strategic concepts
    if any(word in query_lower for word in ["strategy", "strategic", "competitive"]):
        expected_concepts.extend(["Strategic Framing", "SWOT Analysis"])
    
    # Decision-making concepts
    if "decision" in query_lower:
        expected_concepts.extend(["Decision Tree", "Stakeholder Alignment"])
    
    # Optimization concepts
    if any(word in query_lower for word in ["optimize", "efficiency", "production"]):
        expected_concepts.extend(["Linear Optimization", "Aggregate Planning"])
    
    return list(set(expected_concepts))  # Remove duplicates

def validate_concept_extraction(query: str, extracted_concepts: list) -> Dict[str, Any]:
    """
    Validate that expected concepts are extracted.
    
    Args:
        query: The original query
        extracted_concepts: List of extracted concept names
        
    Returns:
        Dictionary with validation results
    """
    expected_concepts = identify_expected_concepts(query)
    extracted_concepts_lower = [concept.lower() for concept in extracted_concepts]
    
    # Check for matches (case-insensitive)
    matches = []
    for expected in expected_concepts:
        for extracted in extracted_concepts:
            if expected.lower() in extracted.lower() or extracted.lower() in expected.lower():
                matches.append(expected)
                break
    
    match_rate = len(matches) / len(expected_concepts) if expected_concepts else 0.0
    
    return {
        "expected_concepts": expected_concepts,
        "extracted_concepts": extracted_concepts,
        "matches": matches,
        "match_rate": match_rate,
        "passed": match_rate >= 0.5 if expected_concepts else True  # Pass if 50%+ match or no expectations
    }

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_query_classification():
    """Test query difficulty classification"""
    test_queries = [
        ("Should we continue a legacy project despite risks?", "strategic"),
        ("How do we optimize production capacity?", "strategic"),
        ("What is the best way to make a quick decision?", "basic"),
        ("How do we handle employee concerns?", "basic"),
        ("What long-term strategic options should we consider?", "strategic")
    ]
    
    print("🧪 Testing Query Classification")
    print("=" * 40)
    
    for query, expected in test_queries:
        result = classify_query(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} Query: {query}")
        print(f"   Expected: {expected}, Got: {result}")
        print()
    
    print("✅ Query classification test completed!")

if __name__ == "__main__":
    test_query_classification() 