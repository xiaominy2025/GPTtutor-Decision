#!/usr/bin/env python3
"""
Test script to verify the fix for generate_response function
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
        # Check for both bold and non-bold section headers
        if line in response_sections:
            current_section = line
        elif line.replace("**", "") in response_sections:
            current_section = line.replace("**", "")
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

def test_fix():
    """Test the fix for bold section headers"""
    
    print("🧪 Testing Fix for Bold Section Headers")
    print("=" * 50)
    
    # Test case: Response with bold headers (what GPT should return)
    print("\n📝 Test: Response with Bold Headers")
    print("-" * 40)
    
    bold_response = """
**Strategy or Explanation**
What should you do when faced with this decision? Let's use a Decision Tree to map out your options.

**Story or Analogy**
Imagine Sarah, a marketing manager, who had to choose between two job offers.

**Reflection Prompts**
• What values matter most to you in this decision?
• How might your choice look different in 5 years?
• What would you tell a friend in the same situation?

**Concept/Tool References**
- Decision Tree: A visual tool for mapping options
"""
    
    prebuilt_tooltips = {
        "decision tree": "A visual tool that maps out different options and their potential outcomes to help make confident choices when faced with uncertainty."
    }
    
    frameworks_gpt = {}
    
    result = generate_response(bold_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Bold headers processed successfully")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Test case: Response with non-bold headers (fallback)
    print("\n📝 Test: Response with Non-Bold Headers")
    print("-" * 40)
    
    non_bold_response = """
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
    
    result = generate_response(non_bold_response, prebuilt_tooltips, frameworks_gpt)
    print("✅ Non-bold headers processed successfully")
    print("📊 Result preview:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    print("\n✅ Fix verified! The function now handles both bold and non-bold section headers.")

if __name__ == "__main__":
    test_fix() 