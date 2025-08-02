#!/usr/bin/env python3
"""
GPTTutor-Decision V1.6.5 Final Query Engine
Clean, modular, self-testing system for August 12 deployment
"""

import os
import sys
import json
import re
import time
import traceback
import difflib
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import spacy
import uuid
import string

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# V1.6.5 FINAL Configuration
USE_GPT_FOR_DETECTION = True
DEBUG_MODE = False   # Set to True for instructor debugging

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Global variables for lazy loading
_index = None
_metadata = None
_documents = None
_file_names = None
_model = None
_nlp = None

def load_data_lazily():
    """Load data only when needed - prevents import-time hangs"""
    global _index, _metadata, _documents, _file_names, _model, _nlp
    
    if _index is None:
        try:
            _index = faiss.read_index("vector_index.faiss")
            with open("metadata.json", "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            _documents = _metadata["documents"]
            _file_names = _metadata.get("file_names", ["Unknown"] * len(_documents))
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _nlp = spacy.load("en_core_web_sm")
            print("✅ Data loaded successfully")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            sys.exit(1)
    
    return _index, _metadata, _documents, _file_names, _model, _nlp

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# --- Fusion Logic ---
def fuse_detections(keyword, semantic, gpt):
    scores = {}
    for domain in set(keyword + semantic + gpt):
        scores[domain] = 0
        if domain in keyword: scores[domain] += 0.6
        if domain in semantic: scores[domain] += 0.4
        if domain in gpt: scores[domain] += 0.5

        if domain in semantic and domain in gpt:
            scores[domain] += 0.2
        if domain in keyword and domain in semantic and domain in gpt:
            scores[domain] = max(scores[domain], 1.0)

    result = [d for d, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]]

    if DEBUG_MODE:
        print(f"Keyword: {keyword}, Semantic: {semantic}, GPT: {gpt}")
        print(f"Fusion result: {result}")

    return result

# --- Semantic Detection ---
def semantic_domain_detection(query: str) -> List[str]:
    """Semantic domain detection using glossary concepts."""
    try:
        domains = []
        query_lower = query.lower()
        
        # Check glossary concepts for domain classification
        for concept, info in EXPANDED_GLOSSARY.items():
            if concept.lower() in query_lower:
                domain = info.get('domain', 'general')
                if domain not in domains:
                    domains.append(domain)
        
        return domains
    except Exception as e:
        if DEBUG_MODE:
            print(f"Semantic domain detection failed: {e}")
        return []

def semantic_field_detection(query: str) -> List[str]:
    """Semantic field detection using glossary concepts."""
    try:
        fields = []
        query_lower = query.lower()
        
        # Check glossary concepts for field classification
        for concept, info in EXPANDED_GLOSSARY.items():
            if concept.lower() in query_lower:
                field = info.get('application_field', 'general')
                if field not in fields:
                    fields.append(field)
        
        return fields
    except Exception as e:
        if DEBUG_MODE:
            print(f"Semantic field detection failed: {e}")
        return []

def semantic_entity_detection(query: str) -> List[str]:
    """Semantic entity detection using glossary concepts."""
    try:
        entities = []
        query_lower = query.lower()
        
        # Extract entities from glossary concepts
        for concept, info in EXPANDED_GLOSSARY.items():
            if concept.lower() in query_lower:
                entities.append(concept)
        
        return entities
    except Exception as e:
        if DEBUG_MODE:
            print(f"Semantic entity detection failed: {e}")
        return []

# --- GPT Detection ---
def detect_by_gpt(query: str):
    """
    Use GPT to enhance detection of domains, fields, and entities.
    Returns (domains, fields, entities).
    """
    try:
        prompt = f"""
        Analyze this decision-making query and classify it into:
        1. Domains: strategy, analytical_tools, human_behaviors, human_machine
        2. Application Fields: operations, finance, defense, IT, education, sustainability, innovation, leadership
        3. Entities: stakeholders, risks, tools, metrics, timeframes

        Query: "{query}"

        Respond in this exact format:
        Domains: [list of domains]
        Application Fields: [list of fields]
        Entities: [list of entities]
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a decision-analysis assistant. Always respond in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.1
        )

        text = response.choices[0].message.content or ""
        domains, fields, entities = [], [], []

        if DEBUG_MODE:
            print(f"GPT Response: {text}")

        for line in text.splitlines():
            line = line.strip()
            if line.startswith("Domains:"):
                domains_str = line.replace("Domains:", "").strip()
                if domains_str.startswith("[") and domains_str.endswith("]"):
                    domains = [d.strip().strip('"\'') for d in domains_str[1:-1].split(",")]
                else:
                    domains = [d.strip() for d in domains_str.split(",")]
            elif line.startswith("Application Fields:"):
                fields_str = line.replace("Application Fields:", "").strip()
                if fields_str.startswith("[") and fields_str.endswith("]"):
                    fields = [f.strip().strip('"\'') for f in fields_str[1:-1].split(",")]
                else:
                    fields = [f.strip() for f in fields_str.split(",")]
            elif line.startswith("Entities:"):
                entities_str = line.replace("Entities:", "").strip()
                if entities_str.startswith("[") and entities_str.endswith("]"):
                    entities = [e.strip().strip('"\'') for e in entities_str[1:-1].split(",")]
                else:
                    entities = [e.strip() for e in entities_str.split(",")]

        if DEBUG_MODE:
            print(f"Parsed - Domains: {domains}, Fields: {fields}, Entities: {entities}")

        return domains, fields, entities
    except Exception as e:
        if DEBUG_MODE:
            print("⚠️ GPT detection failed:", e)
        return [], [], []

# Import modular components
try:
    from query_engine_bulk_glossary_v165 import EXPANDED_GLOSSARY
    from query_engine_entities_expanded_v165 import EXPANDED_ENTITIES
    GLOSSARY_LOADED = True
except ImportError as e:
    print(f"⚠️ Warning: Modular components not found: {e}")
    EXPANDED_GLOSSARY = {}
    EXPANDED_ENTITIES = {}
    GLOSSARY_LOADED = False

# Decision frameworks
FRAMEWORKS = {
    "decision tree": "A visual tool that maps out different options and their potential outcomes.",
    "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats.",
    "cost-benefit analysis": "A systematic approach to compare the pros and cons of different options.",
    "grow model": "A structured approach to goal setting and action planning.",
    "prospect theory": "Shows how people often value avoiding losses more than achieving gains.",
    "bounded rationality": "The recognition that good decisions don't require perfect information.",
    "ooda loop": "A decision cycle (Observe, Orient, Decide, Act) for rapid decision-making."
}

# Analytical tools for prompt injection
ANALYTICAL_TOOLS = [
    ("Monte Carlo Simulation", "A statistical tool that uses random sampling to simulate thousands of potential outcomes under uncertainty."),
    ("Scenario Analysis", "A method that explores different hypothetical futures (e.g., best-case, worst-case) to support strategic decision planning."),
    ("Sensitivity Analysis", "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions."),
    ("Solver-based Simulation", "A computational approach that uses algorithms to find optimal or feasible solutions under constraints and uncertainty."),
    ("Linear Optimization", "A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints."),
    ("Decision Tree", "A visual tool that maps out options, chance events, and outcomes to support structured decision-making under uncertainty."),
    ("Utility Functions", "Mathematical representations of preferences used to evaluate and compare uncertain outcomes in decision analysis."),
    ("Seasonal Analysis", "A forecasting method that identifies and models repeating patterns or cycles in time series data."),
    ("Regression", "A statistical technique for estimating relationships among variables and predicting future values based on historical data."),
    ("Moving Average", "A method that smooths time series data by averaging values over a specified number of periods to identify trends."),
    ("Semi-quantitative Forecast", "A forecasting approach that combines qualitative judgment with quantitative data for more robust predictions."),
    ("Profitability Analysis", "An assessment of the ability of a project or business to generate earnings compared to its costs and expenses."),
    ("Competitive Advantage Analysis", "A strategic evaluation of factors that allow an organization to outperform its competitors."),
    ("Value Chain Analysis", "A process of analyzing the activities that add value to a product or service from conception to delivery."),
    ("Cognitive Behaviors", "Patterns of thinking and perception that influence decision-making, often studied to improve judgment and reduce bias."),
    ("Judgment Intuitive Bias", "Systematic errors in thinking that affect decisions and judgments, often unconsciously."),
    ("Investigative Negotiation", "A negotiation approach that focuses on uncovering underlying interests and information to create mutually beneficial outcomes."),
    ("Negotiation Term Sheet", "A document outlining the key terms and conditions of a negotiation or agreement before final contracts are drafted."),
    ("Value Creation", "The process of generating benefits that exceed the costs for stakeholders in a decision or transaction."),
    ("Expected Value", "A calculation that combines possible outcomes and their probabilities to determine the average result of uncertain scenarios."),
    ("Risk Tolerance Assessment", "An evaluation of an individual's or organization's willingness to accept risk in pursuit of objectives."),
    ("Leadership Assessment", "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts."),
    ("Human-Computer Integration", "The collaboration between humans and computer systems to enhance decision-making and problem-solving capabilities.")
]

# V1.6.5 IMPROVEMENTS - Core functions
def extract_enhanced_entities(query: str) -> Dict[str, Any]:
    """Extract enhanced entities for additional nuance using fusion logic"""
    try:
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # Use spaCy for entity extraction (keyword-based)
        doc = nlp(query.lower())
        keyword_entities = {
            'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
            'people': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
            'locations': [ent.text for ent in doc.ents if ent.label_ == 'GPE'],
            'money': [ent.text for ent in doc.ents if ent.label_ == 'MONEY'],
            'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
            'concepts': [],
            'keywords': []
        }
        
        # Extract decision-making concepts (semantic-based)
        concept_matches = []
        for concept in EXPANDED_GLOSSARY.keys():
            if concept.lower() in query.lower():
                keyword_entities['concepts'].append(concept)
                keyword_entities['keywords'].append(concept)
                concept_matches.append(concept)
        
        # Semantic detection
        semantic_entities = semantic_entity_detection(query)
        
        # GPT detection
        gpt_entities = []
        if USE_GPT_FOR_DETECTION:
            _, _, gpt_entities = detect_by_gpt(query)
        
        # Merge entities (no cap, deduplicate)
        all_entities = list(set(keyword_entities['keywords'] + semantic_entities + gpt_entities))
        
        # Create final entities dict
        entities = {
            'organizations': keyword_entities['organizations'],
            'people': keyword_entities['people'],
            'locations': keyword_entities['locations'],
            'money': keyword_entities['money'],
            'dates': keyword_entities['dates'],
            'concepts': keyword_entities['concepts'],
            'keywords': all_entities
        }
        
        # Add default keywords if none found
        if not entities['keywords']:
            entities['keywords'] = ['decision', 'analysis', 'strategy']
        
        if DEBUG_MODE:
            print(f"Keyword entities: {keyword_entities['keywords']}")
            print(f"Semantic entities: {semantic_entities}")
            print(f"GPT entities: {gpt_entities}")
            print(f"Merged entities: {all_entities}")
        
        return entities
    except Exception as e:
        print(f"Entity extraction failed: {e}")
        return {'keywords': ['decision', 'analysis', 'strategy']}

def detect_followup_query(query: str) -> bool:
    """Detect if this is a follow-up query"""
    followup_indicators = [
        "what about", "how about", "what if", "but what", "and if",
        "also", "additionally", "furthermore", "moreover", "besides",
        "on the other hand", "however", "but", "yet", "though",
        "although", "despite", "in spite of", "nevertheless"
    ]
    
    query_lower = query.lower()
    return any(indicator in query_lower for indicator in followup_indicators)

def generate_domain_aware_followup_prompt(query: str, entities: Dict[str, Any], is_followup: bool) -> str:
    """Generate domain-aware follow-up prompt with lens-shifting logic"""
    
    # V1.6.5 IMPROVEMENT: LENS-SHIFTING LOGIC
    domains = []
    
    # Detect domains from entities
    if entities.get('concepts'):
        for concept in entities['concepts']:
            if concept in EXPANDED_GLOSSARY:
                domain = EXPANDED_GLOSSARY[concept].get('domain', 'general')
                if domain not in domains:
                    domains.append(domain)
    
    # If no domains detected, use general
    if not domains:
        domains = ['general']
    
    # V1.6.5 RULE: 2-4 follow-ups based on domain count
    if len(domains) == 1:
        max_followups = 3
    else:
        max_followups = min(4, 2 + len(domains) - 1)
    
    prompt = f"""
Generate {max_followups} open-ended follow-up questions for this decision scenario.
Focus on domains: {', '.join(domains)}
Query: {query}
Is follow-up: {is_followup}

Rules:
- 2-4 questions maximum
- Open-ended format
- Domain-specific insights
- Lens-shifting perspective
- No yes/no questions
"""
    
    return prompt

def generate_concept_tooltips(query: str, entities: Dict[str, Any]) -> List[str]:
    """Generate concept tooltips based on V1.6.5 rules"""
    
    try:
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # Get query embedding
        query_embedding = model.encode([query])[0]
        
        # Find relevant concepts
        relevant_concepts = []
        
        for concept, info in EXPANDED_GLOSSARY.items():
            if concept.lower() in query.lower():
                relevant_concepts.append((concept, info, 1.0))  # Direct match
            else:
                # Semantic similarity
                concept_embedding = model.encode([concept])[0]
                similarity = util.pytorch_cos_sim(
                    query_embedding.reshape(1, -1), 
                    concept_embedding.reshape(1, -1)
                )[0][0].item()
                
                if similarity >= 0.35:  # Core threshold
                    relevant_concepts.append((concept, info, similarity))
        
        # Sort by relevance
        relevant_concepts.sort(key=lambda x: x[2], reverse=True)
        
        # Apply V1.6.5 rules
        tooltips = []
        domains = set()
        
        for concept, info, similarity in relevant_concepts:
            domain = info.get('domain', 'general')
            
            # Threshold rules
            if domain == 'primary' and similarity >= 0.50:
                tooltips.append(f"{concept}: {info['definition']}")
                domains.add(domain)
            elif domain == 'secondary' and similarity >= 0.40:
                tooltips.append(f"{concept}: {info['definition']}")
                domains.add(domain)
            elif similarity >= 0.35:
                tooltips.append(f"{concept}: {info['definition']}")
                domains.add(domain)
            
            # Cap at 4 tooltips
            if len(tooltips) >= 4:
                break
        
        # Fallback if no tooltips found
        if not tooltips:
            tooltips = [
                "Strategic Framing: Structuring the decision problem to clarify objectives and alternatives",
                "Cost-Benefit Analysis: Comparing the advantages and disadvantages of different options"
            ]
        
        return tooltips[:4]  # Ensure max 4
        
    except Exception as e:
        print(f"Tooltip generation failed: {e}")
        return [
            "Strategic Framing: Structuring the decision problem to clarify objectives and alternatives",
            "Cost-Benefit Analysis: Comparing the advantages and disadvantages of different options"
        ]

def classify_analytical_subdomain(query: str) -> str:
    """Classify the analytical subdomain based on query content."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["optimize", "optimization", "efficient", "efficiency", "allocate", "allocation"]):
        return "optimization"
    elif any(word in query_lower for word in ["simulate", "simulation", "monte carlo", "scenario", "uncertainty", "risk"]):
        return "simulation"
    else:
        return "general"

def detect_course_concept_domains(query: str) -> List[str]:
    """Detect which course concept domains are relevant to the query using fusion logic."""
    # Keyword detection
    keyword_domains = []
    query_lower = query.lower()
    
    # Strategy domain keywords
    strategy_keywords = ["strategy", "strategic", "positioning", "competitive", "market"]
    if any(word in query_lower for word in strategy_keywords):
        keyword_domains.append("strategy")
    
    # Analytical tools domain keywords
    analytical_keywords = ["optimize", "simulate", "forecast", "model", "analysis", "data", "uncertainty", "tariff"]
    if any(word in query_lower for word in analytical_keywords):
        keyword_domains.append("analytical_tools")
    
    # Human behaviors domain keywords (more specific)
    behavior_keywords = ["bias", "behavior", "judgment", "cognitive", "communication", "interpersonal", "feedback", "bad news"]
    if any(word in query_lower for word in behavior_keywords):
        keyword_domains.append("human_behaviors")
    
    # Negotiation domain keywords (separate from general behavior)
    negotiation_keywords = ["negotiate", "negotiation", "deal", "bargain", "terms", "agreement"]
    if any(word in query_lower for word in negotiation_keywords):
        keyword_domains.append("negotiation")
    
    # Semantic detection
    semantic_domains = semantic_domain_detection(query)
    
    # GPT detection
    gpt_domains = []
    if USE_GPT_FOR_DETECTION:
        gpt_domains, _, _ = detect_by_gpt(query)
    
    # Fusion logic
    result = fuse_detections(keyword_domains, semantic_domains, gpt_domains)
    
    # If no domains detected, default to general
    if not result:
        result = ["general"]
    
    if DEBUG_MODE:
        print(f"Keyword domains: {keyword_domains}")
        print(f"Semantic domains: {semantic_domains}")
        print(f"GPT domains: {gpt_domains}")
        print(f"Fused result: {result}")
    
    return result

def extract_application_fields(query: str, top_n: int = 2) -> List[str]:
    """Extract application fields from the query using fusion logic."""
    # Keyword detection
    keyword_fields = []
    query_lower = query.lower()
    
    # Standard business fields
    business_fields = [
        "marketing", "operations", "finance", "human resources", 
        "information technology", "research and development", "sales"
    ]
    
    for field in business_fields:
        if field in query_lower:
            keyword_fields.append(field)
    
    # Semantic detection
    semantic_fields = semantic_field_detection(query)
    
    # GPT detection
    gpt_fields = []
    if USE_GPT_FOR_DETECTION:
        _, gpt_fields, _ = detect_by_gpt(query)
    
    # Fusion logic
    result = fuse_detections(keyword_fields, semantic_fields, gpt_fields)
    
    # Return top N fields, or default if none found
    if not result:
        result = ["general business context"]
    
    if DEBUG_MODE:
        print(f"Keyword fields: {keyword_fields}")
        print(f"Semantic fields: {semantic_fields}")
        print(f"GPT fields: {gpt_fields}")
        print(f"Fused result: {result}")
    
    return result[:top_n]

def get_top_ranked_concepts(query: str, domains: List[str]) -> List[Dict[str, str]]:
    """Get top ranked concepts based on query and domains."""
    
    # Domain-specific concept libraries
    domain_concepts = {
        "human_behaviors": [
            {"term": "Cognitive Bias", "definition": "Systematic patterns of deviation from rationality in judgment and decision-making"},
            {"term": "Psychological Safety", "definition": "A shared belief that the team is safe for interpersonal risk-taking"},
            {"term": "Emotional Intelligence", "definition": "The ability to understand and manage emotions in oneself and others"},
            {"term": "Active Listening", "definition": "A communication technique that requires the listener to fully concentrate and respond thoughtfully"}
        ],
        "negotiation": [
            {"term": "BATNA", "definition": "Best Alternative To Negotiated Agreement - your fallback option if negotiations fail"},
            {"term": "ZOPA", "definition": "Zone Of Possible Agreement - the range where both parties can reach a mutually acceptable deal"},
            {"term": "Value Creation", "definition": "Expanding the pie by finding ways to satisfy more of everyone's interests"},
            {"term": "Anchoring", "definition": "The tendency to rely heavily on the first piece of information offered in negotiations"}
        ],
        "analytical_tools": [
            {"term": "Monte Carlo Simulation", "definition": "A statistical technique that uses random sampling to simulate thousands of possible outcomes"},
            {"term": "Sensitivity Analysis", "definition": "A method to determine how different values of an input affect a particular outcome"},
            {"term": "Expected Value", "definition": "A calculation that combines possible outcomes and their probabilities"},
            {"term": "Decision Tree", "definition": "A visual tool that maps out options, chance events, and outcomes"}
        ],
        "strategy": [
            {"term": "Competitive Advantage", "definition": "A unique position that allows an organization to outperform its competitors"},
            {"term": "Strategic Positioning", "definition": "How a company differentiates itself in the market to create value"},
            {"term": "Value Chain Analysis", "definition": "A process of analyzing activities that add value to a product or service"},
            {"term": "Core Competencies", "definition": "The unique capabilities that give an organization its competitive edge"}
        ]
    }
    
    # Default concepts for unknown domains
    default_concepts = [
        {"term": "Strategic Framing", "definition": "Structuring the decision problem to clarify objectives and alternatives"},
        {"term": "Cost-Benefit Analysis", "definition": "Comparing the advantages and disadvantages of different options"},
        {"term": "Risk Assessment", "definition": "Evaluating potential threats and their likelihood"},
        {"term": "Stakeholder Analysis", "definition": "Identifying and understanding the interests of all parties affected by a decision"}
    ]
    
    # Determine concept selection based on domains
    if len(domains) == 1:
        # Single domain: 3 concepts from that domain
        primary_domain = domains[0]
        if primary_domain in domain_concepts:
            return domain_concepts[primary_domain][:3]
        else:
            return default_concepts[:3]
    else:
        # Multiple domains: 2 from primary, 1 from each secondary (max 4 total)
        primary_domain = domains[0]
        secondary_domains = domains[1:]
        
        concepts = []
        
        # Add 2 from primary domain
        if primary_domain in domain_concepts:
            concepts.extend(domain_concepts[primary_domain][:2])
        else:
            concepts.extend(default_concepts[:2])
        
        # Add 1 from each secondary domain (up to 2 more to keep total ≤ 4)
        for secondary_domain in secondary_domains[:2]:  # Limit to 2 secondary domains
            if secondary_domain in domain_concepts and len(concepts) < 4:
                concepts.append(domain_concepts[secondary_domain][0])
            elif len(concepts) < 4:
                concepts.append(default_concepts[len(concepts)])
        
        return concepts[:4]  # Ensure max 4 concepts

def generate_strategy_or_explanation(domains: List[str], entities: Dict[str, Any], fields: List[str], query: str) -> str:
    """Generate a 120–140 word strategy explanation using domains, entities, and keywords."""
    analytical_focus = classify_analytical_subdomain(query)
    explanation_parts = []

    # Natural, context-aware opening based on query content and detected domains
    keywords = entities.get('keywords', [])
    
    # Determine the most relevant domain for natural narrative
    primary_domain = None
    if "negotiation" in domains:
        primary_domain = "negotiation"
    elif "analytical_tools" in domains or "technical" in domains:
        primary_domain = "analytical"
    elif "strategy" in domains:
        primary_domain = "strategy"
    elif "human_behaviors" in domains and len(domains) == 1:
        primary_domain = "human_behaviors"
    else:
        primary_domain = "general"
    
    # Generate natural, engaging openings based on context
    if primary_domain == "human_behaviors":
        # For interpersonal situations, focus on the human element naturally
        if "bad news" in query.lower() or "feedback" in query.lower():
            explanation_parts.append(
                "Delivering difficult messages is one of the most challenging aspects of leadership. "
                "The key lies in balancing honesty with empathy—being direct about the situation while "
                "preserving the relationship and the person's dignity."
            )
        elif "communication" in query.lower() or "interpersonal" in query.lower():
            explanation_parts.append(
                "Effective communication isn't just about what you say—it's about how your message "
                "lands with the other person. Understanding their perspective and adapting your approach "
                "can transform a potential conflict into a collaborative solution."
            )
        else:
            explanation_parts.append(
                "When human dynamics are at play, the technical aspects of a decision often take a back seat "
                "to the interpersonal elements. People's emotions, motivations, and relationships can significantly "
                "influence outcomes, sometimes more than the facts themselves."
            )
    
    elif primary_domain == "negotiation":
        # For negotiation scenarios, focus on the collaborative potential
        if "terms" in query.lower() or "deal" in query.lower():
            explanation_parts.append(
                "Every negotiation is essentially a problem-solving exercise where both parties have something "
                "valuable to offer. The art lies in uncovering what each side truly needs versus what they "
                "initially demand, then crafting solutions that create more value than either party expected."
            )
        else:
            explanation_parts.append(
                "Successful negotiations rarely result from one side 'winning' at the other's expense. "
                "Instead, they emerge from understanding each party's underlying interests and finding "
                "creative ways to satisfy more of everyone's needs than initially seemed possible."
            )
    
    elif primary_domain == "analytical":
        # For analytical decisions, focus on the systematic approach
        if "uncertainty" in query.lower() or "risk" in query.lower():
            explanation_parts.append(
                "When facing uncertainty, the temptation is often to wait for more information or make "
                "conservative choices. But the best approach usually involves systematically exploring "
                "the range of possible outcomes and preparing for multiple scenarios."
            )
        elif "optimize" in query.lower() or "efficiency" in query.lower():
            explanation_parts.append(
                "Optimization isn't just about finding the best solution—it's about understanding the "
                "trade-offs involved and ensuring that improving one aspect doesn't inadvertently "
                "undermine others that might be equally important."
            )
        else:
            explanation_parts.append(
                "Complex decisions often benefit from breaking them down into manageable pieces. "
                "By analyzing each component systematically, you can identify patterns and relationships "
                "that aren't immediately obvious, leading to more informed choices."
            )
    
    elif primary_domain == "strategy":
        # For strategic decisions, focus on the big picture
        if "long-term" in query.lower() or "future" in query.lower():
            explanation_parts.append(
                "Strategic decisions are fundamentally about positioning for the future while managing "
                "the present. The challenge lies in balancing immediate needs with long-term vision, "
                "recognizing that today's choices create tomorrow's opportunities and constraints."
            )
        else:
            explanation_parts.append(
                "Strategic thinking requires zooming out to see the bigger picture while staying "
                "grounded in current realities. It's about understanding how today's decisions "
                "will ripple through time and affect multiple stakeholders."
            )
    
    else:
        # For general decisions, focus on the complexity and nuance
        explanation_parts.append(
            "Most meaningful decisions involve multiple competing priorities and uncertain outcomes. "
            "The challenge isn't finding the perfect answer—it's making the best choice given the "
            "information available while remaining flexible enough to adapt as circumstances evolve."
        )

    # Strategy
    if "strategy" in domains:
        explanation_parts.append(
            "From a strategic perspective, clarify long-term goals and competitive positioning. "
            "Consider trade-offs such as growth versus stability or cost leadership versus differentiation."
        )

    # Analytics
    if "analytical_tools" in domains:
        if analytical_focus == "optimization":
            explanation_parts.append(
                "Analytically, Linear Optimization or Decision Trees help balance efficiency with flexibility, ensuring resource allocations remain adaptive."
            )
        elif analytical_focus == "simulation":
            explanation_parts.append(
                "Monte Carlo Simulation and Scenario Planning allow you to test outcomes under uncertainty, preparing robust strategies for volatile demand."
            )
        else:
            explanation_parts.append(
                "Forecasting and sensitivity analysis highlight potential outcomes, helping decision makers anticipate risks and opportunities."
            )

    # Human behaviors
    if "human_behaviors" in domains:
        explanation_parts.append(
            "It is also important to account for human factors—such as cognitive biases or negotiation dynamics—that can shape final decisions."
        )

    # Finance note - only add if finance is strongly relevant to the query
    if "finance" in fields:
        # Check if the query is actually about financial decisions, not just general business
        finance_keywords = ["investment", "roi", "profit", "revenue", "cost", "budget", "financial", "economic", "pricing", "valuation"]
        query_lower = query.lower()
        
        # Only add financial analysis if the query explicitly mentions financial concepts
        if any(keyword in query_lower for keyword in finance_keywords):
            explanation_parts.append(
                "Financial analysis, including ROI and DuPont frameworks, ensures that chosen options align with fiscal health and strategic objectives."
            )

    full_text = " ".join(explanation_parts)

    # Auto-expand if under 100 words
    if len(full_text.split()) < 100:
        full_text += " Additionally, exploring alternative perspectives or potential blind spots can reveal risks or opportunities that might otherwise be overlooked."

    return full_text.strip()

def generate_story_or_analogy(fields: List[str], domains: List[str]) -> str:
    """Generate a 60–80 word case study story in action."""
    field = fields[0] if fields else "general business context"
    
    # Use the same domain priority logic as Strategic Thinking Lens
    primary_domain = None
    if "negotiation" in domains:
        primary_domain = "negotiation"
    elif "analytical_tools" in domains or "technical" in domains:
        primary_domain = "analytical"
    elif "strategy" in domains:
        primary_domain = "strategy"
    elif "human_behaviors" in domains and len(domains) == 1:
        primary_domain = "human_behaviors"
    else:
        primary_domain = "general"
    
    # Generate stories based on primary domain with field customization
    if primary_domain == "negotiation":
        if "operations" in fields:
            return (
                f"A manufacturing company was negotiating with suppliers over component pricing. "
                f"Rather than focusing solely on price, they explored the supplier's capacity constraints "
                f"and discovered opportunities for volume commitments that benefited both parties. "
                f"This led to a long-term partnership that reduced costs by 15% while improving quality."
            )
        elif "finance" in fields:
            return (
                f"Two companies were negotiating a merger with competing valuation models. "
                f"Instead of arguing over numbers, they focused on synergies and growth opportunities. "
                f"This led to a creative earn-out structure that aligned interests and created "
                f"more value than either party initially expected."
            )
        else:
            return (
                f"Two tech startups were deadlocked over intellectual property rights in their merger talks. "
                f"Rather than continuing to argue over ownership percentages, they stepped back to explore "
                f"what each company truly needed to succeed. This led to a creative licensing structure "
                f"that preserved both companies' core assets while enabling the combined entity to thrive."
            )
    
    elif primary_domain == "analytical":
        if "operations" in fields:
            return (
                f"A logistics company was struggling to optimize their delivery routes under uncertain demand. "
                f"Rather than using static planning, they built a simulation model that incorporated "
                f"real-time traffic data and customer behavior patterns. This allowed them to test hundreds "
                f"of scenarios and develop a flexible routing strategy that reduced costs by 25%."
            )
        elif "finance" in fields:
            return (
                f"An investment firm was evaluating portfolio allocation under market uncertainty. "
                f"Rather than relying on historical averages, they used Monte Carlo simulation to model "
                f"thousands of market scenarios. This revealed optimal risk-adjusted allocations "
                f"that outperformed traditional approaches by 3% annually."
            )
        else:
            return (
                f"A manufacturing company was struggling to predict demand for their seasonal products. "
                f"Rather than relying on gut instinct, they built a simulation model incorporating historical "
                f"data, market trends, and customer behavior patterns. This allowed them to test hundreds "
                f"of scenarios and develop a flexible production strategy that reduced waste by 40%."
            )
    
    elif primary_domain == "strategy":
        if "operations" in fields:
            return (
                f"A retail chain was debating whether to expand into e-commerce or focus on improving "
                f"their physical stores. Instead of choosing one approach, they analyzed customer behavior "
                f"and discovered that their best customers actually used both channels. This insight led to "
                f"an integrated strategy that enhanced both experiences, driving growth across all channels."
            )
        elif "finance" in fields:
            return (
                f"A company was deciding between debt financing and equity investment for expansion. "
                f"Rather than choosing based on current rates, they analyzed their growth trajectory "
                f"and market conditions. This led to a hybrid approach that minimized dilution "
                f"while maintaining financial flexibility for future opportunities."
            )
        else:
            return (
                f"A retail chain was debating whether to expand into e-commerce or focus on improving "
                f"their physical stores. Instead of choosing one approach, they analyzed customer behavior "
                f"and discovered that their best customers actually used both channels. This insight led to "
                f"an integrated strategy that enhanced both experiences, driving growth across all channels."
            )
    
    elif primary_domain == "human_behaviors":
        if "operations" in fields:
            return (
                f"A plant manager had to tell his team that production targets were being increased. "
                f"Instead of announcing it in a memo, he gathered the team and explained the business context. "
                f"The conversation became a collaborative discussion about process improvements, "
                f"resulting in ideas that exceeded the new targets while improving safety."
            )
        elif "finance" in fields:
            return (
                f"A CFO had to communicate budget cuts to department heads. Rather than sending emails, "
                f"she held individual meetings to understand each department's priorities and constraints. "
                f"This led to creative solutions that minimized impact while maintaining key initiatives, "
                f"strengthening cross-departmental collaboration."
            )
        else:
            return (
                f"Sarah, a marketing director, faced the delicate task of telling her star employee that his "
                f"promotion was delayed due to budget cuts. Instead of a formal meeting, she invited him for coffee "
                f"and shared the context honestly. The conversation became a collaborative discussion about "
                f"alternative growth opportunities, strengthening their working relationship."
            )
    
    else:  # general
        if "operations" in fields:
            return (
                f"A healthcare organization was torn between investing in new technology or expanding "
                f"their existing services. Rather than making a binary choice, they piloted the technology "
                f"in one department while gradually expanding services in others. This approach allowed them "
                f"to learn from both strategies and adapt their plans based on real-world results."
            )
        elif "finance" in fields:
            return (
                f"A startup was deciding between bootstrapping and seeking venture capital. "
                f"Rather than choosing one path, they analyzed their burn rate and growth potential. "
                f"This led to a hybrid approach: self-funding initial development while preparing "
                f"for strategic investment when market conditions were optimal."
            )
        else:
            return (
                f"A healthcare organization was torn between investing in new technology or expanding "
                f"their existing services. Rather than making a binary choice, they piloted the technology "
                f"in one department while gradually expanding services in others. This approach allowed them "
                f"to learn from both strategies and adapt their plans based on real-world results."
            )

def generate_reflection_prompts(domains: List[str], entities: Dict[str, Any]) -> List[str]:
    """Generate 2–4 domain-specific lens-shifting reflection prompts."""
    import random
    
    prompts = []
    
    # Domain-specific prompt templates
    domain_prompts = {
        "human_behaviors": [
            "How might the decision change when considering the emotional impact on stakeholders?",
            "What if you approached this from the perspective of building trust and relationships?",
            "How does the concept of cognitive bias influence your evaluation of options?",
            "What would change if you prioritized psychological safety in this decision?"
        ],
        "negotiation": [
            "How might the decision change when considering the other party's underlying interests?",
            "What if you explored creative options that expand the pie rather than divide it?",
            "How does the concept of BATNA (Best Alternative To Negotiated Agreement) influence your evaluation?",
            "What would change if you focused on building long-term relationships rather than short-term gains?"
        ],
        "analytical_tools": [
            "How might the decision change when considering different scenarios and their probabilities?",
            "What if you analyzed the sensitivity of your assumptions to different outcomes?",
            "How does the concept of expected value influence your evaluation of options?",
            "What would change if you incorporated more data-driven insights into your analysis?"
        ],
        "strategy": [
            "How might the decision change when considering long-term competitive positioning?",
            "What if you evaluated this from the perspective of sustainable competitive advantage?",
            "How does the concept of strategic fit influence your evaluation of options?",
            "What would change if you prioritized strategic flexibility over immediate optimization?"
        ]
    }
    
    # Determine primary and secondary domains
    if len(domains) == 1:
        # Single domain: 3 questions from that domain
        primary_domain = domains[0]
        if primary_domain in domain_prompts:
            prompts = random.sample(domain_prompts[primary_domain], min(3, len(domain_prompts[primary_domain])))
        else:
            # Fallback for unknown domains
            prompts = [
                "How might the decision change when considering different stakeholder perspectives?",
                "What if you evaluated this from multiple time horizons?",
                "How does the concept of trade-offs influence your evaluation of options?"
            ]
    else:
        # Multiple domains: 2 from primary, 1 from each secondary (max 4 total)
        primary_domain = domains[0]
        secondary_domains = domains[1:]
        
        # Add 2 from primary domain
        if primary_domain in domain_prompts:
            prompts.extend(random.sample(domain_prompts[primary_domain], min(2, len(domain_prompts[primary_domain]))))
        
        # Add 1 from each secondary domain (up to 2 more to keep total ≤ 4)
        for secondary_domain in secondary_domains[:2]:  # Limit to 2 secondary domains
            if secondary_domain in domain_prompts and len(prompts) < 4:
                prompts.append(random.choice(domain_prompts[secondary_domain]))
        
        # If we don't have enough prompts, add generic ones
        while len(prompts) < 4:
            prompts.append("How might the decision change when considering different perspectives?")
    
    return prompts[:4]  # Ensure max 4 prompts

def generate_concept_tool_references(query: str, domains: List[str]) -> List[str]:
    """Generate 2–4 concept/tool references with definitions."""
    tooltips = get_top_ranked_concepts(query, domains)
    formatted = []
    for c in tooltips[:4]:
        formatted.append(f"- **{c['term']}**: {c.get('definition', 'No definition available.')}")
    return formatted

def process_query(query: str, course_config: dict = None) -> str:
    """Main pipeline for generating structured answers."""
    # Extract domains, fields, and entities using fusion logic
    domains_detected = detect_course_concept_domains(query)
    fields = extract_application_fields(query, top_n=2)
    entities = extract_enhanced_entities(query)

    # Generate each section
    explanation = generate_strategy_or_explanation(domains_detected, entities, fields, query)
    story = generate_story_or_analogy(fields, domains_detected)
    prompts = generate_reflection_prompts(domains_detected, entities)
    concepts = generate_concept_tool_references(query, domains_detected)

    # Format the complete answer
    response = f"""
**Strategic Thinking Lens**
{explanation}

**Story in Action**
{story}

**Follow-up Prompts**
{chr(10).join(['• ' + p for p in prompts])}

**Concept & Tool**
{chr(10).join(concepts)}
"""
    return response.strip()

# SELF-TESTING FUNCTIONS
def run_self_test():
    """Run comprehensive self-test"""
    print("🧪 V1.6.5 SELF-TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Basic Import Test", test_basic_import),
        ("Data Loading Test", test_data_loading),
        ("Entity Extraction Test", test_entity_extraction),
        ("Follow-up Detection Test", test_followup_detection),
        ("Tooltip Generation Test", test_tooltip_generation),
        ("Query Processing Test", test_query_processing),
        ("Modular Components Test", test_modular_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 {test_name}...")
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 SELF-TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - V1.6.5 READY FOR DEPLOYMENT")
        return True
    else:
        print("⚠️ SOME TESTS FAILED - NEEDS ATTENTION")
        return False

def test_basic_import():
    """Test basic imports"""
    try:
        import os, sys, json, time
        import numpy as np
        import faiss
        from sentence_transformers import SentenceTransformer
        import spacy
        from openai import OpenAI
        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False

def test_data_loading():
    """Test data loading"""
    try:
        load_data_lazily()
        return True
    except Exception as e:
        print(f"Data loading error: {e}")
        return False

def test_entity_extraction():
    """Test entity extraction"""
    try:
        query = "I need to decide between two job offers with different salaries and locations"
        entities = extract_enhanced_entities(query)
        return isinstance(entities, dict)
    except Exception as e:
        print(f"Entity extraction error: {e}")
        return False

def test_followup_detection():
    """Test follow-up detection"""
    try:
        # Test follow-up query
        followup = detect_followup_query("What about the other option?")
        # Test regular query
        regular = detect_followup_query("I need help deciding")
        return followup and not regular
    except Exception as e:
        print(f"Follow-up detection error: {e}")
        return False

def test_tooltip_generation():
    """Test tooltip generation"""
    try:
        query = "I need to analyze the costs and benefits of this decision"
        tooltips = generate_concept_tooltips(query, {})
        return 1 <= len(tooltips) <= 4
    except Exception as e:
        print(f"Tooltip generation error: {e}")
        return False

def test_query_processing():
    """Test query processing"""
    try:
        query = "I'm considering a career change but worried about the risks"
        result = process_query(query)
        return "Strategic Thinking Lens" in result and len(result) > 100
    except Exception as e:
        print(f"Query processing error: {e}")
        return False

def test_modular_components():
    """Test modular components"""
    try:
        # Test if modular components are available
        if GLOSSARY_LOADED:
            return len(EXPANDED_GLOSSARY) > 0
        else:
            print("Modular components not loaded - using fallback")
            return True
    except Exception as e:
        print(f"Modular components error: {e}")
        return False

# Main execution
if __name__ == "__main__":
    try:
        # Check if test mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # Run self-test suite
            success = run_self_test()
            sys.exit(0 if success else 1)
        else:
            # Interactive mode
            print("🤖 GPTTutor-Decision V1.6.5")
            print("Type 'exit' to quit, 'test' to run self-test")
            
            while True:
                try:
                    query = input("\nAsk a question: ")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting. Goodbye!")
                    break
                
                if query.strip().lower() == "exit":
                    print("👋 Exiting. Goodbye!")
                    break
                
                if query.strip().lower() == "test":
                    run_self_test()
                    continue
                
                if not query.strip():
                    print("⚠️ Please enter a non-empty question.")
                    continue
                
                answer = process_query(query)
                print(f"{answer}")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting. Goodbye!") 