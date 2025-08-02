#!/usr/bin/env python3
"""
Add missing entity enhancement functions to query_engine.py
"""

def add_missing_functions():
    """Add the missing entity enhancement functions to query_engine.py."""
    
    print("🔧 Adding missing entity enhancement functions...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add the missing functions before the enhance_strategic_lens_with_entities function
        functions_to_add = '''
def enhance_story_with_entities(story: str, entities: dict) -> str:
    """
    Enhance the Story in Action section with extracted entities.
    
    Args:
        story: Original story text
        entities: Extracted entities dictionary
    
    Returns:
        Enhanced story with entity-specific details
    """
    if not entities:
        return story
    
    enhanced_story = story
    
    # Add entity-specific details to the story
    if 'time_periods' in entities:
        time_terms = ', '.join(entities['time_periods'])
        enhanced_story += f" The timeline of {time_terms} adds urgency to the decision."
    
    if 'quantitative_terms' in entities:
        quant_terms = ', '.join(entities['quantitative_terms'])
        enhanced_story += f" The specific metrics of {quant_terms} provide concrete benchmarks."
    
    if 'stakeholders' in entities:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        enhanced_story += f" Multiple stakeholders including {stakeholder_terms} have competing interests."
    
    if 'constraints' in entities:
        constraint_terms = ', '.join(entities['constraints'])
        enhanced_story += f" Operational constraints like {constraint_terms} limit the available options."
    
    if 'risks' in entities:
        risk_terms = ', '.join(entities['risks'])
        enhanced_story += f" The presence of {risk_terms} creates uncertainty in the decision environment."
    
    if 'technologies' in entities:
        tech_terms = ', '.join(entities['technologies'])
        enhanced_story += f" The integration of {tech_terms} introduces both opportunities and challenges."
    
    if 'industries' in entities:
        industry_terms = ', '.join(entities['industries'])
        enhanced_story += f" The {industry_terms} context shapes the competitive landscape."
    
    if 'locations' in entities:
        location_terms = ', '.join(entities['locations'])
        enhanced_story += f" Geographic factors in {location_terms} influence the strategic options."
    
    return enhanced_story

def enhance_followup_prompts_with_entities(prompts: str, entities: dict) -> str:
    """
    Enhance the Follow-up Prompts section with extracted entities.
    
    Args:
        prompts: Original follow-up prompts text
        entities: Extracted entities dictionary
    
    Returns:
        Enhanced follow-up prompts with entity-specific questions
    """
    if not entities:
        return prompts
    
    enhanced_prompts = prompts
    
    # Add entity-specific follow-up questions
    entity_questions = []
    
    if 'time_periods' in entities:
        time_terms = ', '.join(entities['time_periods'])
        entity_questions.append(f"- How does the {time_terms} timeline affect your decision priorities?")
    
    if 'quantitative_terms' in entities:
        quant_terms = ', '.join(entities['quantitative_terms'])
        entity_questions.append(f"- What specific {quant_terms} metrics would help you evaluate your options?")
    
    if 'stakeholders' in entities:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        entity_questions.append(f"- How might {stakeholder_terms} influence or be affected by your decision?")
    
    if 'constraints' in entities:
        constraint_terms = ', '.join(entities['constraints'])
        entity_questions.append(f"- How can you work within the {constraint_terms} constraints while achieving your goals?")
    
    if 'risks' in entities:
        risk_terms = ', '.join(entities['risks'])
        entity_questions.append(f"- What strategies can you develop to mitigate the {risk_terms} risks?")
    
    if 'technologies' in entities:
        tech_terms = ', '.join(entities['technologies'])
        entity_questions.append(f"- How might {tech_terms} create new opportunities or challenges for your decision?")
    
    if 'industries' in entities:
        industry_terms = ', '.join(entities['industries'])
        entity_questions.append(f"- How does the {industry_terms} context shape your competitive positioning?")
    
    if 'locations' in entities:
        location_terms = ', '.join(entities['locations'])
        entity_questions.append(f"- What geographic factors in {location_terms} should influence your strategic approach?")
    
    # Add entity-specific questions to the prompts
    if entity_questions:
        # Find the end of the existing prompts and add entity questions
        if "Format as bullet points" in enhanced_prompts:
            # Insert before the format instruction
            enhanced_prompts = enhanced_prompts.replace(
                "Format as bullet points",
                "\n".join(entity_questions) + "\n\nFormat as bullet points"
            )
        else:
            # Add at the end
            enhanced_prompts += "\n\n" + "\n".join(entity_questions)
    
    return enhanced_prompts

'''
        
        # Find the position to insert the functions (before enhance_strategic_lens_with_entities)
        insert_marker = "def enhance_strategic_lens_with_entities(strategic_lens: str, entities: dict) -> str:"
        insert_pos = content.find(insert_marker)
        
        if insert_pos != -1:
            # Insert the functions before the marker
            new_content = content[:insert_pos] + functions_to_add + content[insert_pos:]
            
            # Write the fixed content back
            with open("query_engine.py", "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("✅ Missing functions added successfully")
            return True
        else:
            print("❌ Could not find insertion point")
            return False
        
    except Exception as e:
        print(f"❌ Failed to add missing functions: {e}")
        return False

def test_fixed_query_engine():
    """Test the fixed query engine."""
    
    print("\n🧪 Testing fixed query engine...")
    
    try:
        from query_engine import process_query, extract_enhanced_entities
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        # Extract entities
        entities = extract_enhanced_entities(test_query)
        print(f"Extracted entities: {entities}")
        
        # Process query
        result = process_query(test_query)
        print(f"✅ Query processing successful!")
        print(f"Result length: {len(result)} characters")
        
        # Check for entity-specific content
        if 'year' in result.lower() or 'uncertainty' in result.lower():
            print("✅ Entity-specific content found in response")
        else:
            print("⚠️ Entity-specific content may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the missing functions fix."""
    
    print("🎯 ADDING MISSING ENTITY ENHANCEMENT FUNCTIONS")
    print("=" * 60)
    
    # Add missing functions
    add_success = add_missing_functions()
    
    if add_success:
        # Test the fix
        test_success = test_fixed_query_engine()
        
        if test_success:
            print("\n🎉 SUCCESS: Missing functions added and tested!")
            print("The query engine should now work correctly with entity enhancement.")
        else:
            print("\n⚠️ Functions added but test failed. Additional investigation needed.")
    else:
        print("\n❌ Failed to add missing functions.")
    
    return add_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Missing functions fix completed successfully!")
    else:
        print("\n❌ Missing functions fix failed!") 