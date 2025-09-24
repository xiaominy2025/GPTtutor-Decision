#!/usr/bin/env python3
"""
Simple test script to verify clean output from query_engine.py
"""

import subprocess
import sys

def test_clean_output():
    """Test that query_engine.py produces clean output without developer information"""
    
    test_questions = [
        "I've been offered a strategic HQ role but must leave a city I love.",
        "My mentor offered me funding for grad school, but I'm unsure I want to go."
    ]
    
    print("🧪 Testing Clean Output from Query Engine")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 40)
        
        try:
            # Run the query engine with the test question
            result = subprocess.run(
                ['python', 'query_engine.py'],
                input=question + '\nexit\n',
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            
            # Check for problematic developer information
            problematic_patterns = [
                '📚 Retrieved',
                '🎯 Synthesized Answer:',
                '📊 Sources:',
                '⏱️ Response time:',
                '📈 Quality check:',
                '🔧 Grammar & Clarity Improvements Applied:',
                '✅ No grammar or clarity issues detected',
                '🔋 Token Efficiency:',
                '📈 Usage:',
                '💰 Cost savings:',
                '[TOOLTIPS METADATA FOR UI]:',
                '⚠️ Context was smart-truncated',
                '  [1]',
                '  [2]',
                '  [3]',
                '  [4]',
                '  [5]',
                '❌ API Error:',
                '❌ No response received from API',
                '❌ Error from OpenAI API:',
                '❌ Error processing test question',
                '✅ TEST MODE COMPLETE:',
                '✅ Test mode completed. Exiting.',
                '👋 Exiting. Goodbye!',
                '📊 Usage Statistics:',
                '⚠️ Please enter a non-empty question.',
                '❌ Error embedding query:',
                '❌ Error searching FAISS index:',
                '⚠️ No results found in the index.'
            ]
            
            found_problematic = []
            for pattern in problematic_patterns:
                if pattern in output:
                    found_problematic.append(pattern)
            
            if found_problematic:
                print(f"❌ Found problematic developer information:")
                for pattern in found_problematic:
                    print(f"   • {pattern}")
                print(f"\nOutput preview:")
                print(output[:500] + "..." if len(output) > 500 else output)
            else:
                print("✅ No developer information found in output")
                print("✅ Output appears to be clean and user-facing")
                
                # Check if the output starts with the expected format
                if "**How to Strategize Your Decision**" in output:
                    print("✅ Output starts with proper decision-making format")
                else:
                    print("❌ Output does not start with expected format")
                
                print(f"\nOutput preview:")
                print(output[:500] + "..." if len(output) > 500 else output)
                
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
        except Exception as e:
            print(f"❌ Error running test: {e}")
    
    print(f"\n✅ Clean output testing completed!")

if __name__ == "__main__":
    test_clean_output() 