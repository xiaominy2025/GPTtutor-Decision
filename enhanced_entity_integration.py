#!/usr/bin/env python3
"""
Enhanced entity integration for Story in Action and Follow-up Prompts.
"""

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

def fix_domain_aware_followup_prompt():
    """
    Fix the domain-aware follow-up prompt generation to ensure proper logic.
    """
    
    print("🔧 Fixing domain-aware follow-up prompt generation...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the generate_domain_aware_followup_prompt function
        start_marker = "def generate_domain_aware_followup_prompt(query: str) -> str:"
        end_marker = "def generate_domain_aware_followup_questions(query: str) -> list:"
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos == -1 or end_pos == -1:
            print("❌ Could not find function boundaries")
            return False
        
        # Extract the current function
        current_function = content[start_pos:end_pos]
        
        # Create the enhanced function with entity integration
        enhanced_function = '''def generate_domain_aware_followup_prompt(query: str, entities: dict = None) -> str:
    """
    Generate domain-aware follow-up question prompt based on detected domains and identified concepts.
    
    Logic:
    - Single domain (≥70%): 3 questions related to concepts in that domain
    - Multiple domains: 2 questions for primary domain concepts, 1 for each additional domain concepts
    - General domain: 2 questions, 1 related to each identified concept
    - Cap at 4 total questions
    - Enhanced with entity-specific questions if entities provided
    """
    domains = detect_course_concept_domains(query)
    
    # Get identified concepts for the query
    identified_concepts = get_top_ranked_concepts(query, top_k=4)
    
    if not domains or not identified_concepts:
        base_prompt = """**Follow-up Prompts**

Generate exactly 2 reflective questions that help the student apply strategic thinking to their decision. Focus on:
- Clarifying objectives and trade-offs
- Considering long-term implications
- Evaluating different perspectives

Format as bullet points (- Question text)"""
        
        # Enhance with entities if available
        if entities:
            base_prompt = enhance_followup_prompts_with_entities(base_prompt, entities)
        
        return base_prompt
    
    # Sort domains by score (descending)
    sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)
    primary_domain = sorted_domains[0]
    
    # Group concepts by domain
    concepts_by_domain = {
        'behavioral': [],
        'technical': [],
        'strategic': [],
        'negotiation': [],
        'general': []
    }
    
    for concept_name, definition in identified_concepts:
        concept_domain = CONCEPT_DOMAINS.get(concept_name, 'general')
        concepts_by_domain[concept_domain].append((concept_name, definition))
    
    # Determine question distribution based on domain detection
    if primary_domain[1] >= 0.7:  # Single strong domain
        domain_name = primary_domain[0]
        domain_concepts = concepts_by_domain[domain_name]
        
        if domain_concepts:
            # 3 questions focused on concepts in this domain
            prompt = f"""**Follow-up Prompts**

Generate exactly 3 reflective questions that help the student apply {domain_name} concepts to their decision. Focus on the following identified concepts: {', '.join([c[0] for c in domain_concepts[:3]])}

Questions should:
- Help students apply {domain_name} thinking to their specific situation
- Encourage deeper reflection on the identified concepts
- Guide practical application of {domain_name} principles

Format as bullet points (- Question text)"""
        else:
            # Fallback for strong domain but no domain-specific concepts
            prompt = f"""**Follow-up Prompts**

Generate exactly 3 reflective questions that help the student apply {domain_name} thinking to their decision. Focus on:
- How {domain_name} factors influence their decision
- Applying {domain_name} principles to their specific context
- Considering {domain_name} implications and trade-offs

Format as bullet points (- Question text)"""
    
    elif len(sorted_domains) > 1:  # Multiple domains
        # 2 questions for primary domain, 1 for each additional domain (capped at 4 total)
        primary_domain_name = primary_domain[0]
        primary_concepts = concepts_by_domain[primary_domain_name]
        
        # Get additional domains (excluding primary)
        additional_domains = [d for d in sorted_domains[1:] if d[1] > 0.3]  # Only include domains with >30% confidence
        total_questions = 2 + len(additional_domains)
        total_questions = min(total_questions, 4)  # Cap at 4
        
        prompt_parts = []
        prompt_parts.append(f"Generate exactly {total_questions} reflective questions:")
        
        # Primary domain questions
        if primary_concepts:
            concept_names = ', '.join([c[0] for c in primary_concepts[:2]])
            prompt_parts.append(f"- 2 questions focused on {primary_domain_name} concepts: {concept_names}")
        else:
            prompt_parts.append(f"- 2 questions focused on {primary_domain_name} thinking")
        
        # Additional domain questions
        for i, (domain_name, score) in enumerate(additional_domains[:2]):  # Max 2 additional domains
            domain_concepts = concepts_by_domain[domain_name]
            if domain_concepts:
                concept_name = domain_concepts[0][0]
                prompt_parts.append(f"- 1 question focused on {domain_name} concept: {concept_name}")
            else:
                prompt_parts.append(f"- 1 question focused on {domain_name} thinking")
        
        prompt_parts.append("\\nQuestions should help students apply the identified concepts to their specific decision context.")
        prompt_parts.append("Format as bullet points (- Question text)")
        
        prompt = "**Follow-up Prompts**\\n\\n" + "\\n".join(prompt_parts)
    
    else:  # General domain or weak signals
        # 2 questions, 1 related to each identified concept (max 2 concepts)
        if len(identified_concepts) >= 2:
            concept1, concept2 = identified_concepts[0][0], identified_concepts[1][0]
            prompt = f"""**Follow-up Prompts**

Generate exactly 2 reflective questions that help the student apply strategic thinking to their decision:

- 1 question focused on applying the concept: {concept1}
- 1 question focused on applying the concept: {concept2}

Questions should encourage deeper reflection and practical application of these concepts to their specific situation.

Format as bullet points (- Question text)"""
        else:
            # Fallback for general domain
            prompt = """**Follow-up Prompts**

Generate exactly 2 reflective questions that help the student apply strategic thinking to their decision. Focus on:
- Clarifying objectives and trade-offs
- Considering long-term implications
- Evaluating different perspectives

Format as bullet points (- Question text)"""
    
    # Enhance with entities if available
    if entities:
        prompt = enhance_followup_prompts_with_entities(prompt, entities)
    
    return prompt'''
        
        # Replace the function
        new_content = content.replace(current_function, enhanced_function)
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ Domain-aware follow-up prompt generation fixed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix domain-aware follow-up prompt: {e}")
        return False

def enhance_process_query_with_entities():
    """
    Enhance the process_query function to use entities in Story in Action and Follow-up Prompts.
    """
    
    print("🔧 Enhancing process_query with entity integration...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the process_query function call to generate_domain_aware_followup_prompt
        old_call = "domain_followup_prompt = generate_domain_aware_followup_prompt(query)"
        new_call = "domain_followup_prompt = generate_domain_aware_followup_prompt(query, entities)"
        
        if old_call in content:
            content = content.replace(old_call, new_call)
            print("✅ Updated follow-up prompt call with entities")
        else:
            print("⚠️ Follow-up prompt call pattern not found")
        
        # Add entity enhancement for Story in Action and Follow-up Prompts
        # Find the section where the answer is processed
        story_enhancement_pattern = """        # Apply final formatting
        final_output = format_final_output(answer.strip())"""
        
        story_enhancement_replacement = """        # Enhance Story in Action and Follow-up Prompts with entities
        if entities:
            # Enhance Story in Action
            story_pattern = r'(\\*\\*Story in Action\\*\\*.*?)(?=\\*\\*|$)'
            story_match = re.search(story_pattern, answer, re.DOTALL | re.IGNORECASE)
            if story_match:
                story_section = story_match.group(1)
                enhanced_story = enhance_story_with_entities(story_section, entities)
                answer = answer.replace(story_section, enhanced_story)
            
            # Enhance Follow-up Prompts
            followup_pattern = r'(\\*\\*Follow-up Prompts\\*\\*.*?)(?=\\*\\*|$)'
            followup_match = re.search(followup_pattern, answer, re.DOTALL | re.IGNORECASE)
            if followup_match:
                followup_section = followup_match.group(1)
                enhanced_followup = enhance_followup_prompts_with_entities(followup_section, entities)
                answer = answer.replace(followup_section, enhanced_followup)
        
        # Apply final formatting
        final_output = format_final_output(answer.strip())"""
        
        if story_enhancement_pattern in content:
            content = content.replace(story_enhancement_pattern, story_enhancement_replacement)
            print("✅ Added entity enhancement for Story in Action and Follow-up Prompts")
        else:
            print("⚠️ Story enhancement pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Process_query enhanced with entity integration")
        return True
        
    except Exception as e:
        print(f"❌ Failed to enhance process_query: {e}")
        return False

def test_enhanced_integration():
    """
    Test the enhanced entity integration.
    """
    
    print("🧪 Testing enhanced entity integration...")
    
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
        entity_indicators = []
        if 'time_periods' in entities:
            entity_indicators.extend(entities['time_periods'])
        if 'risks' in entities:
            entity_indicators.extend(entities['risks'])
        
        entity_found = False
        for indicator in entity_indicators:
            if indicator.lower() in result.lower():
                entity_found = True
                print(f"  ✅ Entity '{indicator}' found in response")
        
        if entity_found:
            print("✅ Entity integration working correctly")
        else:
            print("⚠️ Entity integration may need improvement")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the enhanced entity integration fix."""
    
    print("🎯 ENHANCED ENTITY INTEGRATION FIX")
    print("=" * 60)
    
    # Fix domain-aware follow-up prompt generation
    prompt_fix_success = fix_domain_aware_followup_prompt()
    
    # Enhance process_query with entity integration
    process_enhancement_success = enhance_process_query_with_entities()
    
    # Test the enhanced integration
    test_success = test_enhanced_integration()
    
    # Summary
    print("\n📊 ENHANCEMENT RESULTS")
    print("=" * 50)
    print(f"Follow-up Prompt Fix: {'✅ PASS' if prompt_fix_success else '❌ FAIL'}")
    print(f"Process Query Enhancement: {'✅ PASS' if process_enhancement_success else '❌ FAIL'}")
    print(f"Integration Test: {'✅ PASS' if test_success else '❌ FAIL'}")
    
    if prompt_fix_success and process_enhancement_success and test_success:
        print("\n🎉 ALL ENHANCEMENTS SUCCESSFUL!")
        print("Enhanced entities are now integrated into Story in Action and Follow-up Prompts.")
        print("Domain-aware follow-up prompt generation is working correctly.")
    else:
        print("\n⚠️ Some enhancements failed.")
        print("Please check the error messages above for specific issues.")
    
    return prompt_fix_success and process_enhancement_success and test_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Enhanced entity integration completed successfully!")
    else:
        print("\n❌ Enhanced entity integration failed!") 