#!/usr/bin/env python3
"""
Test script to check Story in Action section lengths
"""

import query_engine

def test_story_in_action_lengths():
    """Test that Story in Action sections are about half the length of Strategic Thinking Lens"""
    
    test_cases = [
        ("How do I choose a college?", "admission"),
        ("Should I take this job offer?", "job"),
        ("How do I start my own business?", "startup"),
        ("How do I negotiate a better deal?", "negotiation"),
        ("How do I optimize my operations?", "operations"),
        ("What should I do about this decision?", "general")
    ]
    
    print("🧪 Testing Story in Action Length Requirements")
    print("=" * 60)
    
    for query, expected_domain in test_cases:
        print(f"\n📝 Testing: {query}")
        
        # Get fallbacks
        fallbacks = query_engine.context_aware_fallbacks(query)
        strategic_lens = fallbacks.get('Strategic Thinking Lens', '')
        story_in_action = fallbacks.get('Story in Action', '')
        
        strategic_word_count = len(strategic_lens.split())
        story_word_count = len(story_in_action.split())
        
        print(f"   📊 Strategic Thinking Lens: {strategic_word_count} words")
        print(f"   📊 Story in Action: {story_word_count} words")
        print(f"   📊 Ratio: {story_word_count/strategic_word_count:.2f}")
        
        # Check if story is about half the length (40-60% of strategic lens)
        ratio = story_word_count / strategic_word_count
        if 0.4 <= ratio <= 0.6:
            print(f"   ✅ PASS: Story length is appropriate (~50% of Strategic Lens)")
        elif ratio < 0.4:
            print(f"   ⚠️  WARNING: Story is too short (< 40% of Strategic Lens)")
        else:
            print(f"   ⚠️  WARNING: Story is too long (> 60% of Strategic Lens)")
        
        # Show first 150 characters of story
        print(f"   📄 Story preview: {story_in_action[:150]}...")
    
    print("\n" + "=" * 60)
    print("🏁 Story in Action Length Test Complete")

if __name__ == "__main__":
    test_story_in_action_lengths() 