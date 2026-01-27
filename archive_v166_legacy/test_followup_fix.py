#!/usr/bin/env python3
"""
Test Follow-up Questions Fix
===========================

Test script to verify that the follow-up questions fix is working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query

def test_followup_questions():
    """Test that we get the correct number of follow-up questions"""
    print("🧪 Testing Follow-up Questions Fix")
    print("=" * 50)
    
    test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year"
    
    print(f"📋 Testing query: {test_query[:60]}...")
    
    try:
        result = process_query(test_query)
        
        # Count follow-up questions
        lines = result.split('\n')
        followup_section = False
        question_count = 0
        questions = []
        
        for line in lines:
            if "**Follow-up Prompts**" in line:
                followup_section = True
            elif followup_section and line.strip().startswith('- '):
                question_count += 1
                questions.append(line.strip())
            elif followup_section and line.strip().startswith('**'):
                break
        
        print(f"📊 Found {question_count} follow-up questions")
        
        if 2 <= question_count <= 4:
            print("✅ Correct number of follow-up questions!")
            print("\n📋 Questions found:")
            for i, question in enumerate(questions, 1):
                print(f"  {i}. {question}")
        else:
            print(f"❌ Incorrect number of follow-up questions: {question_count}")
            print("Expected 2-4 questions")
        
        # Check response length
        print(f"\n📊 Response length: {len(result)} characters")
        
        # Check for required sections
        required_sections = ["**Strategic Thinking Lens**", "**Story in Action**", "**Follow-up Prompts**", "**Concepts/Tools**"]
        missing_sections = []
        
        for section in required_sections:
            if section not in result:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections: {missing_sections}")
        else:
            print("✅ All required sections present")
        
        return 2 <= question_count <= 4
        
    except Exception as e:
        print(f"❌ Error testing follow-up questions: {e}")
        return False

if __name__ == "__main__":
    success = test_followup_questions()
    if success:
        print("\n🎉 Follow-up questions fix is working!")
    else:
        print("\n⚠️ Follow-up questions fix needs attention.")
    sys.exit(0 if success else 1) 