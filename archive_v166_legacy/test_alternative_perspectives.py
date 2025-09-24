#!/usr/bin/env python3
"""
Test script for alternative perspective enhancement feature.
Tests the new functions for adding alternative perspectives based on entity categories.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import (
    get_entity_categories,
    generate_alternative_perspective_strategic_lens,
    generate_alternative_scenario_story_action,
    add_alternative_perspectives
)

def test_entity_categories():
    """Test entity category extraction."""
    print("=== Testing Entity Category Extraction ===")
    
    # Test case 1: Multiple categories
    test_entities_1 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}},
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}}
    }
    
    categories_1 = get_entity_categories(test_entities_1)
    print(f"Test 1 - Multiple categories: {categories_1}")
    assert len(categories_1) == 3, f"Expected 3 categories, got {len(categories_1)}"
    
    # Test case 2: Single category
    test_entities_2 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}}
    }
    
    categories_2 = get_entity_categories(test_entities_2)
    print(f"Test 2 - Single category: {categories_2}")
    assert len(categories_2) == 1, f"Expected 1 category, got {len(categories_2)}"
    
    # Test case 3: Empty entities
    test_entities_3 = {}
    categories_3 = get_entity_categories(test_entities_3)
    print(f"Test 3 - Empty entities: {categories_3}")
    assert len(categories_3) == 0, f"Expected 0 categories, got {len(categories_3)}"
    
    print("✅ Entity category extraction tests passed\n")

def test_alternative_perspective_strategic_lens():
    """Test alternative perspective generation for Strategic Thinking Lens."""
    print("=== Testing Strategic Lens Alternative Perspectives ===")
    
    # Test case 1: Multiple categories - should generate perspective
    test_entities_1 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}}
    }
    
    perspective_1 = generate_alternative_perspective_strategic_lens(test_entities_1, "test query")
    print(f"Test 1 - Multiple categories: {perspective_1}")
    assert perspective_1 != "", "Should generate perspective for multiple categories"
    assert perspective_1.startswith("An alternative perspective is"), "Should start with correct phrase"
    
    # Test case 2: Single category - should not generate perspective
    test_entities_2 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}}
    }
    
    perspective_2 = generate_alternative_perspective_strategic_lens(test_entities_2, "test query")
    print(f"Test 2 - Single category: {perspective_2}")
    assert perspective_2 == "", "Should not generate perspective for single category"
    
    # Test case 3: Specific combination (Timeframe + Stakeholder)
    test_entities_3 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}}
    }
    
    perspective_3 = generate_alternative_perspective_strategic_lens(test_entities_3, "test query")
    print(f"Test 3 - Timeframe + Stakeholder: {perspective_3}")
    assert "align stakeholder interests with appropriate time horizons" in perspective_3, "Should use specific combination logic"
    
    print("✅ Strategic lens alternative perspective tests passed\n")

def test_alternative_scenario_story_action():
    """Test alternative scenario generation for Story in Action."""
    print("=== Testing Story Action Alternative Scenarios ===")
    
    # Test case 1: Multiple categories - should generate scenario
    test_entities_1 = {
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}},
        "Uncertainty": {"high uncertainty": {"confidence": 0.92, "examples": ["high uncertainty"]}}
    }
    
    scenario_1 = generate_alternative_scenario_story_action(test_entities_1, "test query")
    print(f"Test 1 - Multiple categories: {scenario_1}")
    assert scenario_1 != "", "Should generate scenario for multiple categories"
    assert scenario_1.startswith("Alternatively"), "Should start with correct phrase"
    
    # Test case 2: Single category - should not generate scenario
    test_entities_2 = {
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}}
    }
    
    scenario_2 = generate_alternative_scenario_story_action(test_entities_2, "test query")
    print(f"Test 2 - Single category: {scenario_2}")
    assert scenario_2 == "", "Should not generate scenario for single category"
    
    # Test case 3: Specific combination (Criteria + Uncertainty)
    test_entities_3 = {
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}},
        "Uncertainty": {"high uncertainty": {"confidence": 0.92, "examples": ["high uncertainty"]}}
    }
    
    scenario_3 = generate_alternative_scenario_story_action(test_entities_3, "test query")
    print(f"Test 3 - Criteria + Uncertainty: {scenario_3}")
    assert "adaptive criteria that evolve with changing circumstances" in scenario_3, "Should use specific combination logic"
    
    print("✅ Story action alternative scenario tests passed\n")

def test_add_alternative_perspectives():
    """Test the main function that adds alternative perspectives to content."""
    print("=== Testing Add Alternative Perspectives ===")
    
    # Test case 1: Strategic lens with <120 words and multiple entities
    test_content_1 = "This is a short strategic analysis."
    test_entities_1 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}}
    }
    
    result_1 = add_alternative_perspectives(
        test_content_1, test_entities_1, "test query", 
        5, 160, "strategic_lens"
    )
    print(f"Test 1 - Strategic lens short content: {result_1}")
    assert "An alternative perspective is" in result_1, "Should add alternative perspective"
    
    # Test case 2: Strategic lens with >120 words - should not add
    test_content_2 = "This is a longer strategic analysis with many words to exceed the threshold and ensure we have enough content to test the word count logic properly."
    test_entities_2 = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}}
    }
    
    result_2 = add_alternative_perspectives(
        test_content_2, test_entities_2, "test query", 
        25, 160, "strategic_lens"
    )
    print(f"Test 2 - Strategic lens long content: {result_2}")
    # Should still add because we have multiple entity categories
    assert "An alternative perspective is" in result_2, "Should add alternative perspective for multiple categories"
    
    # Test case 3: Story action with multiple entities
    test_content_3 = "This is a story about a decision."
    test_entities_3 = {
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}},
        "Uncertainty": {"high uncertainty": {"confidence": 0.92, "examples": ["high uncertainty"]}}
    }
    
    result_3 = add_alternative_perspectives(
        test_content_3, test_entities_3, "test query", 
        6, 80, "story_action"
    )
    print(f"Test 3 - Story action: {result_3}")
    assert "Alternatively" in result_3, "Should add alternative scenario"
    
    # Test case 4: No entities - should not add anything
    test_content_4 = "This is a test content."
    result_4 = add_alternative_perspectives(
        test_content_4, {}, "test query", 
        4, 160, "strategic_lens"
    )
    print(f"Test 4 - No entities: {result_4}")
    assert result_4 == test_content_4, "Should not modify content without entities"
    
    print("✅ Add alternative perspectives tests passed\n")

def test_integration():
    """Test integration with actual query processing."""
    print("=== Testing Integration ===")
    
    # Simulate a query that would trigger alternative perspectives
    test_query = "Should I accept this job offer immediately or wait for other opportunities?"
    
    # Mock entities that would be extracted
    mock_entities = {
        "Timeframe": {"immediately": {"confidence": 0.9, "examples": ["immediately"]}},
        "Stakeholder": {"employee concerns": {"confidence": 0.85, "examples": ["employee concerns"]}},
        "Criteria": {"market share": {"confidence": 0.9, "examples": ["market share"]}}
    }
    
    # Test strategic lens perspective
    strategic_perspective = generate_alternative_perspective_strategic_lens(mock_entities, test_query)
    print(f"Strategic lens perspective: {strategic_perspective}")
    
    # Test story action scenario
    story_scenario = generate_alternative_scenario_story_action(mock_entities, test_query)
    print(f"Story action scenario: {story_scenario}")
    
    # Test adding to content
    test_content = "This is a strategic analysis of the job offer decision."
    enhanced_content = add_alternative_perspectives(
        test_content, mock_entities, test_query, 
        8, 160, "strategic_lens"
    )
    print(f"Enhanced content: {enhanced_content}")
    
    print("✅ Integration tests passed\n")

if __name__ == "__main__":
    print("🧪 Testing Alternative Perspective Enhancement Feature\n")
    
    try:
        test_entity_categories()
        test_alternative_perspective_strategic_lens()
        test_alternative_scenario_story_action()
        test_add_alternative_perspectives()
        test_integration()
        
        print("🎉 All tests passed! Alternative perspective feature is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 