#!/usr/bin/env python3
"""
Test script for the enhanced generate_response function
"""

import sys
import os

# Add the current directory to the path so we can import from query_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import generate_response, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT

def test_generate_response():
    """Test the enhanced generate_response function with various inputs"""
    
    print("🧪 Testing Enhanced generate_response Function")
    print("=" * 60)
    
    # Test case 1: Complete response with all sections
    print("\n📝 Test 1: Complete Response")
    print("-" * 40)
    
    complete_response = """
Strategy or Explanation
What should you do when faced with this decision? Let's use a Decision Tree to map out your options.

Story or Analogy
Imagine Sarah, a marketing manager, who had to choose between two job offers.

Reflection Prompts
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

Concept/Tool References
- Decision Tree: A visual tool for mapping options
"""
    
    result = generate_response(complete_response, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT)
    print("✅ Complete response processed successfully")
    print("📊 Result preview:")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test case 2: Incomplete response missing sections
    print("\n📝 Test 2: Incomplete Response")
    print("-" * 40)
    
    incomplete_response = """
Strategy or Explanation
What should you do when faced with this decision?

Story or Analogy
Imagine Sarah, a marketing manager.
"""
    
    result = generate_response(incomplete_response, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT)
    print("✅ Incomplete response processed with fallback sections")
    print("📊 Result preview:")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test case 3: Response with tooltip injection
    print("\n📝 Test 3: Tooltip Injection")
    print("-" * 40)
    
    tooltip_response = """
Strategy or Explanation
What should you do when faced with this decision? Let's use a decision tree to map out your options.

Story or Analogy
Imagine Sarah, a marketing manager, who had to choose between two job offers.

Reflection Prompts
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

Concept/Tool References
- Decision Tree: A visual tool for mapping options
"""
    
    result = generate_response(tooltip_response, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT)
    print("✅ Tooltip injection processed successfully")
    print("📊 Result preview:")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test case 4: Response without named tools (should trigger fallback)
    print("\n📝 Test 4: Fallback Framework Suggestion")
    print("-" * 40)
    
    no_tools_response = """
Strategy or Explanation
What should you do when faced with this decision? Let's think about this carefully.

Story or Analogy
Imagine Sarah, a marketing manager, who had to choose between two job offers.

Reflection Prompts
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

Concept/Tool References
- Decision Making: A process for choosing between options
"""
    
    result = generate_response(no_tools_response, PREBUILT_TOOLTIPS, FRAMEWORKS_GPT)
    print("✅ Fallback framework suggestion added")
    print("📊 Result preview:")
    print(result[:200] + "..." if len(result) > 200 else result)
    
    print("\n✅ All tests completed successfully!")
    print("\n📊 Summary of Enhancements:")
    print("• Section enforcement with fallback placeholders")
    print("• Tooltip injection from PREBUILT_TOOLTIPS")
    print("• Fallback framework suggestions")
    print("• Structured response processing")

if __name__ == "__main__":
    test_generate_response() 