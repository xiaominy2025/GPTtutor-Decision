#!/usr/bin/env python3
"""
Post-cleanup test corpus to validate outputs after legacy code removal.
"""

import sys
import json
import os
sys.path.append('.')

import query_engine

# Test corpus with diverse scenarios
TEST_QUERIES = [
    "During a stressful salary negotiation, how can I stay confident without overcommitting?",
    "Under tariff uncertainty, how should I plan my production?",
    "How should a startup decide whether to pivot or stay the course?",
    "In a global expansion, how can a company evaluate whether to enter a new market?",
    "How can I use Monte Carlo simulation to evaluate investment risks under uncertainty?",
    "In a merger negotiation, how can I avoid anchoring bias while still making a strong opening offer?",
    "As a project leader, how do I keep my team motivated when deadlines keep shifting?",
    "When negotiating international trade agreements, how should governments balance short-term concessions with long-term strategic goals?",
    "What is the winner's curse in auctions?",
    "How can I use game theory to analyze competitive strategies?"
]

def capture_post_cleanup_outputs():
    """Capture JSON outputs for all test queries after cleanup."""
    post_cleanup_outputs = {}
    
    for i, query in enumerate(TEST_QUERIES, 1):
        try:
            print(f"Testing Q{i}: {query[:50]}...")
            result = query_engine.run_query_once(query)
            post_cleanup_outputs[f"Q{i}"] = {
                "query": query,
                "output": result
            }
        except Exception as e:
            post_cleanup_outputs[f"Q{i}"] = {
                "query": query,
                "error": str(e)
            }
    
    # Save to file
    with open('post_cleanup_outputs.json', 'w', encoding='utf-8') as f:
        json.dump(post_cleanup_outputs, f, indent=2, ensure_ascii=False)
    
    print(f"Captured {len(post_cleanup_outputs)} test outputs to post_cleanup_outputs.json")
    return post_cleanup_outputs

if __name__ == "__main__":
    capture_post_cleanup_outputs()
