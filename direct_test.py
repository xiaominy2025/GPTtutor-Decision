#!/usr/bin/env python3
"""
Direct Test Script for GPTutor
==============================

This script runs tests directly without going through the main loop.
"""

import sys
import os

# Add the current directory to the path so we can import query_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_direct_test():
    """Run tests directly by importing and calling the test function."""
    
    print("🧪 Running Direct Test...")
    print("=" * 50)
    
    try:
        # Import the test function directly
        from query_engine import run_test_mode
        
        # Define test questions
        test_questions = [
            "Should I take the job offer or stay at my current company?",
            "How do I decide between two good options?"
        ]
        
        print(f"📋 Running {len(test_questions)} test questions...")
        
        # Run the test mode function directly
        run_test_mode(test_questions)
        
        print("\n✅ Direct test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    run_direct_test() 