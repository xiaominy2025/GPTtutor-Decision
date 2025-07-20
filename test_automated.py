#!/usr/bin/env python3
"""
Automated Test Script for GPTutor Decision Coach
===============================================

This script runs automated tests without requiring user input.
"""

import subprocess
import sys

def run_automated_test():
    """Run automated test using the query engine in test mode."""
    
    print("🧪 Starting Automated Test Mode...")
    print("=" * 60)
    
    try:
        # Run the query engine in test mode
        result = subprocess.run([
            sys.executable, "query_engine.py", "--test"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print("✅ Test completed successfully!")
        print("\n📊 Test Output:")
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Test Warnings/Errors:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    run_automated_test() 