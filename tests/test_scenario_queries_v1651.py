#!/usr/bin/env python3
"""
Extended Scenario Tests for V1.6.5.1
Validates fuzzy matching and alternative perspectives across diverse decision scenarios
"""

import pytest
import sys
import os
import time
from typing import List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the query engine
try:
    from query_engine import process_query
    QUERY_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Query engine import failed: {e}")
    QUERY_ENGINE_AVAILABLE = False

# Import entity extraction for validation
try:
    from clean_entities_static import extract_expanded_entities
    ENTITY_EXTRACTION_AVAILABLE = True
except ImportError as e:
    print(f"❌ Entity extraction import failed: {e}")
    ENTITY_EXTRACTION_AVAILABLE = False

# Comprehensive scenario queries covering different decision domains
SCENARIO_QUERIES = [
    "Should we expand into international markets under high uncertainty?",
    "How do we evaluate different pricing strategies for a new product?",
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

class TestScenarioQueriesV1651:
    """Extended scenario tests for V1.6.5.1"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        if not QUERY_ENGINE_AVAILABLE:
            pytest.skip("Query engine not available")
    
    @pytest.mark.parametrize("query", SCENARIO_QUERIES)
    def test_scenario_query(self, query):
        """Test each scenario query for comprehensive validation"""
        # Process the query
        start_time = time.time()
        result = process_query(query)
        processing_time = time.time() - start_time
        
        # Basic structure validation
        assert isinstance(result, str), f"Result should be string, got {type(result)}"
        assert "**Strategic Thinking Lens**" in result, "Missing Strategic Thinking Lens section"
        assert "**Story in Action**" in result, "Missing Story in Action section"
        assert "**Follow-up Prompts**" in result, "Missing Follow-up Prompts section"
        assert "**Concept" in result, "Missing Concept & Tool section"
        
        # Content length validation (100-600 words)
        word_count = len(result.split())
        assert 100 <= word_count <= 600, f"Content length {word_count} words outside 100-600 range"
        
        # Performance validation
        assert processing_time < 5.0, f"Processing time {processing_time:.2f}s exceeds 5s limit"
        
        # Alternative perspective validation
        has_alternative = (
            "An alternative perspective" in result or 
            "Alternatively" in result or
            "alternative perspective" in result.lower() or
            "risks" in result.lower()
        )
        assert has_alternative, f"No alternative perspective or risk context for query: {query}"
        
        # Entity enrichment validation (if available)
        if ENTITY_EXTRACTION_AVAILABLE:
            entities = extract_expanded_entities(query)
            assert isinstance(entities, dict), "Entity extraction should return dict"
            assert "confidence" in entities, "Entity extraction should include confidence score"
            
            # Check for meaningful entity extraction
            has_entities = any(
                entities.get(category, {}) 
                for category in ["timeframe", "stakeholders", "criteria", "uncertainty", "complexity"]
            )
            assert has_entities, f"No entities extracted for query: {query}"
    
    def test_fuzzy_matching_across_scenarios(self):
        """Test fuzzy matching works across diverse scenarios"""
        if not ENTITY_EXTRACTION_AVAILABLE:
            pytest.skip("Entity extraction not available")
        
        # Test queries that should trigger fuzzy matching
        fuzzy_test_queries = [
            "How can we act quickly to improve efficiency?",
            "What about the risks of moving too fast?",
            "Should we consider the long-term implications?",
            "How do we balance stakeholder needs?"
        ]
        
        for query in fuzzy_test_queries:
            entities = extract_expanded_entities(query)
            
            # Validate entity structure
            assert isinstance(entities, dict)
            assert "confidence" in entities
            
            # Check for fuzzy matches with confidence >= 0.6
            has_fuzzy_match = False
            for category in ["timeframe", "stakeholders", "criteria", "uncertainty", "complexity"]:
                if entities.get(category):
                    for entity_data in entities[category].values():
                        if isinstance(entity_data, dict) and entity_data.get("confidence", 0) >= 0.6:
                            has_fuzzy_match = True
                            break
                    if has_fuzzy_match:
                        break
            
            assert has_fuzzy_match, f"No fuzzy match found for query: {query}"
    
    def test_alternative_perspectives_triggering(self):
        """Test that alternative perspectives are triggered appropriately"""
        # Test queries that should trigger alternative perspectives
        perspective_test_queries = [
            "How should a firm balance capacity planning with regulatory risk?",
            "What if customers demand faster delivery while investors expect higher returns?",
            "How do we handle supplier relationships during a policy shift?",
            "Should we delay international expansion until regulatory uncertainty clears?"
        ]
        
        for query in perspective_test_queries:
            result = process_query(query)
            
            # Check for alternative perspective indicators
            has_alternative = (
                "An alternative perspective" in result or 
                "Alternatively" in result or
                "alternative perspective" in result.lower()
            )
            
            assert has_alternative, f"Alternative perspective not triggered for: {query}"
    
    def test_short_content_handling(self):
        """Test that short content triggers appropriate responses"""
        short_queries = [
            "Should we expand quickly?",
            "What about the risks?",
            "How do we proceed?",
            "What's the best approach?"
        ]
        
        for query in short_queries:
            result = process_query(query)
            
            # For very short queries, check for alternative perspectives or risk context
            if len(result.split()) < 150:
                has_alternative = (
                    "An alternative perspective" in result or 
                    "Alternatively" in result or
                    "alternative perspective" in result.lower() or
                    "risks" in result.lower()
                )
                assert has_alternative, f"Short content should trigger alternative perspective: {query}"
    
    def test_performance_under_load(self):
        """Test performance when processing multiple complex scenarios"""
        complex_queries = [
            "How should a firm balance capacity planning with regulatory risk while considering stakeholder interests?",
            "What if customers demand faster delivery while investors expect higher returns and suppliers face constraints?",
            "How do we handle supplier relationships during a policy shift that affects multiple stakeholders?"
        ]
        
        start_time = time.time()
        results = []
        
        for query in complex_queries:
            result = process_query(query)
            results.append(result)
            
            # Basic validation
            assert isinstance(result, str)
            assert len(result) > 100
        
        total_time = time.time() - start_time
        
        # Should complete all queries within reasonable time
        assert total_time < 15.0, f"Processing {len(complex_queries)} queries took too long: {total_time:.2f}s"
        
        # All results should be different
        assert len(set(results)) == len(results), "All results should be unique"
    
    def test_entity_confidence_distribution(self):
        """Test that entity confidence scores are distributed appropriately"""
        if not ENTITY_EXTRACTION_AVAILABLE:
            pytest.skip("Entity extraction not available")
        
        # Test queries with different complexity levels
        test_queries = [
            "How can we act quickly to improve efficiency?",
            "What about the risks of moving too fast?",
            "Should we consider the long-term implications?",
            "How do we balance stakeholder needs?"
        ]
        
        confidence_scores = []
        
        for query in test_queries:
            entities = extract_expanded_entities(query)
            confidence = entities.get("confidence", 0.0)
            confidence_scores.append(confidence)
            
            # Confidence should be between 0 and 1
            assert 0.0 <= confidence <= 1.0, f"Confidence score {confidence} outside valid range"
        
        # At least some queries should have meaningful confidence
        assert any(score > 0.3 for score in confidence_scores), "No queries had meaningful confidence scores"

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"]) 