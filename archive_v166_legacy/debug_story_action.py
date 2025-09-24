#!/usr/bin/env python3
"""
Debug script to test Story in Action expansion specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import query_engine
import re

def test_story_action_expansion():
    """Test Story in Action expansion specifically"""
    query = "How do cognitive biases affect team decision making?"
    
    print("Testing Story in Action expansion...")
    print(f"Query: {query}")
    print()
    
    # Test with enhanced entities enabled
    query_engine.USE_ENHANCED_ENTITIES = True
    enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
    
    print("=== ENHANCED ANSWER ===")
    print(enhanced_answer)
    print()
    
    # Extract Story in Action section
    story_match = re.search(r'\*\*Story in Action\*\*(.*?)(?=\*\*Follow-up Prompts\*\*|\*\*Concepts/Tools\*\*|\Z)', enhanced_answer, re.DOTALL)
    if story_match:
        story_content = story_match.group(1).strip()
        story_words = len(story_content.split())
        print(f"Story in Action: {story_words} words")
        print(f"Content: {story_content}")
        print()
        
        # Test the expansion function directly
        print("Testing expansion function directly...")
        from query_engine import expand_section_content
        expanded_content = expand_section_content(story_content, 70, query)
        expanded_words = len(expanded_content.split())
        print(f"Expanded to: {expanded_words} words")
        print(f"Expanded content: {expanded_content}")
    else:
        print("❌ Story in Action section not found!")

if __name__ == "__main__":
    test_story_action_expansion() 