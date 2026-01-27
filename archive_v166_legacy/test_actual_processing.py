#!/usr/bin/env python3
"""
Test script to simulate the actual processing flow and identify section bleeding
"""

import re

def simulate_process_query_flow():
    """Simulate the actual processing flow from process_query"""
    
    # Simulate the answer that might come from GPT
    raw_answer = """**Strategic Thinking Lens**

This strategic thinking lens focuses on optimization under uncertainty, using mathematical modeling and scenario analysis to balance efficiency with flexibility.

**Story in Action**

A manufacturing plant manager faces tariff uncertainty while optimizing production. The manager uses linear optimization models to maximize profit while considering various constraints and market conditions. The approach involves scenario analysis to prepare for different tariff outcomes.

**Follow-up Prompts**

- How does linear optimization inform your approach to balancing efficiency with flexibility?
- What trade-offs exist between your options?
- How would you handle the uncertainty in tariff rates?

**Concepts/Tools**

Linear Optimization: A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints.
Scenario Analysis: A method that explores different hypothetical futures (e.g., best-case, worst-case) to support strategic decision planning.
Risk Assessment: Systematic evaluation of potential threats and their impact on decision outcomes.
"""

    print("=== ORIGINAL RAW ANSWER ===")
    print(raw_answer)
    print("\n" + "="*50 + "\n")
    
    # Step 1: Apply enforce_thinkpal_structure
    print("=== STEP 1: enforce_thinkpal_structure ===")
    
    # Simulate the enforce_thinkpal_structure function
    def enforce_thinkpal_structure(answer: str, query: str = "") -> str:
        import re
        
        # V1.6.3: Check for the new 4-section structure
        required_headers = [
            r'Strategic Thinking Lens',
            r'Story in Action',
            r'Follow-up Prompts',
            r'Concepts/Tools'
        ]
        
        # Count how many required headers are present (case insensitive, with or without **)
        header_count = 0
        for pattern in required_headers:
            # Look for the pattern with optional ** markers and case insensitive
            flexible_pattern = r'(\*\*)?\s*' + re.escape(pattern) + r'\s*(\*\*)?'
            if re.search(flexible_pattern, answer, re.IGNORECASE):
                header_count += 1
        
        # If we have at least 3 of the 4 required headers, check Strategic Thinking Lens length
        if header_count >= 3:
            # Extract Strategic Thinking Lens section
            lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\*\*[^*]+\*\*|$)', answer, re.DOTALL | re.IGNORECASE)
            if lens_match:
                lens_content = lens_match.group(1).strip()
                word_count = len(lens_content.split())
                
                # V1.6.5: Enforce Strategic Thinking Lens length (120-160 words)
                if word_count < 120:  # Too short, replace with fallback
                    print("✨ Enhanced Strategic Thinking Lens applied (fallback upgrade)")
                    # For this test, we'll just return the original
                    pass
            
            return answer.strip()
        
        # If the GPT response doesn't have the right structure, use context-aware fallbacks
        # For this test, we'll just return the original
        return answer.strip()
    
    structured_answer = enforce_thinkpal_structure(raw_answer, "test query")
    print("After enforce_thinkpal_structure:")
    print(structured_answer)
    print("\n" + "="*50 + "\n")
    
    # Step 2: Simulate the section enhancement process
    print("=== STEP 2: Section Enhancement Process ===")
    
    # Simulate the entity enhancement process
    entities = {
        'time_periods': ['next year'],
        'quantitative_terms': ['maximize profit'],
        'stakeholders': ['plant manager'],
        'constraints': ['tariff uncertainty'],
        'risks': ['tariff uncertainty'],
        'technologies': ['linear optimization'],
        'industries': ['manufacturing'],
        'uncertainty_indicators': ['uncertainty']
    }
    
    # Simulate the enhancement functions with the FIXED versions
    def enhance_story_with_entities(story: str, entities: dict) -> str:
        """Enhance the Story in Action section with extracted entities."""
        if not entities:
            return story
        
        # Extract the content after the header
        import re
        header_match = re.search(r'\*\*Story in Action\*\*', story, re.IGNORECASE)
        if not header_match:
            return story
        
        header = story[:header_match.end()]
        content = story[header_match.end():].strip()
        
        enhanced_content = content
        
        # Add entity-specific details to the story content
        if 'time_periods' in entities:
            time_terms = ', '.join(entities['time_periods'])
            enhanced_content += f"\n\nThe timeline of {time_terms} adds urgency to the decision."
        
        if 'stakeholders' in entities:
            stakeholder_terms = ', '.join(entities['stakeholders'])
            enhanced_content += f" Multiple stakeholders including {stakeholder_terms} have competing interests."
        
        # Return the enhanced section with proper formatting
        return f"{header}\n{enhanced_content}"
    
    def enhance_followup_prompts_with_entities(prompts: str, entities: dict) -> str:
        """Enhance the Follow-up Prompts section with extracted entities."""
        if not entities:
            return prompts
        
        # Extract the content after the header
        import re
        header_match = re.search(r'\*\*Follow-up Prompts\*\*', prompts, re.IGNORECASE)
        if not header_match:
            return prompts
        
        header = prompts[:header_match.end()]
        content = prompts[header_match.end():].strip()
        
        enhanced_content = content
        
        # Add entity-specific questions to the content
        if 'technologies' in entities:
            tech_terms = ', '.join(entities['technologies'])
            enhanced_content += f"\n\nTechnology considerations: {tech_terms}"
        
        # Return the enhanced section with proper formatting
        return f"{header}\n{enhanced_content}"
    
    # Apply enhancements using the IMPROVED patterns
    if entities:
        # Enhance Story in Action
        story_pattern = r'(\*\*Story in Action\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
        story_match = re.search(story_pattern, structured_answer, re.DOTALL | re.IGNORECASE)
        if story_match:
            story_section = story_match.group(1)
            enhanced_story = enhance_story_with_entities(story_section, entities)
            structured_answer = structured_answer.replace(story_section, enhanced_story)
        
        # Enhance Follow-up Prompts
        followup_pattern = r'(\*\*Follow-up Prompts\*\*.*?)(?=\n\*\*[^*]+\*\*|$)'
        followup_match = re.search(followup_pattern, structured_answer, re.DOTALL | re.IGNORECASE)
        if followup_match:
            followup_section = followup_match.group(1)
            enhanced_followup = enhance_followup_prompts_with_entities(followup_section, entities)
            structured_answer = structured_answer.replace(followup_section, enhanced_followup)
    
    print("After entity enhancement:")
    print(structured_answer)
    print("\n" + "="*50 + "\n")
    
    # Step 3: Simulate final formatting
    print("=== STEP 3: Final Formatting ===")
    
    def format_final_output(answer: str) -> str:
        """Ensure the final output matches the frontend expected format exactly."""
        import re
        
        # Remove colons from section headers only (not from tool definitions)
        answer = re.sub(r'\*\*(How to Strategize Your Decision|Story in Action|Analytical Tools \(When Appropriate\)|Follow-up Prompts|Concepts/Tools)\*\*:', r'**\1**', answer)
        
        # Convert "Analytical Tools (When Appropriate)" to "Analytical Tools"
        answer = re.sub(r'\*\*Analytical Tools \(When Appropriate\)\*\*', r'**Analytical Tools**', answer)
        
        # Convert numbered follow-up prompts to bullet points
        answer = re.sub(r'^\d+\.\s*', '- ', answer, flags=re.MULTILINE)
        
        # Ensure proper spacing between sections
        answer = re.sub(r'\*\*(How to Strategize Your Decision|Story in Action|Analytical Tools|Follow-up Prompts|Concepts/Tools)\*\*\n', r'**\1**\n\n', answer)
        
        return answer
    
    def ensure_all_sections(markdown: str) -> str:
        required_sections = [
            "**Strategic Thinking Lens**",
            "**Story in Action**",
            "**Follow-up Prompts**",
            "**Concepts/Tools**"
        ]
        for section in required_sections:
            if section not in markdown:
                print(f"🚨 Inserting fallback for missing section: {section}")
                markdown += f"\n\n{section}\nNo content available."
        return markdown
    
    final_output = format_final_output(structured_answer.strip())
    final_output = ensure_all_sections(final_output)
    
    print("Final output:")
    print(final_output)
    print("\n" + "="*50 + "\n")
    
    # Step 4: Analyze the sections
    print("=== STEP 4: Section Analysis ===")
    
    # Extract each section to see what's happening
    sections = {
        'Strategic Thinking Lens': r'\*\*Strategic Thinking Lens\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
        'Story in Action': r'\*\*Story in Action\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
        'Follow-up Prompts': r'\*\*Follow-up Prompts\*\*.*?(?=\n\*\*[^*]+\*\*|$)',
        'Concepts/Tools': r'\*\*Concepts/Tools\*\*.*?(?=\n\*\*[^*]+\*\*|$)'
    }
    
    for section_name, pattern in sections.items():
        match = re.search(pattern, final_output, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(0)
            print(f"{section_name}:")
            print(f"Length: {len(content)}")
            print(f"Content: {repr(content[:200])}...")
            print()
        else:
            print(f"{section_name}: NOT FOUND")
            print()

if __name__ == "__main__":
    simulate_process_query_flow() 