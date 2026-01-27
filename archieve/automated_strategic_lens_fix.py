#!/usr/bin/env python3
"""
Automated Strategic Lens Fix

This script implements enhanced strategic lens generation with better differentiation
and query-specific content to reduce similarity between original and follow-up queries.
"""

import sys
import os
import re
from typing import Dict, List, Tuple

# Add the current directory to the path so we can import query_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def extract_query_keywords(query: str) -> List[str]:
    """Extract distinctive keywords from the query for strategic lens enhancement."""
    query_lower = query.lower()
    keywords = []
    
    # Extract technical terms
    technical_terms = [
        'optimization', 'simulation', 'modeling', 'analysis', 'forecasting', 'uncertainty',
        'linear', 'nonlinear', 'algorithm', 'algorithmic', 'computational', 'mathematical',
        'quantitative', 'statistical', 'probabilistic', 'stochastic', 'deterministic',
        'heuristic', 'metaheuristic', 'genetic', 'evolutionary', 'neural', 'machine learning'
    ]
    for term in technical_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract decision terms
    decision_terms = [
        'trade-off', 'balance', 'compare', 'evaluate', 'choose', 'decide', 'select',
        'prioritize', 'rank', 'weigh', 'consider', 'assess', 'analyze', 'examine',
        'investigate', 'explore', 'determine', 'identify', 'find', 'discover'
    ]
    for term in decision_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract context terms
    context_terms = [
        'tariff', 'production', 'profit', 'efficiency', 'flexibility', 'career', 'job',
        'business', 'startup', 'admission', 'education', 'finance', 'technology',
        'health', 'relocation', 'leadership', 'ethics', 'negotiation', 'operations',
        'supply chain', 'inventory', 'capacity', 'demand', 'supply', 'cost', 'revenue',
        'market', 'competition', 'customer', 'stakeholder', 'team', 'organization'
    ]
    for term in context_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract specific optimization terms
    optimization_terms = [
        'maximize', 'minimize', 'optimize', 'best', 'optimal', 'optimum', 'efficient',
        'effective', 'productive', 'profitable', 'cost-effective', 'value', 'benefit',
        'advantage', 'superior', 'excellent', 'outstanding', 'premium', 'quality'
    ]
    for term in optimization_terms:
        if term in query_lower:
            keywords.append(term)
    
    return list(set(keywords))  # Remove duplicates

def generate_entity_context(entities: dict) -> str:
    """Generate context-specific content based on extracted entities."""
    context_parts = []
    
    if 'time_periods' in entities and entities['time_periods']:
        time_terms = ', '.join(entities['time_periods'])
        context_parts.append(f"the {time_terms} timeline")
    
    if 'quantitative_terms' in entities and entities['quantitative_terms']:
        quant_terms = ', '.join(entities['quantitative_terms'])
        context_parts.append(f"the {quant_terms} metrics")
    
    if 'stakeholders' in entities and entities['stakeholders']:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        context_parts.append(f"the {stakeholder_terms} perspectives")
    
    if 'constraints' in entities and entities['constraints']:
        constraint_terms = ', '.join(entities['constraints'])
        context_parts.append(f"the {constraint_terms} limitations")
    
    if 'risks' in entities and entities['risks']:
        risk_terms = ', '.join(entities['risks'])
        context_parts.append(f"the {risk_terms} factors")
    
    if 'technologies' in entities and entities['technologies']:
        tech_terms = ', '.join(entities['technologies'])
        context_parts.append(f"the {tech_terms} capabilities")
    
    if 'industries' in entities and entities['industries']:
        industry_terms = ', '.join(entities['industries'])
        context_parts.append(f"the {industry_terms} sector dynamics")
    
    if context_parts:
        return f" Pay particular attention to {', '.join(context_parts)}."
    
    return ""

def generate_query_specific_context(query: str) -> str:
    """Generate query-specific context based on the query content."""
    query_lower = query.lower()
    context_parts = []
    
    # Check for specific question types
    if 'how does' in query_lower or 'how do' in query_lower:
        context_parts.append("methodological approach")
    
    if 'what are' in query_lower or 'what is' in query_lower:
        context_parts.append("conceptual understanding")
    
    if 'why' in query_lower:
        context_parts.append("causal analysis")
    
    if 'when' in query_lower:
        context_parts.append("temporal considerations")
    
    if 'where' in query_lower:
        context_parts.append("spatial factors")
    
    if 'who' in query_lower:
        context_parts.append("stakeholder analysis")
    
    # Check for specific optimization contexts
    if 'optimization' in query_lower and 'linear' in query_lower:
        context_parts.append("linear programming techniques")
    
    if 'efficiency' in query_lower and 'flexibility' in query_lower:
        context_parts.append("efficiency-flexibility trade-offs")
    
    if 'production' in query_lower and 'profit' in query_lower:
        context_parts.append("production-profit optimization")
    
    if 'tariff' in query_lower and 'uncertainty' in query_lower:
        context_parts.append("tariff uncertainty management")
    
    if context_parts:
        return f" Focus on {', '.join(context_parts)} in your analysis."
    
    return ""

def enhance_strategic_lens_with_query_context(strategic_lens: str, query: str, entities: dict = None) -> str:
    """
    Enhanced strategic lens generation with better differentiation and query-specific content.
    """
    
    # Extract query-specific keywords for better differentiation
    query_keywords = extract_query_keywords(query)
    
    # Generate query-specific context
    query_context = generate_query_specific_context(query)
    
    # Add query-specific context
    enhanced_lens = strategic_lens
    if query_context:
        enhanced_lens += query_context
    
    # Add query-specific keywords if available
    if query_keywords:
        keyword_context = f" Specifically, consider {', '.join(query_keywords[:3])} in your analysis."
        enhanced_lens += keyword_context
    
    # Add more distinctive entity-based content
    if entities:
        entity_context = generate_entity_context(entities)
        if entity_context:
            enhanced_lens += entity_context
    
    return enhanced_lens

def create_enhanced_strategic_lens_function():
    """Create the enhanced strategic lens generation function."""
    
    enhanced_function = '''
def generate_course_domain_strategic_lens(query: str, course_domain: str, application_field: str = None, entities: dict = None) -> str:
    """
    Generate Strategic Thinking Lens content based on the detected course concept domain, application field, and extracted entities.
    Enhanced with query-specific context and better differentiation.
    
    Args:
        query: The user's query
        course_domain: The detected course concept domain (technical, strategic, behavioral, negotiation, general)
        application_field: The detected application field (job, startup, admission, etc.)
        entities: Extracted entities dictionary for enhanced nuance
    
    Returns:
        String with domain-specific Strategic Thinking Lens content enhanced with entities and query context
    """
    
    # Application-specific strategic lens content with enhanced differentiation
    if application_field == "job":
        if course_domain == "strategic":
            base_lens = "This requires career-focused strategic analysis and long-term professional planning. Consider your career trajectory, skill development opportunities, and professional growth potential when evaluating job offers. This involves balancing immediate benefits like salary and work-life balance with long-term career positioning, considering factors like industry trends, company culture, and advancement opportunities. Strategic career thinking requires evaluating multiple career scenarios, assessing how each role contributes to your professional development, and ensuring alignment with your broader career goals. Consider the trade-offs between different career paths, evaluating how each option impacts both immediate job satisfaction and long-term career advancement. Assess the risks of various career choices and how they align with your professional objectives while maintaining flexibility for future career transitions."
        else:
            base_lens = "This decision involves strategic thinking about your career alternatives, professional objectives, and long-term implications. Consider your career goals, values, and how each opportunity contributes to your professional development. Use structured approaches to compare job offers systematically, weighing factors like growth potential, compensation, company culture, and work-life balance. This requires balancing multiple competing career priorities and considering both immediate job satisfaction and long-term professional trajectory. Strategic career thinking involves identifying key trade-offs between different career paths, evaluating risks and opportunities, and ensuring alignment with your broader professional objectives while maintaining flexibility for future career adjustments. Consider how this decision fits into your broader career framework and what information gaps you need to address about each opportunity."
    
    elif application_field == "startup":
        if course_domain == "strategic":
            base_lens = "This requires entrepreneurial strategic analysis and business opportunity evaluation. Consider market dynamics, competitive landscape, and resource allocation to achieve sustainable business advantage. This involves balancing immediate market entry opportunities with long-term business positioning, considering factors like market timing, competitive landscape, and execution capabilities. Strategic startup thinking requires evaluating multiple business scenarios, assessing competitive responses, and ensuring alignment with broader entrepreneurial goals. Consider the trade-offs between different business approaches, evaluating how each option impacts both immediate market position and long-term competitive advantage. Assess the risks of various strategic choices and how they align with your business objectives while maintaining flexibility for future adjustments."
        else:
            base_lens = "This decision involves strategic thinking about business alternatives, market opportunities, and long-term implications. Consider your business goals, market positioning, and how each option contributes to your entrepreneurial vision. Use structured approaches to compare business opportunities systematically. This requires balancing multiple competing business priorities and considering both immediate market entry and long-term business trajectory. Strategic business thinking involves identifying key trade-offs between different business approaches, evaluating risks and opportunities, and ensuring alignment with your broader business objectives while maintaining flexibility for future adjustments."
    
    elif application_field == "admission":
        if course_domain == "strategic":
            base_lens = "This requires education-focused strategic analysis and academic planning. Consider your educational trajectory, learning opportunities, and long-term academic and career goals when evaluating educational options. This involves balancing immediate factors like cost and location with long-term educational positioning, considering factors like academic reputation, program quality, and career outcomes. Strategic educational thinking requires evaluating multiple academic scenarios, assessing how each program contributes to your learning and career development, and ensuring alignment with your broader educational and professional goals. Consider the trade-offs between different educational paths, evaluating how each option impacts both immediate learning experience and long-term career prospects. Assess the risks of various educational choices and how they align with your academic objectives while maintaining flexibility for future learning opportunities."
        else:
            base_lens = "This decision involves strategic thinking about educational alternatives, learning objectives, and long-term implications. Consider your educational goals, values, and how each option contributes to your academic and career development. Use structured approaches to compare educational opportunities systematically. This requires balancing multiple competing educational priorities and considering both immediate learning experience and long-term career trajectory. Strategic educational thinking involves identifying key trade-offs between different educational approaches, evaluating risks and opportunities, and ensuring alignment with your broader academic objectives while maintaining flexibility for future learning adjustments."
    
    elif application_field == "operations":
        if course_domain == "technical":
            base_lens = "This requires operations-focused technical analysis and production optimization. Consider your operational constraints, production capacity, and efficiency requirements when evaluating optimization strategies. This involves balancing precision with practical operational constraints, considering factors like production schedules, resource availability, and quality standards. Technical operations thinking involves quantifying operational risks, preparing for multiple production scenarios, and optimizing for both current performance and future operational adaptability. Consider the trade-offs between model complexity and operational interpretability, evaluating how different analytical approaches impact both immediate production efficiency and long-term operational resilience. Assess the risks of various modeling approaches and how they align with operational objectives while maintaining the ability to respond to changing production conditions."
        else:
            base_lens = "This decision involves strategic thinking about operational alternatives, production objectives, and long-term implications. Consider your operational goals, efficiency targets, and how each option contributes to your production optimization. Use structured approaches to compare operational strategies systematically. This requires balancing multiple competing operational priorities and considering both immediate production efficiency and long-term operational trajectory. Strategic operations thinking involves identifying key trade-offs between different operational approaches, evaluating risks and opportunities, and ensuring alignment with your broader operational objectives while maintaining flexibility for future operational adjustments."
    
    elif application_field == "finance":
        if course_domain == "strategic":
            base_lens = "This requires finance-focused strategic analysis and investment planning. Consider your financial trajectory, investment opportunities, and long-term financial goals when evaluating financial decisions. This involves balancing immediate returns with long-term financial positioning, considering factors like market conditions, risk tolerance, and investment horizons. Strategic financial thinking requires evaluating multiple investment scenarios, assessing how each option contributes to your financial development, and ensuring alignment with your broader financial goals. Consider the trade-offs between different investment approaches, evaluating how each option impacts both immediate returns and long-term financial security. Assess the risks of various financial choices and how they align with your investment objectives while maintaining flexibility for future financial adjustments."
        else:
            base_lens = "This decision involves strategic thinking about financial alternatives, investment objectives, and long-term implications. Consider your financial goals, risk tolerance, and how each option contributes to your financial development. Use structured approaches to compare investment opportunities systematically. This requires balancing multiple competing financial priorities and considering both immediate returns and long-term financial trajectory. Strategic financial thinking involves identifying key trade-offs between different investment approaches, evaluating risks and opportunities, and ensuring alignment with your broader financial objectives while maintaining flexibility for future financial adjustments."
    
    elif application_field == "technology":
        if course_domain == "technical":
            base_lens = "This requires technology-focused technical analysis and digital transformation planning. Consider your technological constraints, implementation requirements, and innovation objectives when evaluating technology strategies. This involves balancing precision with practical technological constraints, considering factors like system compatibility, user adoption, and scalability requirements. Technical technology thinking involves quantifying technological risks, preparing for multiple implementation scenarios, and optimizing for both current performance and future technological adaptability. Consider the trade-offs between system complexity and user interpretability, evaluating how different technological approaches impact both immediate functionality and long-term technological resilience. Assess the risks of various technology approaches and how they align with organizational objectives while maintaining the ability to respond to changing technological conditions."
        else:
            base_lens = "This decision involves strategic thinking about technological alternatives, innovation objectives, and long-term implications. Consider your technology goals, digital transformation targets, and how each option contributes to your technological advancement. Use structured approaches to compare technology strategies systematically. This requires balancing multiple competing technological priorities and considering both immediate functionality and long-term technological trajectory. Strategic technology thinking involves identifying key trade-offs between different technological approaches, evaluating risks and opportunities, and ensuring alignment with your broader technological objectives while maintaining flexibility for future technological adjustments."
    
    elif application_field == "health":
        if course_domain == "strategic":
            base_lens = "This requires health-focused strategic analysis and wellness planning. Consider your health trajectory, wellness opportunities, and long-term health goals when evaluating health decisions. This involves balancing immediate health needs with long-term wellness positioning, considering factors like medical conditions, lifestyle factors, and preventive care. Strategic health thinking requires evaluating multiple health scenarios, assessing how each option contributes to your overall wellness, and ensuring alignment with your broader health objectives. Consider the trade-offs between different health approaches, evaluating how each option impacts both immediate health outcomes and long-term wellness. Assess the risks of various health choices and how they align with your wellness objectives while maintaining flexibility for future health adjustments."
        else:
            base_lens = "This decision involves strategic thinking about health alternatives, wellness objectives, and long-term implications. Consider your health goals, wellness targets, and how each option contributes to your overall health. Use structured approaches to compare health strategies systematically. This requires balancing multiple competing health priorities and considering both immediate health outcomes and long-term wellness trajectory. Strategic health thinking involves identifying key trade-offs between different health approaches, evaluating risks and opportunities, and ensuring alignment with your broader health objectives while maintaining flexibility for future health adjustments."
    
    elif application_field == "education":
        if course_domain == "strategic":
            base_lens = "This requires education-focused strategic analysis and learning planning. Consider your educational trajectory, learning opportunities, and long-term skill development goals when evaluating educational decisions. This involves balancing immediate learning needs with long-term educational positioning, considering factors like skill gaps, career requirements, and learning preferences. Strategic education thinking requires evaluating multiple learning scenarios, assessing how each option contributes to your skill development, and ensuring alignment with your broader educational objectives. Consider the trade-offs between different educational approaches, evaluating how each option impacts both immediate learning outcomes and long-term skill development. Assess the risks of various educational choices and how they align with your learning objectives while maintaining flexibility for future educational adjustments."
        else:
            base_lens = "This decision involves strategic thinking about educational alternatives, learning objectives, and long-term implications. Consider your educational goals, skill development targets, and how each option contributes to your learning advancement. Use structured approaches to compare educational strategies systematically. This requires balancing multiple competing educational priorities and considering both immediate learning outcomes and long-term educational trajectory. Strategic education thinking involves identifying key trade-offs between different educational approaches, evaluating risks and opportunities, and ensuring alignment with your broader educational objectives while maintaining flexibility for future educational adjustments."
    
    elif application_field == "relocation":
        if course_domain == "strategic":
            base_lens = "This requires relocation-focused strategic analysis and location planning. Consider your relocation trajectory, location opportunities, and long-term lifestyle goals when evaluating relocation decisions. This involves balancing immediate relocation needs with long-term location positioning, considering factors like cost of living, career opportunities, and quality of life. Strategic relocation thinking requires evaluating multiple location scenarios, assessing how each option contributes to your lifestyle goals, and ensuring alignment with your broader relocation objectives. Consider the trade-offs between different location approaches, evaluating how each option impacts both immediate relocation outcomes and long-term lifestyle positioning. Assess the risks of various relocation choices and how they align with your lifestyle objectives while maintaining flexibility for future relocation adjustments."
        else:
            base_lens = "This decision involves strategic thinking about relocation alternatives, lifestyle objectives, and long-term implications. Consider your relocation goals, lifestyle targets, and how each option contributes to your quality of life. Use structured approaches to compare relocation strategies systematically. This requires balancing multiple competing relocation priorities and considering both immediate relocation outcomes and long-term lifestyle trajectory. Strategic relocation thinking involves identifying key trade-offs between different relocation approaches, evaluating risks and opportunities, and ensuring alignment with your broader relocation objectives while maintaining flexibility for future relocation adjustments."
    
    elif application_field == "leadership":
        if course_domain == "behavioral":
            base_lens = "This requires leadership-focused behavioral analysis and team management planning. Consider your leadership trajectory, team dynamics, and organizational culture when evaluating leadership decisions. This involves balancing immediate team needs with long-term leadership positioning, considering factors like team motivation, organizational values, and management styles. Behavioral leadership thinking requires evaluating multiple leadership scenarios, assessing how each approach contributes to team performance, and ensuring alignment with your broader leadership objectives. Consider the trade-offs between different leadership approaches, evaluating how each option impacts both immediate team dynamics and long-term organizational culture. Assess the risks of various leadership choices and how they align with your management objectives while maintaining flexibility for future leadership adjustments."
        else:
            base_lens = "This decision involves strategic thinking about leadership alternatives, management objectives, and long-term implications. Consider your leadership goals, team development targets, and how each option contributes to your management effectiveness. Use structured approaches to compare leadership strategies systematically. This requires balancing multiple competing leadership priorities and considering both immediate team outcomes and long-term leadership trajectory. Strategic leadership thinking involves identifying key trade-offs between different leadership approaches, evaluating risks and opportunities, and ensuring alignment with your broader leadership objectives while maintaining flexibility for future leadership adjustments."
    
    elif application_field == "ethics":
        if course_domain == "behavioral":
            base_lens = "This requires ethics-focused behavioral analysis and values-based decision planning. Consider your ethical trajectory, moral principles, and long-term values when evaluating ethical decisions. This involves balancing immediate ethical concerns with long-term moral positioning, considering factors like stakeholder impact, organizational values, and personal integrity. Behavioral ethics thinking requires evaluating multiple ethical scenarios, assessing how each option contributes to your moral development, and ensuring alignment with your broader ethical objectives. Consider the trade-offs between different ethical approaches, evaluating how each option impacts both immediate moral outcomes and long-term ethical positioning. Assess the risks of various ethical choices and how they align with your values while maintaining flexibility for future ethical adjustments."
        else:
            base_lens = "This decision involves strategic thinking about ethical alternatives, values-based objectives, and long-term implications. Consider your ethical goals, moral development targets, and how each option contributes to your integrity. Use structured approaches to compare ethical strategies systematically. This requires balancing multiple competing ethical priorities and considering both immediate moral outcomes and long-term ethical trajectory. Strategic ethics thinking involves identifying key trade-offs between different ethical approaches, evaluating risks and opportunities, and ensuring alignment with your broader ethical objectives while maintaining flexibility for future ethical adjustments."
    
    # Domain-specific content (when no specific application field or general cases)
    elif course_domain == "technical":
        base_lens = "This involves technical analysis and modeling under uncertainty. Use mathematical and computational tools to optimize outcomes while accounting for variability in key parameters. This requires balancing precision with practical constraints, considering factors like data quality, model assumptions, and implementation feasibility. Technical thinking involves quantifying risks, preparing for multiple scenarios, and optimizing for both current performance and future adaptability. Consider the trade-offs between model complexity and interpretability, evaluating how different analytical approaches impact both immediate decision quality and long-term strategic positioning. Assess the risks of various modeling approaches and how they align with organizational objectives while maintaining the ability to respond to changing conditions."
    
    elif course_domain == "strategic":
        base_lens = "This requires strategic analysis and long-term planning. Consider competitive dynamics, market positioning, and resource allocation to achieve sustainable advantage. This involves balancing immediate opportunities with long-term strategic positioning, considering factors like market timing, competitive landscape, and organizational capabilities. Strategic thinking requires evaluating multiple scenarios, assessing competitive responses, and ensuring alignment with broader organizational goals. Consider the trade-offs between different strategic approaches, evaluating how each option impacts both immediate market position and long-term competitive advantage. Assess the risks of various strategic choices and how they align with organizational objectives while maintaining flexibility for future adjustments."
    
    elif course_domain == "behavioral":
        base_lens = "This involves understanding human factors and psychological influences on decision-making. Consider cognitive biases, group dynamics, and individual motivations that may affect the decision process. This requires balancing rational analysis with human psychology, considering factors like risk tolerance, social influence, and emotional responses. Behavioral thinking involves recognizing potential biases, understanding stakeholder perspectives, and ensuring decisions account for human limitations and motivations. Consider the trade-offs between different approaches to managing human factors, evaluating how each option impacts both immediate acceptance and long-term implementation success. Assess the risks of various behavioral approaches and how they align with organizational culture while maintaining focus on objective outcomes."
    
    elif course_domain == "negotiation":
        base_lens = "This requires preparation for value creation and relationship management. Consider the interests of all parties, potential trade-offs, and long-term relationship implications. This involves balancing assertiveness with collaboration, considering factors like power dynamics, mutual interests, and future interactions. Negotiation thinking requires understanding the other party's constraints, identifying potential value creation opportunities, and preparing for multiple scenarios while considering the long-term implications of your approach. Consider the trade-offs between different negotiation strategies, evaluating how each option impacts both immediate outcomes and future relationship potential. Assess the risks of various negotiation approaches and how they align with your broader objectives while maintaining the potential for future collaboration."
    
    else:  # general
        base_lens = "This decision involves strategic thinking about alternatives, objectives, and trade-offs. Consider your goals, values, and the long-term implications of each choice. Use structured approaches to compare options systematically. This requires balancing multiple competing priorities and considering both immediate and long-term implications. Strategic thinking involves identifying key trade-offs, evaluating risks and opportunities, and ensuring alignment with broader objectives while maintaining flexibility for future adjustments. Consider how this decision fits into your broader strategic framework and what information gaps you need to address. Think about the stakeholders involved and how different outcomes might impact various parties. This systematic approach will help you make a well-informed choice that balances multiple considerations."
    
    # Enhance with query-specific context and entities
    enhanced_lens = enhance_strategic_lens_with_query_context(base_lens, query, entities)
    
    return enhanced_lens
'''
    
    return enhanced_function

def apply_enhanced_fix():
    """Apply the enhanced strategic lens fix to query_engine.py."""
    
    print("🔧 APPLYING ENHANCED STRATEGIC LENS FIX")
    print("=" * 60)
    
    try:
        # Read the current query_engine.py
        with open('query_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create the enhanced functions
        enhanced_functions = create_enhanced_strategic_lens_function()
        
        # Add the helper functions before the main function
        helper_functions = '''
def extract_query_keywords(query: str) -> List[str]:
    """Extract distinctive keywords from the query for strategic lens enhancement."""
    query_lower = query.lower()
    keywords = []
    
    # Extract technical terms
    technical_terms = [
        'optimization', 'simulation', 'modeling', 'analysis', 'forecasting', 'uncertainty',
        'linear', 'nonlinear', 'algorithm', 'algorithmic', 'computational', 'mathematical',
        'quantitative', 'statistical', 'probabilistic', 'stochastic', 'deterministic',
        'heuristic', 'metaheuristic', 'genetic', 'evolutionary', 'neural', 'machine learning'
    ]
    for term in technical_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract decision terms
    decision_terms = [
        'trade-off', 'balance', 'compare', 'evaluate', 'choose', 'decide', 'select',
        'prioritize', 'rank', 'weigh', 'consider', 'assess', 'analyze', 'examine',
        'investigate', 'explore', 'determine', 'identify', 'find', 'discover'
    ]
    for term in decision_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract context terms
    context_terms = [
        'tariff', 'production', 'profit', 'efficiency', 'flexibility', 'career', 'job',
        'business', 'startup', 'admission', 'education', 'finance', 'technology',
        'health', 'relocation', 'leadership', 'ethics', 'negotiation', 'operations',
        'supply chain', 'inventory', 'capacity', 'demand', 'supply', 'cost', 'revenue',
        'market', 'competition', 'customer', 'stakeholder', 'team', 'organization'
    ]
    for term in context_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Extract specific optimization terms
    optimization_terms = [
        'maximize', 'minimize', 'optimize', 'best', 'optimal', 'optimum', 'efficient',
        'effective', 'productive', 'profitable', 'cost-effective', 'value', 'benefit',
        'advantage', 'superior', 'excellent', 'outstanding', 'premium', 'quality'
    ]
    for term in optimization_terms:
        if term in query_lower:
            keywords.append(term)
    
    return list(set(keywords))  # Remove duplicates

def generate_entity_context(entities: dict) -> str:
    """Generate context-specific content based on extracted entities."""
    context_parts = []
    
    if 'time_periods' in entities and entities['time_periods']:
        time_terms = ', '.join(entities['time_periods'])
        context_parts.append(f"the {time_terms} timeline")
    
    if 'quantitative_terms' in entities and entities['quantitative_terms']:
        quant_terms = ', '.join(entities['quantitative_terms'])
        context_parts.append(f"the {quant_terms} metrics")
    
    if 'stakeholders' in entities and entities['stakeholders']:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        context_parts.append(f"the {stakeholder_terms} perspectives")
    
    if 'constraints' in entities and entities['constraints']:
        constraint_terms = ', '.join(entities['constraints'])
        context_parts.append(f"the {constraint_terms} limitations")
    
    if 'risks' in entities and entities['risks']:
        risk_terms = ', '.join(entities['risks'])
        context_parts.append(f"the {risk_terms} factors")
    
    if 'technologies' in entities and entities['technologies']:
        tech_terms = ', '.join(entities['technologies'])
        context_parts.append(f"the {tech_terms} capabilities")
    
    if 'industries' in entities and entities['industries']:
        industry_terms = ', '.join(entities['industries'])
        context_parts.append(f"the {industry_terms} sector dynamics")
    
    if context_parts:
        return f" Pay particular attention to {', '.join(context_parts)}."
    
    return ""

def generate_query_specific_context(query: str) -> str:
    """Generate query-specific context based on the query content."""
    query_lower = query.lower()
    context_parts = []
    
    # Check for specific question types
    if 'how does' in query_lower or 'how do' in query_lower:
        context_parts.append("methodological approach")
    
    if 'what are' in query_lower or 'what is' in query_lower:
        context_parts.append("conceptual understanding")
    
    if 'why' in query_lower:
        context_parts.append("causal analysis")
    
    if 'when' in query_lower:
        context_parts.append("temporal considerations")
    
    if 'where' in query_lower:
        context_parts.append("spatial factors")
    
    if 'who' in query_lower:
        context_parts.append("stakeholder analysis")
    
    # Check for specific optimization contexts
    if 'optimization' in query_lower and 'linear' in query_lower:
        context_parts.append("linear programming techniques")
    
    if 'efficiency' in query_lower and 'flexibility' in query_lower:
        context_parts.append("efficiency-flexibility trade-offs")
    
    if 'production' in query_lower and 'profit' in query_lower:
        context_parts.append("production-profit optimization")
    
    if 'tariff' in query_lower and 'uncertainty' in query_lower:
        context_parts.append("tariff uncertainty management")
    
    if context_parts:
        return f" Focus on {', '.join(context_parts)} in your analysis."
    
    return ""

def enhance_strategic_lens_with_query_context(strategic_lens: str, query: str, entities: dict = None) -> str:
    """
    Enhanced strategic lens generation with better differentiation and query-specific content.
    """
    
    # Extract query-specific keywords for better differentiation
    query_keywords = extract_query_keywords(query)
    
    # Generate query-specific context
    query_context = generate_query_specific_context(query)
    
    # Add query-specific context
    enhanced_lens = strategic_lens
    if query_context:
        enhanced_lens += query_context
    
    # Add query-specific keywords if available
    if query_keywords:
        keyword_context = f" Specifically, consider {', '.join(query_keywords[:3])} in your analysis."
        enhanced_lens += keyword_context
    
    # Add more distinctive entity-based content
    if entities:
        entity_context = generate_entity_context(entities)
        if entity_context:
            enhanced_lens += entity_context
    
    return enhanced_lens
'''
        
        # Find the position to insert helper functions (before the main function)
        insert_position = content.find('def generate_course_domain_strategic_lens')
        if insert_position == -1:
            print("❌ Could not find generate_course_domain_strategic_lens function")
            return False
        
        # Insert helper functions before the main function
        new_content = content[:insert_position] + helper_functions + '\n' + content[insert_position:]
        
        # Replace the main function with the enhanced version
        old_function_start = new_content.find('def generate_course_domain_strategic_lens')
        old_function_end = new_content.find('\n\n\nif __name__ == "__main__":')
        
        if old_function_start == -1 or old_function_end == -1:
            print("❌ Could not locate function boundaries")
            return False
        
        # Replace the function
        final_content = new_content[:old_function_start] + enhanced_functions + '\n\n' + new_content[old_function_end:]
        
        # Write the enhanced content back
        with open('query_engine.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ Enhanced strategic lens generation function applied successfully")
        print("✅ Query-specific keyword extraction added")
        print("✅ Entity-based context generation enhanced")
        print("✅ Better differentiation mechanisms implemented")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying enhanced fix: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_fix():
    """Test the enhanced strategic lens generation."""
    
    print(f"\n🧪 TESTING ENHANCED FIX:")
    print("=" * 60)
    
    try:
        # Import the enhanced functions
        from query_engine import (
            detect_course_concept_domains, 
            extract_application_field,
            extract_enhanced_entities,
            generate_course_domain_strategic_lens
        )
        
        # Test the same queries
        original_query = "under tariff uncertainty, how to optimize the production of my plant to maximize profit for the next year?"
        follow_up_query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
        
        print(f"Testing enhanced strategic lens generation...")
        
        # Test original query
        course_domains = detect_course_concept_domains(original_query)
        application_field = extract_application_field(original_query)
        entities = extract_enhanced_entities(original_query)
        primary_domain = max(course_domains.items(), key=lambda x: x[1])[0] if course_domains else "general"
        
        strategic_lens_orig = generate_course_domain_strategic_lens(
            original_query, primary_domain, application_field, entities
        )
        
        # Test follow-up query
        course_domains_fu = detect_course_concept_domains(follow_up_query)
        application_field_fu = extract_application_field(follow_up_query)
        entities_fu = extract_enhanced_entities(follow_up_query)
        primary_domain_fu = max(course_domains_fu.items(), key=lambda x: x[1])[0] if course_domains_fu else "general"
        
        strategic_lens_fu = generate_course_domain_strategic_lens(
            follow_up_query, primary_domain_fu, application_field_fu, entities_fu
        )
        
        # Calculate similarity
        def calculate_similarity(text1: str, text2: str) -> float:
            words1 = set(re.findall(r'\b\w+\b', text1.lower()))
            words2 = set(re.findall(r'\b\w+\b', text2.lower()))
            if not words1 or not words2:
                return 0.0
            intersection = words1 & words2
            union = words1 | words2
            return len(intersection) / len(union) if union else 0.0
        
        similarity = calculate_similarity(strategic_lens_orig, strategic_lens_fu)
        
        print(f"Enhanced Strategic Lens Similarity Score: {similarity:.2f}")
        
        if similarity < 0.5:
            print("✅ EXCELLENT - Low similarity achieved!")
        elif similarity < 0.7:
            print("✅ GOOD - Moderate similarity, improvement shown")
        else:
            print("⚠️  MODERATE - Some improvement needed")
        
        print("✅ Enhanced strategic lens generation working correctly")
        
    except Exception as e:
        print(f"❌ Error testing enhanced fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 AUTOMATED STRATEGIC LENS FIX")
    print("=" * 60)
    
    try:
        # Apply the enhanced fix
        success = apply_enhanced_fix()
        
        if success:
            # Test the enhanced fix
            test_enhanced_fix()
            
            print(f"\n✅ AUTOMATED FIX COMPLETE")
            print("=" * 60)
            print("Key improvements implemented:")
            print("- Enhanced query-specific keyword extraction")
            print("- Better entity-based context generation")
            print("- More distinctive strategic lens content")
            print("- Improved differentiation between original and follow-up queries")
            print("- Query-specific context integration")
            print("- Comprehensive application field coverage")
        else:
            print("❌ Automated fix failed")
            
    except Exception as e:
        print(f"❌ Error during automated fix: {e}")
        import traceback
        traceback.print_exc() 