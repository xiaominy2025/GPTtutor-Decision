#!/usr/bin/env python3
"""
Enhanced entity and keyword extraction system to add more nuances to answer generation.
This extracts additional entities and keywords beyond course concept domains and application fields.
"""

import re
import nltk
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('stopwords')

def extract_enhanced_entities(query: str) -> Dict[str, List[str]]:
    """
    Extract enhanced entities and keywords from the query to add nuances to answer generation.
    
    Returns:
        Dictionary with entity categories and their extracted values
    """
    query_lower = query.lower()
    entities = {
        'time_periods': [],
        'quantitative_terms': [],
        'stakeholders': [],
        'constraints': [],
        'objectives': [],
        'risks': [],
        'technologies': [],
        'industries': [],
        'locations': [],
        'emotions': [],
        'uncertainty_indicators': [],
        'comparison_terms': [],
        'action_verbs': [],
        'modifiers': []
    }
    
    # Time periods and temporal indicators
    time_patterns = [
        r'\b(short|long)-?term\b',
        r'\bimmediate\b', r'\bimmediately\b',
        r'\bnext\s+(year|month|quarter|week)\b',
        r'\bover\s+time\b', r'\bin\s+the\s+future\b',
        r'\bongoing\b', r'\bcontinuous\b',
        r'\bdeadline\b', r'\btimeline\b',
        r'\bannual\b', r'\bmonthly\b', r'\bquarterly\b'
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, query_lower)
        entities['time_periods'].extend(matches)
    
    # Quantitative terms and metrics
    quantitative_patterns = [
        r'\b\d+%\b', r'\b\d+\s*percent\b',
        r'\b\d+\s*(million|billion|thousand)\b',
        r'\b\d+\s*(dollars?|euros?|pounds?)\b',
        r'\b\d+\s*(employees?|people|staff)\b',
        r'\b\d+\s*(customers?|clients?)\b',
        r'\b\d+\s*(products?|services?)\b',
        r'\b\d+\s*(locations?|offices?)\b',
        r'\b\d+\s*(years?|months?|weeks?)\b',
        r'\b\d+\s*(hours?|days?)\b',
        r'\b\d+\s*(units?|items?)\b',
        r'\b\d+\s*(times?|occasions?)\b'
    ]
    
    for pattern in quantitative_patterns:
        matches = re.findall(pattern, query_lower)
        entities['quantitative_terms'].extend(matches)
    
    # Stakeholders and roles
    stakeholder_patterns = [
        r'\b(team|teams)\b', r'\b(employee|employees|staff)\b',
        r'\b(manager|managers|management)\b', r'\b(leader|leaders|leadership)\b',
        r'\b(customer|customers|client|clients)\b', r'\b(stakeholder|stakeholders)\b',
        r'\b(partner|partners|partnership)\b', r'\b(supplier|suppliers|vendor|vendors)\b',
        r'\b(investor|investors)\b', r'\b(shareholder|shareholders)\b',
        r'\b(board|directors?)\b', r'\b(executive|executives)\b',
        r'\b(consultant|consultants)\b', r'\b(advisor|advisors)\b'
    ]
    
    for pattern in stakeholder_patterns:
        matches = re.findall(pattern, query_lower)
        entities['stakeholders'].extend(matches)
    
    # Constraints and limitations
    constraint_patterns = [
        r'\b(budget|budgetary)\b', r'\b(cost|costs)\b', r'\b(expense|expenses)\b',
        r'\b(time|timeline|deadline)\b', r'\b(resource|resources)\b',
        r'\b(capacity|capabilities)\b', r'\b(limitation|limitations)\b',
        r'\b(constraint|constraints)\b', r'\b(restriction|restrictions)\b',
        r'\b(regulation|regulations|regulatory)\b', r'\b(compliance|compliant)\b',
        r'\b(legal|law|laws)\b', r'\b(policy|policies)\b',
        r'\b(technical|technology)\b', r'\b(infrastructure)\b',
        r'\b(security|safety)\b', r'\b(quality|standards)\b'
    ]
    
    for pattern in constraint_patterns:
        matches = re.findall(pattern, query_lower)
        entities['constraints'].extend(matches)
    
    # Objectives and goals
    objective_patterns = [
        r'\b(objective|objectives|goal|goals)\b', r'\b(target|targets)\b',
        r'\b(aim|aims)\b', r'\b(purpose|purposes)\b', r'\b(intention|intentions)\b',
        r'\b(mission|missions)\b', r'\b(vision|visions)\b',
        r'\b(strategy|strategies|strategic)\b', r'\b(plan|plans|planning)\b',
        r'\b(improve|improvement|enhance|enhancement)\b', r'\b(optimize|optimization)\b',
        r'\b(maximize|maximization)\b', r'\b(minimize|minimization)\b',
        r'\b(increase|decrease)\b', r'\b(grow|growth)\b',
        r'\b(expand|expansion)\b', r'\b(scale|scaling)\b'
    ]
    
    for pattern in objective_patterns:
        matches = re.findall(pattern, query_lower)
        entities['objectives'].extend(matches)
    
    # Risks and uncertainties
    risk_patterns = [
        r'\b(risk|risks|risky)\b', r'\b(threat|threats)\b', r'\b(danger|dangers)\b',
        r'\b(uncertainty|uncertainties|uncertain)\b', r'\b(volatility|volatile)\b',
        r'\b(instability|unstable)\b', r'\b(unpredictable|unpredictability)\b',
        r'\b(fluctuation|fluctuations)\b', r'\b(variability|variable)\b',
        r'\b(contingency|contingencies)\b', r'\b(backup|backups)\b',
        r'\b(fallback|fallbacks)\b', r'\b(mitigation|mitigate)\b',
        r'\b(insurance|insure)\b', r'\b(hedge|hedging)\b'
    ]
    
    for pattern in risk_patterns:
        matches = re.findall(pattern, query_lower)
        entities['risks'].extend(matches)
    
    # Technologies and tools
    technology_patterns = [
        r'\b(ai|artificial\s+intelligence)\b', r'\b(machine\s+learning|ml)\b',
        r'\b(automation|automated)\b', r'\b(software|hardware)\b',
        r'\b(platform|platforms)\b', r'\b(system|systems)\b',
        r'\b(algorithm|algorithms)\b', r'\b(model|models|modeling)\b',
        r'\b(analytics|analysis)\b', r'\b(data|database)\b',
        r'\b(cloud|cloud-based)\b', r'\b(digital|digitization)\b',
        r'\b(online|offline)\b', r'\b(mobile|web)\b',
        r'\b(api|apis)\b', r'\b(integration|integrated)\b'
    ]
    
    for pattern in technology_patterns:
        matches = re.findall(pattern, query_lower)
        entities['technologies'].extend(matches)
    
    # Industries and sectors
    industry_patterns = [
        r'\b(manufacturing|manufacturer)\b', r'\b(healthcare|health\s+care)\b',
        r'\b(finance|financial|banking)\b', r'\b(retail|e-commerce)\b',
        r'\b(education|educational)\b', r'\b(technology|tech)\b',
        r'\b(consulting|consultant)\b', r'\b(real\s+estate)\b',
        r'\b(transportation|logistics)\b', r'\b(energy|utilities)\b',
        r'\b(telecommunications|telecom)\b', r'\b(media|entertainment)\b',
        r'\b(government|public\s+sector)\b', r'\b(nonprofit|charity)\b'
    ]
    
    for pattern in industry_patterns:
        matches = re.findall(pattern, query_lower)
        entities['industries'].extend(matches)
    
    # Locations and geography
    location_patterns = [
        r'\b(global|international|worldwide)\b', r'\b(national|domestic)\b',
        r'\b(regional|local)\b', r'\b(urban|rural)\b',
        r'\b(office|offices|headquarters)\b', r'\b(branch|branches)\b',
        r'\b(remote|virtual|hybrid)\b', r'\b(on-site|off-site)\b',
        r'\b(market|markets)\b', r'\b(region|regions)\b',
        r'\b(country|countries)\b', r'\b(city|cities)\b'
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, query_lower)
        entities['locations'].extend(matches)
    
    # Emotions and psychological factors
    emotion_patterns = [
        r'\b(anxiety|anxious)\b', r'\b(stress|stressed)\b', r'\b(worry|worried)\b',
        r'\b(confidence|confident)\b', r'\b(optimism|optimistic)\b',
        r'\b(pessimism|pessimistic)\b', r'\b(fear|fearful)\b',
        r'\b(excitement|excited)\b', r'\b(enthusiasm|enthusiastic)\b',
        r'\b(frustration|frustrated)\b', r'\b(satisfaction|satisfied)\b',
        r'\b(trust|trustworthy)\b', r'\b(doubt|doubtful)\b',
        r'\b(comfort|comfortable)\b', r'\b(discomfort|uncomfortable)\b'
    ]
    
    for pattern in emotion_patterns:
        matches = re.findall(pattern, query_lower)
        entities['emotions'].extend(matches)
    
    # Uncertainty indicators
    uncertainty_patterns = [
        r'\b(maybe|perhaps|possibly)\b', r'\b(might|could|would)\b',
        r'\b(uncertain|uncertainty)\b', r'\b(unclear|unclear)\b',
        r'\b(unpredictable|unpredictability)\b', r'\b(volatile|volatility)\b',
        r'\b(fluctuating|fluctuation)\b', r'\b(variable|variability)\b',
        r'\b(conditional|conditions)\b', r'\b(depending|depends)\b',
        r'\b(if|whether|unless)\b', r'\b(contingent|contingency)\b'
    ]
    
    for pattern in uncertainty_patterns:
        matches = re.findall(pattern, query_lower)
        entities['uncertainty_indicators'].extend(matches)
    
    # Comparison terms
    comparison_patterns = [
        r'\b(versus|vs|compared\s+to)\b', r'\b(better|worse|best|worst)\b',
        r'\b(more|less|most|least)\b', r'\b(higher|lower)\b',
        r'\b(greater|smaller)\b', r'\b(stronger|weaker)\b',
        r'\b(faster|slower)\b', r'\b(cheaper|expensive)\b',
        r'\b(easier|harder)\b', r'\b(safer|riskier)\b',
        r'\b(alternative|alternatives)\b', r'\b(option|options)\b',
        r'\b(choice|choices)\b', r'\b(trade-off|trade-offs)\b'
    ]
    
    for pattern in comparison_patterns:
        matches = re.findall(pattern, query_lower)
        entities['comparison_terms'].extend(matches)
    
    # Action verbs
    action_patterns = [
        r'\b(decide|deciding|decision)\b', r'\b(choose|choosing|choice)\b',
        r'\b(select|selecting|selection)\b', r'\b(evaluate|evaluating|evaluation)\b',
        r'\b(assess|assessing|assessment)\b', r'\b(analyze|analyzing|analysis)\b',
        r'\b(compare|comparing|comparison)\b', r'\b(optimize|optimizing|optimization)\b',
        r'\b(implement|implementing|implementation)\b', r'\b(execute|executing|execution)\b',
        r'\b(manage|managing|management)\b', r'\b(lead|leading|leadership)\b',
        r'\b(negotiate|negotiating|negotiation)\b', r'\b(plan|planning)\b',
        r'\b(strategize|strategizing|strategy)\b', r'\b(innovate|innovating|innovation)\b'
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, query_lower)
        entities['action_verbs'].extend(matches)
    
    # Modifiers and qualifiers
    modifier_patterns = [
        r'\b(quick|fast|rapid|slow)\b', r'\b(efficient|inefficient)\b',
        r'\b(effective|ineffective)\b', r'\b(successful|unsuccessful)\b',
        r'\b(profitable|unprofitable)\b', r'\b(sustainable|unsustainable)\b',
        r'\b(scalable|unscalable)\b', r'\b(flexible|inflexible)\b',
        r'\b(adaptable|rigid)\b', r'\b(innovative|traditional)\b',
        r'\b(modern|outdated)\b', r'\b(advanced|basic)\b',
        r'\b(complex|simple)\b', r'\b(comprehensive|limited)\b',
        r'\b(thorough|superficial)\b', r'\b(detailed|general)\b'
    ]
    
    for pattern in modifier_patterns:
        matches = re.findall(pattern, query_lower)
        entities['modifiers'].extend(matches)
    
    # Remove duplicates and empty categories
    for category in entities:
        entities[category] = list(set(entities[category]))
        if not entities[category]:
            del entities[category]
    
    return entities

def enhance_strategic_lens_with_entities(strategic_lens: str, entities: Dict[str, List[str]]) -> str:
    """
    Enhance the strategic lens with extracted entities to add more nuance.
    
    Args:
        strategic_lens: Original strategic lens text
        entities: Extracted entities dictionary
    
    Returns:
        Enhanced strategic lens with entity-specific nuances
    """
    enhanced_lens = strategic_lens
    
    # Add time period considerations
    if 'time_periods' in entities:
        time_terms = ', '.join(entities['time_periods'])
        enhanced_lens += f" Consider the {time_terms} implications of your decision."
    
    # Add stakeholder considerations
    if 'stakeholders' in entities:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        enhanced_lens += f" Account for the perspectives and needs of {stakeholder_terms}."
    
    # Add constraint considerations
    if 'constraints' in entities:
        constraint_terms = ', '.join(entities['constraints'])
        enhanced_lens += f" Be mindful of {constraint_terms} limitations."
    
    # Add risk considerations
    if 'risks' in entities:
        risk_terms = ', '.join(entities['risks'])
        enhanced_lens += f" Address {risk_terms} factors in your analysis."
    
    # Add technology considerations
    if 'technologies' in entities:
        tech_terms = ', '.join(entities['technologies'])
        enhanced_lens += f" Leverage {tech_terms} capabilities appropriately."
    
    # Add industry-specific considerations
    if 'industries' in entities:
        industry_terms = ', '.join(entities['industries'])
        enhanced_lens += f" Consider {industry_terms} sector dynamics."
    
    # Add quantitative considerations
    if 'quantitative_terms' in entities:
        quant_terms = ', '.join(entities['quantitative_terms'])
        enhanced_lens += f" Factor in {quant_terms} metrics."
    
    return enhanced_lens

def enhance_followup_questions_with_entities(followup_questions: List[str], entities: Dict[str, List[str]]) -> List[str]:
    """
    Enhance follow-up questions with extracted entities for more targeted prompts.
    
    Args:
        followup_questions: Original follow-up questions
        entities: Extracted entities dictionary
    
    Returns:
        Enhanced follow-up questions with entity-specific prompts
    """
    enhanced_questions = followup_questions.copy()
    
    # Add stakeholder-specific questions
    if 'stakeholders' in entities:
        stakeholder_terms = ', '.join(entities['stakeholders'])
        enhanced_questions.append(f"How will this decision impact {stakeholder_terms}?")
    
    # Add time-specific questions
    if 'time_periods' in entities:
        time_terms = ', '.join(entities['time_periods'])
        enhanced_questions.append(f"What are the {time_terms} implications of each option?")
    
    # Add constraint-specific questions
    if 'constraints' in entities:
        constraint_terms = ', '.join(entities['constraints'])
        enhanced_questions.append(f"How do {constraint_terms} affect your decision options?")
    
    # Add risk-specific questions
    if 'risks' in entities:
        risk_terms = ', '.join(entities['risks'])
        enhanced_questions.append(f"What {risk_terms} mitigation strategies should you consider?")
    
    # Add comparison-specific questions
    if 'comparison_terms' in entities:
        enhanced_questions.append("What criteria will you use to compare your options systematically?")
    
    # Limit to maximum 4 questions
    return enhanced_questions[:4]

def enhance_story_with_entities(story: str, entities: Dict[str, List[str]]) -> str:
    """
    Enhance the story with extracted entities for more contextual narratives.
    
    Args:
        story: Original story text
        entities: Extracted entities dictionary
    
    Returns:
        Enhanced story with entity-specific details
    """
    enhanced_story = story
    
    # Add stakeholder details
    if 'stakeholders' in entities:
        stakeholder_terms = ', '.join(entities['stakeholders'][:2])  # Limit to 2
        enhanced_story = enhanced_story.replace("Someone", f"A {stakeholder_terms}")
    
    # Add industry context
    if 'industries' in entities:
        industry_terms = ', '.join(entities['industries'][:1])  # Limit to 1
        enhanced_story += f" This {industry_terms} professional"
    
    # Add constraint context
    if 'constraints' in entities:
        constraint_terms = ', '.join(entities['constraints'][:2])  # Limit to 2
        enhanced_story += f" faces {constraint_terms} challenges"
    
    return enhanced_story

# Example usage and testing
if __name__ == "__main__":
    # Test entity extraction
    test_queries = [
        "How can I optimize production while considering team dynamics and budget constraints?",
        "Should I invest in AI technology for my manufacturing business with 50 employees?",
        "What are the risks and opportunities of expanding to 3 new markets next year?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        entities = extract_enhanced_entities(query)
        print("Extracted entities:")
        for category, values in entities.items():
            if values:
                print(f"  {category}: {values}") 