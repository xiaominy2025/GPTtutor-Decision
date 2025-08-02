#!/usr/bin/env python3
"""Check current word counts of Story in Action sections"""

from query_engine import context_aware_fallbacks

test_queries = [
    "Should I go to college?",
    "Should I take this job offer?",
    "How do I start my own business?",
    "How do I negotiate a better deal?",
    "How do I optimize my operations?",
    "What should I do about this decision?"
]

print("📊 Current Story in Action Word Counts:")
print("=" * 50)

for query in test_queries:
    fallbacks = context_aware_fallbacks(query)
    story = fallbacks.get('Story in Action', '')
    word_count = len(story.split())
    print(f"Query: {query}")
    print(f"Words: {word_count}")
    print(f"Story: {story[:80]}...")
    print("-" * 30) 