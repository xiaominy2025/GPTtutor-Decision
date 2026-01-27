#!/usr/bin/env python3
"""
Debug script to test word count enforcement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import query_engine

def test_word_count_enforcement():
    """Test word count enforcement directly"""
    query = "How do cognitive biases affect team decision making?"
    
    print("Testing word count enforcement...")
    print(f"Query: {query}")
    print()
    
    # Test with enhanced entities disabled
    query_engine.USE_ENHANCED_ENTITIES = False
    baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
    
    print("=== BASELINE ANSWER ===")
    print(baseline_answer)
    print()
    
    # Test with enhanced entities enabled
    query_engine.USE_ENHANCED_ENTITIES = True
    enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
    
    print("=== ENHANCED ANSWER ===")
    print(enhanced_answer)
    print()
    
    # Extract sections and count words
    import re
    
    # Extract Strategic Thinking Lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*(.*?)(?=\*\*|\Z)', enhanced_answer, re.DOTALL)
    if lens_match:
        lens_content = lens_match.group(1).strip()
        lens_words = len(lens_content.split())
        print(f"Strategic Thinking Lens: {lens_words} words")
        print(f"Content: {lens_content[:100]}...")
        print()
    
    # Extract Story in Action
    story_match = re.search(r'\*\*Story in Action\*\*(.*?)(?=\*\*|\Z)', enhanced_answer, re.DOTALL)
    if story_match:
        story_content = story_match.group(1).strip()
        story_words = len(story_content.split())
        print(f"Story in Action: {story_words} words")
        print(f"Content: {story_content[:100]}...")
        print()

if __name__ == "__main__":
    test_word_count_enforcement() 