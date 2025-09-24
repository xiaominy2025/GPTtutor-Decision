#!/usr/bin/env python3
"""
Test script to verify the double header fix
"""

from query_engine import process_query

def test_double_header_fix():
    """Test that the Strategic Thinking Lens section doesn't have duplicate headers"""
    
    # Test questions that were known to have double header issues
    test_questions = [
        "How can I model the risks involved in launching a new product?",
        "How should I approach a negotiation with a dominant supplier?"
    ]
    
    print("Testing double header fix...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i}: {question} ---")
        
        try:
            answer = process_query(question)
            
            # Count Strategic Thinking Lens headers
            header_count = answer.count("**Strategic Thinking Lens**")
            
            print(f"Strategic Thinking Lens headers found: {header_count}")
            
            if header_count == 1:
                print("✅ PASS: Only one header found")
            else:
                print(f"❌ FAIL: Found {header_count} headers (expected 1)")
                
                # Show the problematic section
                lines = answer.split('\n')
                for j, line in enumerate(lines):
                    if "**Strategic Thinking Lens**" in line:
                        print(f"Header found at line {j+1}: {line}")
            
        except Exception as e:
            print(f"❌ Error processing question: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_double_header_fix() 