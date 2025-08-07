#!/usr/bin/env python3
"""
Script to run 14 questions through the query engine and save results to JSON
"""

import json
import sys
import os
from datetime import datetime

# Import the query engine
from query_engine import process_query

def run_questions_and_save():
    """Run 14 questions through the query engine and save results"""
    
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
    
    results = []
    
    print("Starting query engine tests...")
    print(f"Running {len(questions)} questions...")
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i}/{len(questions)} ---")
        print(f"Question: {question}")
        
        try:
            # Process the query
            answer = process_query(question)
            
            # Store the result
            result = {
                "question_number": i,
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            results.append(result)
            print(f"✓ Question {i} processed successfully")
            
        except Exception as e:
            print(f"✗ Error processing question {i}: {str(e)}")
            result = {
                "question_number": i,
                "question": question,
                "answer": None,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
            results.append(result)
    
    # Save results to JSON file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"query_engine_results_{timestamp}.json"
    
    output_data = {
        "test_run_info": {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(questions),
            "successful_questions": len([r for r in results if r["status"] == "success"]),
            "failed_questions": len([r for r in results if r["status"] == "error"])
        },
        "results": results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Test Complete ===")
    print(f"Results saved to: {filename}")
    print(f"Successful: {output_data['test_run_info']['successful_questions']}")
    print(f"Failed: {output_data['test_run_info']['failed_questions']}")
    
    return filename

if __name__ == "__main__":
    try:
        filename = run_questions_and_save()
        print(f"\nResults saved to: {filename}")
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(1) 