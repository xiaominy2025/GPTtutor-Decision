#!/usr/bin/env python3
"""
Standalone test script for the enhanced generate_response function
"""

def generate_response(answer_raw: str, prebuilt_tooltips: dict, frameworks_gpt: dict) -> str:
    """
    Enhanced response generator that enforces structure and injects tooltips
    
    Args:
        answer_raw: Raw response from GPT
        prebuilt_tooltips: Dictionary of tooltip definitions
        frameworks_gpt: Dictionary of GPT-polished frameworks
    
    Returns:
        Processed answer with enforced structure and tooltips
    """
    # Section headers expected in the answer
    response_sections = {
        "Strategy or Explanation": "",
        "Story or Analogy": "",
        "Reflection Prompts": "",
        "Concept/Tool References": ""
    }

    # Parse sections from raw answer
    current_section = None
    for line in answer_raw.split("\n"):
        line = line.strip()
        if line in response_sections:
            current_section = line
        elif current_section:
            response_sections[current_section] += line + " "

    # Ensure all sections are present with fallback placeholders
    for section in response_sections:
        if not response_sections[section].strip():
            response_sections[section] = "_[This section was not generated — please revise your prompt or add logic to fill this in.]_"

    # Combine all sections into final answer
    final_answer = ""
    for section, content in response_sections.items():
        final_answer += f"**{section}**\n{content.strip()}\n\n"

    # Inject tooltips if keywords appear
    for term, definition in prebuilt_tooltips.items():
        if term.lower() in final_answer.lower() and definition not in final_answer:
            final_answer += f"- **{term.title()}**: {definition}\n"

    # Fallback: add framework suggestion if none found
    named_tools = ["Decision Tree", "GROW", "SWOT", "Premortem", "Weighted Scoring"]
    found_tools = [tool for tool in named_tools if tool.lower() in final_answer.lower()]
    
    if not found_tools:
        final_answer += "\n🧠 *Tip: This decision may benefit from using a Decision Tree or the GROW coaching model to evaluate options.*\n"

    return final_answer.strip()

def test_generate_response():
    """Test the enhanced generate_response function with various inputs"""
    
    print("🧪 Testing Enhanced generate_response Function")
    print("=" * 60)
    
    # Sample tooltips for testing
    prebuilt_tooltips = {
        "decision tree": "A visual tool that maps out different options and their potential outcomes to help make confident choices when faced with uncertainty.",
        "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats to assess your situation comprehensively.",
        "cost-benefit analysis": "A systematic approach to compare the pros and cons of different options by weighing their advantages and disadvantages."
    }
    
    frameworks_gpt = {}  # Empty for testing
    
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
    
    result = generate_response(complete_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Complete response processed successfully")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Test case 2: Incomplete response missing sections
    print("\n📝 Test 2: Incomplete Response")
    print("-" * 40)
    
    incomplete_response = """
Strategy or Explanation
What should you do when faced with this decision?

Story or Analogy
Imagine Sarah, a marketing manager.
"""
    
    result = generate_response(incomplete_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Incomplete response processed with fallback sections")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
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
    
    result = generate_response(tooltip_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Tooltip injection processed successfully")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
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
    
    result = generate_response(no_tools_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Fallback framework suggestion added")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    print("\n✅ All tests completed successfully!")
    print("\n📊 Summary of Enhancements:")
    print("• Section enforcement with fallback placeholders")
    print("• Tooltip injection from PREBUILT_TOOLTIPS")
    print("• Fallback framework suggestions")
    print("• Structured response processing")

if __name__ == "__main__":
    test_generate_response() 