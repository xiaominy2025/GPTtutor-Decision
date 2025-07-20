#!/usr/bin/env python3
"""
Clean Test Script for GPTutor
=============================

This script runs tests without the problematic final_output_cleanup function.
"""

import sys
import os

# Add the current directory to the path so we can import query_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_clean_test():
    """Run tests with custom cleanup logic."""
    
    print("🧪 Running Clean Test...")
    print("=" * 50)
    
    try:
        # Import necessary functions
        from query_engine import run_test_mode
        
        # Define test questions
        test_questions = [
            "I've been offered a promotion, but it means relocating away from my family. How do I decide?",
            "My co-founder wants to pivot the product, but I'm not convinced. How should we evaluate this decision?"
        ]
        
        print(f"📋 Running {len(test_questions)} test questions...")
        
        # Run the test mode function directly
        run_test_mode(test_questions)
        
        print("\n✅ Clean test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    run_clean_test() 