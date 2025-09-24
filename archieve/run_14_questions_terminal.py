#!/usr/bin/env python3
"""
Script to run 14 questions through the query engine and display results in terminal
"""

import sys
import os
from datetime import datetime

# Import the query engine
from query_engine import process_query

def run_questions_in_terminal():
    """Run 14 questions through the query engine and display results in terminal"""
    
    # Define the 14 questions to test (original 7 + 7 new ones)
    questions = [
        # Original 7 questions
        "How do I reduce groupthink in high-pressure team decisions?",
        "What tools can help me evaluate uncertain outcomes in a strategic expansion decision?",
        "How can I model the risks involved in launching a new product?",
        "How should I approach a negotiation with a dominant supplier?",
        "What methods can I use to simulate demand fluctuations for production planning?",
        "How can I align stakeholder interests when making a controversial decision?",
        "How do personal biases affect strategic decision making?",
        
        # New 7 questions
        "Under tariff uncertainty, how do I plan my production?",
        "I have two job offers, how to choose?",
        "How to convey bad news to my boss?",
        "How do I negotiate a better salary package with my boss?",
        "How to negotiate with a dealership?",
        "How shall I deal with unfair critiques from my manager?",
        "My team members are reluctant to give up his legacy projects, how shall I convince him to think differently?"
    ]
    
    print("🚀 Starting 14 Questions Test")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Questions: {len(questions)}")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}/{len(questions)}")
        print(f"{'='*80}")
        print(f"❓ {question}")
        print(f"\n⏳ Processing...")
        
        try:
            # Process the query
            answer = process_query(question)
            
            print(f"\n✅ ANSWER:")
            print(f"{'='*80}")
            print(answer)
            print(f"{'='*80}")
            print(f"✓ Question {i} completed successfully")
            
        except Exception as e:
            print(f"\n❌ ERROR processing question {i}:")
            print(f"Error: {str(e)}")
            print(f"{'='*80}")
        
        # No pause between questions - run as batch
    
    print(f"\n{'='*80}")
    print("🎉 ALL 14 QUESTIONS COMPLETED!")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        run_questions_in_terminal()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        sys.exit(1) 