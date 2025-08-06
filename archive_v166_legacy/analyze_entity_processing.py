#!/usr/bin/env python3
"""
Analyze entity processing patterns from the comprehensive test run.
"""

import json
import re
from datetime import datetime

def analyze_entity_processing():
    """Analyze entity processing patterns from the test results."""
    
    # Based on the terminal output from the test run
    # Count the different entity processing patterns
    
    # From the test output, I can see these patterns:
    # 1. "high confidence - 10% weight" - normal processing
    # 2. "moderate confidence - 8.5% weight" - soft filter
    # 3. "Entity relevance below soft threshold" - discarded
    
    # Let me count from the test output:
    high_confidence_count = 0
    moderate_confidence_count = 0
    below_threshold_count = 0
    
    # Analyzing the test output manually:
    # Query 1: high confidence
    # Query 2: high confidence  
    # Query 3: high confidence
    # Query 4: high confidence
    # Query 5: high confidence
    # Query 6: below threshold
    # Query 7: below threshold
    # Query 8: below threshold
    # Query 9: below threshold
    # Query 10: high confidence
    # Query 11: below threshold
    # Query 12: below threshold
    # Query 13: below threshold
    # Query 14: high confidence
    # Query 15: high confidence
    # Query 16: below threshold
    # Query 17: below threshold
    # Query 18: high confidence
    # Query 19: below threshold
    # Query 20: high confidence
    # Query 21: below threshold
    # Query 22: high confidence
    # Query 23: high confidence
    # Query 24: below threshold
    # Query 25: below threshold
    # Query 26: high confidence
    # Query 27: below threshold
    # Query 28: high confidence
    # Query 29: high confidence
    # Query 30: below threshold
    # Query 31: high confidence
    # Query 32: below threshold
    # Query 33: high confidence
    # Query 34: below threshold
    # Query 35: high confidence
    # Query 36: high confidence
    # Query 37: high confidence
    # Query 38: below threshold
    # Query 39: below threshold
    # Query 40: below threshold
    
    high_confidence_count = 20  # Queries with "high confidence - 10% weight"
    moderate_confidence_count = 0  # No "moderate confidence - 8.5% weight" found
    below_threshold_count = 20  # Queries with "Entity relevance below soft threshold"
    
    total_queries = 40
    total_with_entities = high_confidence_count + moderate_confidence_count
    soft_filter_percentage = (moderate_confidence_count / total_with_entities * 100) if total_with_entities > 0 else 0
    
    print("=== Entity Processing Analysis ===")
    print(f"Total queries tested: {total_queries}")
    print(f"Queries with high confidence entities (10% weight): {high_confidence_count}")
    print(f"Queries with moderate confidence entities (8.5% weight): {moderate_confidence_count}")
    print(f"Queries with no entities (below threshold): {below_threshold_count}")
    print(f"Total queries with entities: {total_with_entities}")
    print(f"Soft filter percentage: {soft_filter_percentage:.1f}%")
    
    print("\n=== Key Findings ===")
    print("✅ All entities processed were high confidence (>= 0.7)")
    print("✅ No entities fell into the soft filter range (0.6-0.7)")
    print("✅ 50% of queries had entities extracted")
    print("✅ 50% of queries had no entities (below 0.6 threshold)")
    
    print("\n=== Recommendations ===")
    if soft_filter_percentage > 25:
        print("⚠️  Soft filter usage > 25% - consider nudging Tier 2 weight to 0.9")
    else:
        print("✅ Soft filter usage is low - current Tier 2 weight (0.85) is appropriate")
    
    # Check word count patterns from the report
    print("\n=== Word Count Analysis ===")
    print("From the test report, Strategic Thinking Lens word counts:")
    print("- Most responses were below 100 words (target: 100-140)")
    print("- Many responses were 80-95 words")
    print("- This suggests the system is being conservative with content length")
    
    return {
        "total_queries": total_queries,
        "high_confidence_count": high_confidence_count,
        "moderate_confidence_count": moderate_confidence_count,
        "below_threshold_count": below_threshold_count,
        "soft_filter_percentage": soft_filter_percentage,
        "recommendation": "keep_current_weight" if soft_filter_percentage <= 25 else "increase_tier2_weight"
    }

if __name__ == "__main__":
    results = analyze_entity_processing() 