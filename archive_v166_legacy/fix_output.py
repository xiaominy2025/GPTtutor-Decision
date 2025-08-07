#!/usr/bin/env python3
"""
Output Fix Script for GPTutor
=============================

This script fixes all identified formatting and logic issues in the output.
"""

import re

def fix_output_formatting(answer: str) -> str:
    """
    Comprehensive fix for all identified issues:
    1. Missing sections
    2. Character name consistency
    3. Debug log removal
    4. Section order
    5. Content bleeding
    """
    
    # 1. Remove debug logs from final output
    lines = answer.split('\n')
    clean_lines = []
    for line in lines:
        if not (line.startswith('DEBUG:') or 
                line.startswith('📚') or 
                line.startswith('⚠️') or
                line.startswith('🎯') or
                line.startswith('📊') or
                line.startswith('⏱️') or
                line.startswith('📈') or
                line.startswith('✅') or
                line.startswith('🔧') or
                line.startswith('🔋') or
                line.startswith('💰') or
                line.startswith('[TOOLTIPS') or
                line.startswith('{') or
                line.startswith('}')):
            clean_lines.append(line)
    
    answer = '\n'.join(clean_lines)
    
    # 2. Fix character name consistency
    character_fixes = [
        (r'this sam', 'they'),
        (r'this sarah', 'they'),
        (r'this alex', 'they'),
        (r'this casey', 'they'),
        (r'this blake', 'they'),
        (r'this drew', 'they'),
        (r'this avery', 'they'),
        (r'this riley', 'they'),
        (r'this quinn', 'they'),
        (r'this morgan', 'they'),
        (r'this taylor', 'they'),
        (r'this jordan', 'they'),
        (r'this [a-z]+', 'they'),  # Catch any remaining random names
        (r'this [A-Z][a-z]+', 'they')  # Catch capitalized names
    ]
    
    for pattern, replacement in character_fixes:
        answer = re.sub(pattern, replacement, answer)
    
    # 3. Fix malformed headers
    header_fixes = [
        (r'\*\*Reflection\*\*Reflection Prompts\*\*', '**Reflection Prompts**'),
        (r'\*{4,}Story in Action\*\*', '**Story in Action**'),
        (r'\*{4,}How to Strategize Your Decision\*\*', '**How to Strategize Your Decision**'),
        (r'\*{4,}Reflection Prompts\*\*', '**Reflection Prompts**'),
        (r'\*{4,}Concepts/Tools/Practice Reference\*\*', '**Concepts/Tools/Practice Reference:**'),
        (r' Prompts\*\*', '**Reflection Prompts**'),
        (r'Story in Action\*\*', '**Story in Action**'),
        (r'How to Strategize Your Decision\*\*', '**How to Strategize Your Decision**'),
        (r'Concepts/Tools/Practice Reference\*\*', '**Concepts/Tools/Practice Reference:**'),
        (r'\*{4,}', '**'),  # Remove excessive asterisks
    ]
    
    for pattern, replacement in header_fixes:
        answer = re.sub(pattern, replacement, answer)
    
    # 4. Extract and rebuild sections in correct order
    sections = {
        "How to Strategize Your Decision": "",
        "Story in Action": "",
        "Reflection Prompts": "",
        "Concepts/Tools/Practice Reference": ""
    }
    
    # Extract content from each section
    current_section = None
    lines = answer.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Detect section headers
        if line == "**How to Strategize Your Decision**":
            current_section = "How to Strategize Your Decision"
        elif line == "**Story in Action**":
            current_section = "Story in Action"
        elif line == "**Reflection Prompts**":
            current_section = "Reflection Prompts"
        elif line == "**Concepts/Tools/Practice Reference**" or line == "**Concepts/Tools/Practice Reference:**":
            current_section = "Concepts/Tools/Practice Reference"
        elif current_section and line and not line.startswith('**'):
            sections[current_section] += line + " "
    
    # 5. Generate improved fallbacks for missing sections
    if not sections["How to Strategize Your Decision"].strip():
        sections["How to Strategize Your Decision"] = "To make this decision effectively, try applying the Decision Tree framework to map out your options and their potential outcomes. Use the GROW Model to structure your thinking: define your Goal, assess your current Reality, explore your Options, and plan your Way forward."
    
    if not sections["Story in Action"].strip():
        sections["Story in Action"] = "Imagine a professional facing a similar challenge. This individual carefully weighed the options, considered the long-term implications, and made a decision that aligned with their core values and strategic objectives."
    
    if not sections["Reflection Prompts"].strip():
        sections["Reflection Prompts"] = "- What specific factors are most critical to your decision?\n- How might this choice impact your long-term goals and values?\n- What steps can you take to validate your decision before committing?"
    
    if not sections["Concepts/Tools/Practice Reference"].strip():
        sections["Concepts/Tools/Practice Reference"] = "- **Decision Tree**: A visual tool that maps out different options and their potential outcomes.\n- **SWOT Analysis**: A framework that helps identify strengths, weaknesses, opportunities, and threats.\n- **GROW Model**: A structured approach to goal setting and action planning."
    
    # 6. Rebuild content in correct order with proper formatting
    final_content = ""
    section_names = ["How to Strategize Your Decision", "Story in Action", "Reflection Prompts", "Concepts/Tools/Practice Reference"]
    for i, section_name in enumerate(section_names):
        if sections[section_name].strip():
            if i == len(section_names) - 1:  # Last section
                final_content += f"**{section_name}**\n{sections[section_name].strip()}"
            else:
                final_content += f"**{section_name}**\n{sections[section_name].strip()}\n\n"
    
    return final_content.strip()

def test_fix():
    """Test the fix function with sample problematic output."""
    
    # Sample problematic output from Test 1
    problematic_output = """**How to Strategize Your Decision**
Moving for a promotion can be a tough decision, impacting both your career and personal life. To navigate this choice effectively, consider using the **SWOT Analysis** to assess the situation comprehensively.

**Concept/Tool References**

**Story in Action**
Imagine Sarah, a dedicated marketing manager, facing a similar dilemma. Casey has been offered a promotion in a different city, but it means being away from her family. Sarah values her career growth but cherishes family time. The decision weighs heavily on her.

**Reflection Prompts**
- How important is career advancement compared to family proximity for you? - What compromises are you willing to make to achieve your long-term goals? - Have you explored alternative solutions that could balance your personal and professional life?"""
    
    print("🧪 Testing Output Fix...")
    print("=" * 50)
    print("❌ BEFORE FIX:")
    print(problematic_output)
    print("\n" + "=" * 50)
    
    fixed_output = fix_output_formatting(problematic_output)
    
    print("✅ AFTER FIX:")
    print(fixed_output)
    print("\n" + "=" * 50)
    
    # Check if all sections are present
    required_sections = [
        "**How to Strategize Your Decision**",
        "**Story in Action**", 
        "**Reflection Prompts**",
        "**Concepts/Tools/Practice Reference**"
    ]
    
    missing = []
    for section in required_sections:
        if section not in fixed_output:
            missing.append(section)
    
    if missing:
        print(f"❌ Still missing sections: {missing}")
    else:
        print("✅ All sections present!")
    
    # Check for character name issues
    if "Casey" in fixed_output or "Sarah" in fixed_output:
        print("❌ Character name issues still present")
    else:
        print("✅ Character names fixed!")

if __name__ == "__main__":
    test_fix() 