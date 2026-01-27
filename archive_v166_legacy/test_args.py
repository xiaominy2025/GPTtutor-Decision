#!/usr/bin/env python3
"""
Test Command Line Arguments
==========================

This script tests if command line arguments are being detected correctly.
"""

import sys

def test_args():
    """Test command line argument detection."""
    
    print("🧪 Testing Command Line Arguments...")
    print("=" * 50)
    
    print(f"sys.argv: {sys.argv}")
    print(f"len(sys.argv): {len(sys.argv)}")
    
    if len(sys.argv) > 1:
        print(f"First argument: {sys.argv[1]}")
        if sys.argv[1] == "--test":
            print("✅ --test argument detected!")
        else:
            print(f"❌ Unexpected argument: {sys.argv[1]}")
    else:
        print("❌ No arguments provided")
    
    print("\n✅ Argument test complete!")

if __name__ == "__main__":
    test_args() 