#!/usr/bin/env python3
"""Test the new decision domains and their Story in Action templates"""

from query_engine import context_aware_fallbacks, extract_application_field

# Test queries for new domains
test_queries = [
    "Should I invest in stocks or bonds?",
    "Which health insurance plan should I choose?",
    "Should I get a master's degree or certifications?",
    "Should I move to a new city for my career?",
    "How do I handle conflict between team members?",
    "Should I take a stance on this controversial issue?",
    "Should I adopt AI technology for my business?"
]

print("🧪 Testing New Decision Domains")
print("=" * 50)

for query in test_queries:
    domain = extract_application_field(query)
    fallbacks = context_aware_fallbacks(query)
    story = fallbacks.get('Story in Action', '')
    word_count = len(story.split())
    
    print(f"Query: {query}")
    print(f"Domain: {domain}")
    print(f"Story words: {word_count}")
    print(f"Story: {story}")
    print("-" * 50) 