#!/usr/bin/env python3
"""
Clean Query Engine - Produces only user-facing output without developer information
V1.6.6.6 Final Version - No Streaming Support
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
import openai
import numpy as np
import faiss
# OpenAI embeddings instead of sentence-transformers for Lambda compatibility
from pathlib import Path

# --- Lightweight diversity memory (per warm container) ---
RECENT_EXAMPLES_LRU: list[tuple[str, str]] = []  # (entity, year)


# Tunable configuration for concept–lens alignment (one-call engine)
CONFIG_V167B = {
    'SHORTLIST_K': 6,
    'ENABLE_LENS_DERIVED_FOLLOWUPS': True,
    'RECENT_EXAMPLES_MAX': 20,
    'RECENT_EXAMPLES_AVOID_WINDOW': 5,
    'ALWAYS_ENHANCE_LENS': True,
    'PRIMARY_ATTEMPTS': 3,
    'CONTENT_DENSITY_MIN': 0.45,
}

PLACEHOLDER_PHRASES = {
    "company x",
    "company y",
    "company z",
    "company a",
    "company b",
    "organization x",
    "organization y",
    "organization z",
    "a buyer",
    "the buyer",
    "a marketing professional",
    "a marketing executive",
    "a mid-level manager",
    "a retail company",
    "a car manufacturer",
    "a car dealership",
    "an employee",
}

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors
    """
    import numpy as np
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def batch_cosine_similarity(query_vec, reference_vecs):
    """
    Calculate cosine similarity between query vector and multiple reference vectors
    """
    import numpy as np
    similarities = []
    for ref_vec in reference_vecs:
        sim = cosine_similarity(query_vec, ref_vec)
        similarities.append(sim)
    return np.array(similarities)

# Removed sentence-transformers import - using custom cosine similarity
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
            # Spacy not available, using fallback NLP processing
import uuid
import string

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

if not openai_api_key:
    print("FAIL: Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Define metadata loading constants
COURSE_ID = os.getenv("COURSE_ID", "decision")

# 1. Runtime metadata location (Lambda cold start creates this in rebuild mode)
TMP_META_PATH = Path(f"/tmp/courses/{COURSE_ID}/metadata.json")

# 2. Baked base metadata location
COURSE_DIR = Path(f"courses/{COURSE_ID}")
BASE_META_PATH = COURSE_DIR / "base_metadata.json"

# 3. Legacy metadata location (pre-transition)
LEGACY_META_PATH = COURSE_DIR / "metadata.json"

# Select the highest-priority existing file
if TMP_META_PATH.exists():
    SELECTED_META_PATH = TMP_META_PATH
elif BASE_META_PATH.exists():
    SELECTED_META_PATH = BASE_META_PATH
elif LEGACY_META_PATH.exists():
    SELECTED_META_PATH = LEGACY_META_PATH
else:
    raise FileNotFoundError(f"No metadata file found for course {COURSE_ID}")

# --- Relevance Scoring Helper ---
def compute_relevance_score(query):
    """
    Compute relevance score for query abuse prevention.
    Higher scores indicate more relevant queries for decision-making topics.
    """
    # Extract domains using existing function
    domains = detect_course_concept_domains(query)
    domain_count = len([d for d in domains.values() if d > 0.1])
    
    # Extract application field using existing function
    try:
        application_field = extract_application_field_semantic(query, None)  # Will use cached model
    except:
        application_field = extract_application_field(query)
    
    # Extract concepts using existing function (DEPRECATED - will be replaced)
    concepts = get_top_ranked_concepts_DEPRECATED(query, top_k=3)
    concept_count = len(concepts)
    
    # Fuzzy fallback if no concept match
    if not concepts:
        fuzzy_hits = extract_concepts_with_fuzzy_matching(query, threshold=0.8)
        if fuzzy_hits:
            concepts = fuzzy_hits
            concept_count = len(concepts)
    
    # Calculate relevance score
    score = 2 * concept_count + domain_count + (1 if application_field else 0)
    
    debug_info = {
        "domains": list(domains.keys()),
        "application_fields": [application_field] if application_field else [],
        "concepts": [concept[0] for concept in concepts],
        "score": score
    }
    return score, debug_info

# Set OpenAI API key for old API
openai.api_key = openai_api_key

def get_openai_embedding(text):
    """
    Get embedding from OpenAI API for Lambda compatibility
    """
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error getting OpenAI embedding: {e}")
        # Return a zero vector as fallback
        return [0.0] * 1536  # OpenAI ada-002 embedding dimension

def get_openai_embeddings(texts):
    """
    Get embeddings from OpenAI API for multiple texts
    """
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=texts
        )
        return [item['embedding'] for item in response['data']]
    except Exception as e:
        print(f"Error getting OpenAI embeddings: {e}")
        # Return zero vectors as fallback
        return [[0.0] * 1536] * len(texts)

# Performance timing system (moved to API server route level)

# Global variables for lazy loading
_index = None
_metadata = None
_documents = None
_file_names = None
_model = None
_nlp = None

# TEMPORARY CACHE for V1.6.6.6 – to be removed in V1.6.7 when multi-course engine is introduced
# Purpose: Avoid reloading course data (~24s) on every query while bypassing course_config in V1.6.6.6
# This cache should be removed or revised in V1.6.7 when the centralized multi-course architecture is introduced
cached_data = {}

def load_data_lazily():
    """Load data only when needed"""
    global _index, _metadata, _documents, _file_names, _model, _nlp
    
    if _index is None:
        try:
            _index = faiss.read_index("vector_index.faiss")
            with open(SELECTED_META_PATH, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            _documents = _metadata["documents"]
            _file_names = _metadata.get("file_names", ["Unknown"] * len(_documents))
            
            # Use OpenAI embeddings instead of sentence-transformers for Lambda compatibility
            _model = None  # Will use OpenAI API for embeddings
            if SPACY_AVAILABLE:
                _nlp = spacy.load("en_core_web_sm")
            else:
                _nlp = None
            
            # Data loading complete (timing now handled by cache wrapper)
            # Data loaded successfully
            
        except Exception as e:
            print(f"FAIL: Error loading data: {e}")
            sys.exit(1)
    
    return _index, _metadata, _documents, _file_names, _model, _nlp

def load_course_data_cached(course_id):
    """
    TEMPORARY CACHE WRAPPER for V1.6.6.6 – to be removed in V1.6.7 when multi-course engine is introduced
    
    Purpose: Avoid reloading course data (~24s) on every query while bypassing course_config in V1.6.6.6
    This cache should be removed or revised in V1.6.7 when the centralized multi-course architecture is introduced
    
    Args:
        course_id: Course identifier (currently ignored in V1.6.6.6, always uses 'decision')
        
    Returns:
        Cached course data or loads it for the first time
    """
    # V1.6.6.6: Always use 'decision' course regardless of course_id parameter
    # This is a temporary workaround until V1.6.7 multi-course architecture
    effective_course_id = "decision"
    
    if effective_course_id in cached_data:
        # Using cached data
        return cached_data[effective_course_id]
    
    # Performance timing: Only measure actual data loading time
    start_time = time.time()
    # Load data using existing lazy loading mechanism
    data = load_data_lazily()
    duration = time.time() - start_time
    cached_data[effective_course_id] = data
    return data

# Decision frameworks - Core domains of the decision-making process
FRAMEWORKS = {
    "strategic analysis": "Strategic frameworks for analyzing competitive positioning, industry structure, and business strategy decisions.",
    "analytical tools": "Mathematical and statistical tools for optimization, forecasting, simulation, and data-driven decision making.",
    "human behaviors": "Psychological frameworks for understanding cognitive biases, decision patterns, and behavioral economics in decision making.",
    "negotiation frameworks": "Structured approaches for bargaining, value creation, and reaching agreements in competitive situations.",
    "risk assessment": "Systematic frameworks for evaluating uncertainty, threats, and opportunities in decision contexts."
}

# Add a list of analytical tools and their definitions for prompt injection
ANALYTICAL_TOOLS = [
    ("Monte Carlo Simulation", "A statistical tool that uses random sampling to simulate thousands of potential outcomes under uncertainty."),
    ("Scenario Analysis", "A method that explores different hypothetical futures (e.g., best-case, worst-case) to support strategic decision planning."),
    ("Sensitivity Analysis", "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions."),
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
    ("Risk Tolerance Profile", "An evaluation of an individual's or organization's willingness to accept risk in pursuit of objectives."),
    ("Leadership Assessment", "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts."),
    ("Human-Computer Integration", "The collaboration between humans and computer systems to enhance decision-making and problem-solving capabilities.")
]

# Comprehensive concept glossary with domain categorization, core concept flags, and aliases
# Enhanced with improved aliases for better concept detection
CONCEPT_GLOSSARY = {
    "strategic framing": {"definition": "Structuring the decision problem to clarify objectives and alternatives", "core": True, "aliases": ['strategic analysis', 'problem framing', 'decision framing', 'structure decision', 'frame problem', 'strategic framing']},
    "stakeholder alignment": {"definition": "Ensuring all parties' interests are considered and balanced", "core": True, "aliases": ['stakeholder management', 'stakeholder engagement', 'alignment']},
    "risk assessment": {"definition": "Systematic evaluation of potential threats and their impact on decision outcomes", "core": True, "aliases": ['risk evaluation', 'risk analysis', 'threat assessment']},
    "scenario planning": {"definition": "Exploring different future possibilities to prepare for uncertainty", "core": True, "aliases": ['scenario analysis', 'future planning', 'uncertainty planning']},
    "scenario analysis": {"definition": "A modeling approach that explores different future possibilities and outcomes to prepare for uncertainty in decision-making", "core": True, "aliases": ['scenario planning', 'model uncertainty', 'uncertainty modeling']},
    "contingency planning": {"definition": "Developing backup strategies to prepare for uncertainty", "core": False, "aliases": ['backup planning', 'emergency planning', 'fallback strategies']},
    "decision tree": {"definition": "A visual tool that maps out different options and their potential outcomes", "core": True, "aliases": ['decision mapping', 'option tree', 'outcome mapping', 'tree analysis', 'decision branching']},
    "swot analysis": {"definition": "A framework that helps identify strengths, weaknesses, opportunities, and threats", "core": True, "aliases": ['swot', 'strengths weaknesses', 'opportunities threats', 'strengths weaknesses opportunities threats', 'swot analysis']},
    "monte carlo simulation": {"definition": "A statistical modeling tool that uses random sampling to simulate thousands of potential outcomes under uncertainty for risk analysis and production planning", "core": True, "aliases": ['monte carlo', 'simulation modeling', 'statistical simulation', 'uncertainty simulation', 'probabilistic simulation', 'simulate', 'scenarios', 'thousands', 'random sampling', 'simulate uncertainty']},
    "sensitivity analysis": {"definition": "A technique to determine how different values of an input affect a particular outcome under a given set of assumptions", "core": True, "aliases": ['sensitivity testing', 'what-if analysis', 'parameter analysis', 'change parameters', 'different values', 'affects outcome', 'test different inputs', 'parameter sensitivity', 'what if']},
    "linear optimization": {"definition": "A mathematical method for maximizing or minimizing a linear objective function, subject to linear equality and inequality constraints", "core": True, "aliases": ['linear programming', 'optimization', 'mathematical optimization', 'lp method', 'optimize', 'constraints', 'resource allocation', 'optimize under constraints']},
    "utility functions": {"definition": "Mathematical representations of preferences used to evaluate and compare uncertain outcomes in decision analysis", "core": True, "aliases": ['utility', 'preference functions', 'value functions']},
    "expected value": {"definition": "A calculation that combines possible outcomes and their probabilities to determine the average result of uncertain scenarios", "core": True, "aliases": ['expected outcome', 'probability weighted', 'average outcome', 'ev analysis']},
    "batna": {"definition": "Best Alternative to a Negotiated Agreement - your strongest alternative if an agreement cannot be reached", "core": True, "aliases": ['best alternative', 'walk away option', 'negotiation alternative', 'reservation alternative', 'best alternative to negotiated agreement', 'best option if no deal', 'alternative to agreement']},
    "reservation point": {"definition": "The least favorable outcome acceptable before walking away from a negotiation", "core": True, "aliases": ['walk away point', 'minimum acceptable', 'bottom line', 'walk-away point', 'minimum outcome', 'least acceptable', 'walk away', 'reservation point']},
    "zopa": {"definition": "Zone of Possible Agreement - the overlap between both parties' acceptable ranges in negotiation", "core": True, "aliases": ['zone of agreement', 'negotiation zone', 'agreement zone', 'bargaining zone', 'possible agreement', 'negotiation', 'zone of possible agreement', 'agreement range']},
    "supply chain": {"definition": "The network of organizations, people, activities, information, and resources involved in moving a product or service from supplier to customer", "core": True, "aliases": ['supply chain management', 'logistics', 'procurement', 'distribution', 'supply chain optimization', 'supply chain disruption']},
    "risk management": {"definition": "The process of identifying, assessing, and controlling threats to an organization's capital and earnings", "core": True, "aliases": ['risk assessment', 'risk mitigation', 'threat management', 'risk control', 'risk evaluation', 'risk analysis']},
    "leadership style": {"definition": "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts", "core": True, "aliases": ['leadership evaluation', 'leadership skills', 'management assessment', 'leadership assessment']},
    "cognitive behaviors": {"definition": "Patterns of thinking and perception that influence decision-making, often studied to improve judgment and reduce bias", "core": True, "aliases": ['cognitive behavior', 'thinking patterns', 'mental models', 'cognitive bias']},
    "judgment intuitive bias": {"definition": "Systematic errors in thinking that affect decisions and judgments, often unconsciously", "core": True, "aliases": ['cognitive bias', 'judgment bias', 'thinking errors', 'decision bias']},
    "negotiation term sheet": {"definition": "A document outlining the key terms and conditions of a negotiation or agreement before final contracts are drafted", "core": True, "aliases": ['term sheet', 'negotiation terms', 'agreement terms', 'deal sheet']},
    "negotiation strategy": {"definition": "A systematic approach to achieving favorable outcomes in discussions and agreements", "core": True, "aliases": ['negotiation approach', 'bargaining strategy', 'deal strategy']},
    "value creation": {"definition": "The process of generating benefits that exceed the costs for stakeholders in a decision or transaction", "core": True, "aliases": ['value generation', 'benefit creation', 'stakeholder value']},
    "risk tolerance profile": {"definition": "An evaluation of an individual's or organization's willingness to accept risk in pursuit of objectives", "core": True, "aliases": ['risk tolerance', 'risk appetite', 'risk willingness', 'risk tolerance assessment']},
    "human-computer integration": {"definition": "The collaboration between humans and computer systems to enhance decision-making and problem-solving capabilities", "core": True, "aliases": ['human computer', 'human machine', 'computer integration']},
    "competitive advantage analysis": {"definition": "A strategic evaluation of factors that allow an organization to outperform its competitors", "core": True, "aliases": ['competitive advantage', 'competitive analysis', 'advantage analysis']},
    "value chain analysis": {"definition": "A process of analyzing the activities that add value to a product or service from conception to delivery", "core": True, "aliases": ['value chain', 'chain analysis', 'value analysis', 'activity-based analysis', 'value creation activities', 'value activities', 'chain of activities']},
    "investigative negotiation": {"definition": "A negotiation approach that focuses on uncovering underlying interests and information to create mutually beneficial outcomes", "core": True, "aliases": ['investigative', 'interest-based negotiation', 'information gathering', 'uncover interests', 'underlying interests', 'investigative negotiation']},
    "seasonal analysis": {"definition": "A forecasting method that identifies and models repeating patterns or cycles in time series data", "core": False, "aliases": ['seasonal patterns', 'seasonality', 'cyclical analysis', 'seasonality modeling', 'repeating patterns', 'cycles', 'seasonal forecasting', 'cyclical patterns', 'seasonal']},
    "regression": {"definition": "A statistical technique for estimating relationships among variables and predicting future values based on historical data", "core": True, "aliases": ['regression analysis', 'statistical regression', 'prediction model', 'forecast', 'historical', 'trends', 'future values', 'predict based on history', 'statistical prediction', 'forecasting']},
    "moving average": {"definition": "A method that smooths time series data by averaging values over a specified number of periods to identify trends", "core": False, "aliases": ['moving averages', 'trend smoothing', 'time series smoothing']},
    "semi-quantitative forecast": {"definition": "A forecasting approach that combines qualitative judgment with quantitative data for more robust predictions", "core": False, "aliases": ['semi quantitative', 'mixed forecasting', 'qualitative quantitative']},
    "profitability analysis": {"definition": "An assessment of the ability of a project or business to generate earnings compared to its costs and expenses", "core": True, "aliases": ['profitability', 'earnings analysis', 'financial performance']},
    "prospect theory": {"definition": "Shows how people often value avoiding losses more than achieving gains", "core": True, "aliases": ['prospect', 'loss aversion', 'gain loss']},
    "confirmation bias": {"definition": "Favoring evidence that supports existing beliefs", "core": True, "aliases": ['selective evidence bias', 'favor confirming information', 'seek confirming evidence', 'ignore contradicting', 'favor existing beliefs', 'confirm beliefs', 'favor confirming']},
    "anchoring bias": {"definition": "Relying too heavily on initial information", "core": True, "aliases": ['initial value bias', 'rely on first information', 'first piece of information', 'anchor on initial', 'stick to first impression', 'initial reference point', 'first information']},
    "framing bias": {"definition": "Decisions influenced by whether information is presented positively or negatively", "core": True, "aliases": ['context framing', 'positive negative framing', 'presentation bias']},
    "representative heuristic": {"definition": "Judging probability based on similarity", "core": True, "aliases": ['representativeness bias', 'judge by similarity', 'similar to past', 'based on similarity', 'judge probability by similarity']},
    "endowment effect": {"definition": "Valuing owned items higher than market value", "core": True, "aliases": ['ownership bias', 'value own work higher', 'overvalue own', 'my work is worth more', 'value my creation higher', 'own work more valuable', 'personal attachment', 'value own']},
    "status quo bias": {"definition": "Preference for maintaining the current state", "core": True, "aliases": ['resistance to change', 'status quo', 'maintaining current', 'not want to give up', 'reluctant to change', 'prefer current', 'refuse to change', 'stick with current', 'keep current', "don't want to change", 'prefer existing', 'stick to current']},
    "escalation of commitment": {"definition": "Continuing investment in failing endeavors", "core": True, "aliases": ['sunk cost fallacy', 'legacy project', 'continuing investment', 'failing project', 'persistent investment', 'keep investing', 'already spent', 'time investment', 'continue despite failure', 'invest more in failing', 'keep going despite problems', 'legacy']},
    "mental accounting": {"definition": "Treating money and financial resources differently based on their source or context", "core": True, "aliases": ['psychological budgeting', 'money source bias', 'financial categorization']},
    "game theory": {"definition": "Strategic analysis of competitive interactions", "core": True, "aliases": ['strategic games', 'payoff analysis', 'competitive interactions', 'strategic analysis', 'competitive strategy', 'strategic thinking', 'competitive analysis', 'strategic interactions', 'game theory']},
    "winner's curse": {"definition": "Originating in auction theory, it's a bias where the 'winner' ends up worse off by overpaying, overcommitting, or misjudging the true value.", "core": True, "aliases": ['overpaying', 'competitive bidding', 'overcommitting', 'bidding war', 'auction', 'competitive situation', 'overbid', 'competitive overpayment', 'bidding curse', 'auction curse', 'winner curse', 'auction theory', 'auction theory bias', "winner's curse"]},
    "integrative negotiation": {"definition": "Win-win bargaining through value creation", "core": True, "aliases": ['collaborative negotiation', 'win-win bargaining', 'value creation', 'mutual benefits', 'win-win solutions', 'create value', 'collaborative approach', 'mutual gains', 'win-win']},
    "distributive negotiation": {"definition": "Zero-sum bargaining where one's gain is another's loss", "core": False, "aliases": []},
    "porter's five forces": {"definition": "Framework for analyzing industry competitiveness", "core": True, "aliases": ['five forces analysis', 'competitive', 'industry', 'competitiveness', 'industry analysis', 'competitive forces', 'industry structure', 'competitive analysis', 'five forces']},
    "cost leadership": {"definition": "Achieving competitive edge by offering the lowest cost", "core": True, "aliases": ['low-cost strategy', 'competitive edge', 'lowest cost', 'cost advantage', 'price leadership', 'low cost advantage', 'cost competitive', 'lowest price strategy', 'low cost']},
    "differentiation strategy": {"definition": "Gaining advantage by offering unique features valued by customers", "core": True, "aliases": ['uniqueness strategy', 'unique features', 'differentiate', 'product differentiation', 'competitive advantage', 'unique value', 'stand out', 'distinctive features', 'differentiation']},
    "portfolio management": {"definition": "Balancing business units and investments", "core": True, "aliases": ['strategic portfolio management', 'business units', 'balance portfolio', 'investment portfolio', 'manage portfolio', 'portfolio balance', 'business unit management', 'portfolio']},
    "qualitative forecasting": {"definition": "Judgment-based prediction methods", "core": True, "aliases": []},
    "regression forecasting": {"definition": "Using statistical models for long-term predictions", "core": True, "aliases": ['regression analysis']},
    "seasonal forecasting": {"definition": "Accounting for repeating seasonal patterns", "core": True, "aliases": ['seasonality modeling']},
    "integer optimization": {"definition": "Solving LP problems with discrete choices", "core": True, "aliases": ['discrete optimization', 'integer programming', 'discrete choices', 'whole number optimization', 'discrete variables', 'integer variables', 'discrete decision making', 'discrete']},
    "aggregate planning": {"definition": "Balancing supply and demand through optimization", "core": True, "aliases": ['demand-driven optimization', 'balance supply demand', 'supply demand', 'aggregate planning', 'demand planning', 'supply planning']},
    "analytical solver": {"definition": "Tool for implementing optimization models", "core": True, "aliases": ['solver add-on', 'optimization tool', 'solver tool', 'analytical solver']},
    "integrated optimization & simulation": {"definition": "Combining LP and simulation for robust planning", "core": False, "aliases": []},
    "automated simulation models": {"definition": "Tools that streamline repetitive decision simulations", "core": False, "aliases": []},
}

# Domain categorization for better concept filtering
CONCEPT_DOMAINS = {
    # Human behavior and psychology concepts
    "cognitive behaviors": "behavioral",
    "judgment intuitive bias": "behavioral", 
    "prospect theory": "behavioral",
    "leadership style": "behavioral",
    "risk tolerance profile": "behavioral",
    "confirmation bias": "behavioral",
    "anchoring bias": "behavioral",
    "framing bias": "behavioral",
    "representative heuristic": "behavioral",
    "endowment effect": "behavioral",
    "status quo bias": "behavioral",
    "escalation of commitment": "behavioral",
    "mental accounting": "behavioral",
    
    # Technical/analytical concepts
    "monte carlo simulation": "technical",
    "sensitivity analysis": "technical",
    "linear optimization": "technical",
    "utility functions": "technical",
    "expected value": "technical",
    "scenario analysis": "technical",
    "scenario planning": "technical",
    "regression": "technical",
    "moving average": "technical",
    "seasonal analysis": "technical",
    "semi-quantitative forecast": "technical",
    "qualitative forecasting": "technical",
    "regression forecasting": "technical",
    "seasonal forecasting": "technical",
    "integer optimization": "technical",
    "aggregate planning": "technical",
    "analytical solver": "technical",
    "integrated optimization & simulation": "technical",
    "automated simulation models": "technical",
    
    # Strategic concepts
    "strategic framing": "strategic",
    "stakeholder alignment": "strategic",
    "swot analysis": "strategic",
    "competitive advantage analysis": "strategic",
    "value chain analysis": "strategic",
    "value creation": "strategic",
    "profitability analysis": "strategic",
    "porter's five forces": "strategic",
    "cost leadership": "strategic",
    "differentiation strategy": "strategic",
    "portfolio management": "strategic",
    "strategic planning": "strategic",
    "strategic analysis": "strategic",
    
    # Technical/analytical concepts
    
    # Negotiation concepts
    "batna": "negotiation",
    "reservation point": "negotiation",
    "zopa": "negotiation",
    "investigative negotiation": "negotiation",
    "negotiation term sheet": "negotiation",
    "negotiation strategy": "negotiation",
    # Domain corrections per V1666.6.1
    "game theory": "strategic",
    "winner's curse": "behavioral",
    "integrative negotiation": "negotiation",
    "distributive negotiation": "negotiation",
    
    # General decision-making concepts (can apply to multiple domains)
    "decision tree": "technical",
    "risk assessment": "technical",
    "contingency planning": "general",
    "grow model": "general",
    "ooda loop": "general",
    "supply chain": "technical",
    "risk management": "technical",
    "human-computer integration": "technical",
    "decision making process": "strategic",
    "systematic analysis": "technical",
    "process framework": "strategic"
}

# Global cache for concept embeddings to improve performance
_concept_embeddings_cache = None

def clear_concept_cache():
    """Clear the concept embeddings cache to force re-initialization with new format."""
    global _concept_embeddings_cache
    _concept_embeddings_cache = None
    # Concept embeddings cache cleared
    
# Clear cache on import to ensure fresh concept selection
clear_concept_cache() 

def fuzzy_domain_match(query_lower: str, keyword: str, threshold: float = 0.85) -> bool:
    """
    Sophisticated fuzzy matching for domain keywords that avoids opposite meanings.
    
    Args:
        query_lower: Query in lowercase
        keyword: Keyword to match
        threshold: Similarity threshold (default 0.85)
    
    Returns:
        True if keyword matches query with safeguards against opposite meanings
    """
    from difflib import SequenceMatcher
    import re
    
    # First check for exact word boundary match (highest priority)
    if re.search(rf'\b{re.escape(keyword)}\b', query_lower):
        return True
    
    # Define opposite meaning pairs to avoid false matches
    opposite_pairs = {
        'certain': ['uncertain', 'uncertainty'],
        'uncertain': ['certain', 'certainty'],
        'certainty': ['uncertain', 'uncertainty'],
        'uncertainty': ['certain', 'certainty'],
        'optimize': ['compromise', 'degrade'],
        'compromise': ['optimize', 'maximize'],
        'maximize': ['minimize', 'reduce'],
        'minimize': ['maximize', 'increase'],
        'increase': ['decrease', 'reduce'],
        'decrease': ['increase', 'maximize'],
        'reduce': ['increase', 'maximize'],
        'positive': ['negative', 'adverse'],
        'negative': ['positive', 'favorable'],
        'favorable': ['unfavorable', 'negative'],
        'unfavorable': ['favorable', 'positive'],
        'stable': ['volatile', 'unstable'],
        'volatile': ['stable', 'steady'],
        'unstable': ['stable', 'steady'],
        'steady': ['volatile', 'unstable'],
        'predictable': ['unpredictable', 'volatile'],
        'unpredictable': ['predictable', 'stable'],
        'reliable': ['unreliable', 'unstable'],
        'unreliable': ['reliable', 'stable']
    }
    
    # Check if keyword has opposite meanings
    if keyword in opposite_pairs:
        opposites = opposite_pairs[keyword]
        for word in query_lower.split():
            if word in opposites:
                return False  # Avoid matching if opposite word is present
    
    # Fuzzy match with word boundary checking
    words = query_lower.split()
    for word in words:
        # Skip very short words (likely to be false matches)
        if len(word) < 3:
            continue
            
        similarity = SequenceMatcher(None, keyword, word).ratio()
        if similarity >= threshold:
            # Additional check: ensure the matched word is not an opposite
            if keyword in opposite_pairs:
                opposites = opposite_pairs[keyword]
                if word in opposites:
                    continue  # Skip this match, try next word
            return True
    
    return False

def detect_course_concept_domains(query: str) -> dict:
    """
    Detect multiple course concept domains of a query based on sophisticated keyword analysis.
    Returns: Dictionary with course concept domain names as keys and confidence scores as values.
    """
    query_lower = query.lower()
    course_concept_domains = {
        'behavioral': 0,
        'technical': 0,
        'strategic': 0,
        'negotiation': 0
    }
    
    # Behavioral/psychological indicators - Three-tier weighted system
    behavioral_keywords_strong = [
        'psychology', 'bias', 'cognitive', 'judgment', 'motivation', 'emotion', 'behavior', 
        'personality', 'perception', 'heuristic', 'irrational', 'mindset', 'trust', 'fairness', 
        'prejudice', 'stereotype', 'attitude', 'habit'
    ]
    
    behavioral_keywords_modest = [
        'team', 'conflict', 'leadership', 'human', 'people', 'manager', 'workplace', 'relationship', 
        'communication', 'group', 'culture', 'collaboration', 'cooperation', 'morale', 'satisfaction', 
        'loyalty', 'turnover', 'incentive', 'persuasion', 'decision-bias', 'intuition', 'framing', 
        'influence', 'authority', 'hierarchy', 'trustworthiness', 'interaction', 'miscommunication', 
        'negotiation-style', 'reputation', 'credibility', 'empathy', 'feedback', 'cohesion', 'identity', 
        'rivalry', 'hostility', 'compliance', 'disagreement', 'consensus', 'coordination', 
        'organizational-change', 'leadership-choice', 'talent-strategy', 'workforce-plan', 'decision-making-process', 'decision making process', 'systematic-process', 'systematic process',
        'systematic decision', 'decision making', 'decision-making', 'process'
    ]
    
    behavioral_keywords_weak = [
        'stress', 'fatigue', 'workload', 'distraction', 'rumor', 'gossip', 'peer-pressure', 
        'mood', 'impulsive', 'misperception', 'misunderstanding', 'overconfidence'
    ]
    
    # Apply weighted scoring for behavioral keywords with sophisticated fuzzy matching
    for keyword in behavioral_keywords_strong:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['behavioral'] += 3
    
    for keyword in behavioral_keywords_modest:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['behavioral'] += 2
    
    for keyword in behavioral_keywords_weak:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.80):
            course_concept_domains['behavioral'] += 1
    
    # Technical/analytical indicators - Three-tier weighted system
    technical_keywords_strong = [
        'simulation', 'forecast', 'optimization', 'algorithm', 'mathematical', 'calculate', 'data', 
        'statistical', 'uncertainty', 'uncertain', 'probability', 'model', 'regression', 'correlation', 'variance', 
        'distribution', 'equation', 'analytics', 'dataset', 'outlier', 'predictive', 'clustering', 
        'classification', 'Monte Carlo', 'machine-learning', 'artificial-intelligence', 'computation', 
        'quantitative', 'sampling', 'hypothesis', 'variable', 'predictor', 'coefficient', 'diagnostic', 
        'estimator', 'measurement', 'inferential', 'likelihood', 'stochastic', 'residual', 'trend', 
        'time-series', 'scenario-analysis', 'linear-programming', 'decision-tree', 'sensitivity-analysis', 
        'payoff-matrix', 'probability-tree', 'risk-analysis', 'break-even', 'cost-benefit', 'expected-value', 
        'decision-model', 'utility-function', 'solver', 'constraint', 'probability-distribution', 
        'algorithmic-decision', 'decision-support-system', 'optimization-engine', 'predictive-analytics', 
        'recommender-system', 'automation', 'machine-support', 'computer-assisted', 'model-driven-decision', 
        'analytics-engine', 'systematic-decision-making', 'systematic'
    ]
    
    technical_keywords_modest = [
        'production', 'demand', 'operations', 'manufacturing', 'logistics', 'visualize', 'diagram', 
        'chart', 'graph', 'flow', 'dashboard', 'spreadsheet', 'analysis', 'KPI', 'forecasting', 
        'metrics', 'sensitivity', 'benchmarking', 'monitoring', 'validation', 'calibration', 'estimation', 
        'scenario', 'projection', 'baseline', 'quantification', 'scoring', 'optimization-tool', 'modeling', 
        'experiment', 'sampling-plan', 'workflow', 'simulation-tool', 'pipeline', 'evaluation', 
        'trade-off-analysis', 'diagnostic-tool', 'metric', 'dashboard-tool', 'decision-aid', 'digital-twin', 
        'simulation-platform', 'solver-tool', 'analytics-software', 'spreadsheet-model', 'data-visualization', 
        'forecasting-tool'
    ]
    
    # Apply weighted scoring for technical keywords
    for keyword in technical_keywords_strong:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['technical'] += 3
    
    for keyword in technical_keywords_modest:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['technical'] += 2
    
    technical_keywords_weak = [
        'analysis', 'evaluation', 'assessment', 'measurement', 'calculation', 'computation', 
        'processing', 'methodology', 'framework', 'approach', 'technique', 'method', 'tool', 
        'system', 'process', 'procedure', 'protocol', 'standard', 'benchmark', 'metric', 
        'indicator', 'measure', 'score', 'rating', 'ranking', 'comparison', 'comparative'
    ]
    
    for keyword in technical_keywords_weak:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.80):
            course_concept_domains['technical'] += 1
    
    # Strategic indicators - Three-tier weighted system
    strategic_keywords_strong = [
        'strategy', 'strategic', 'market', 'competitive', 'competition', 'business', 'organization', 
        'company', 'industry', 'expansion', 'growth', 'planning', 'corporate', 'advantage', 'positioning', 
        'portfolio', 'diversification', 'integration', 'outsourcing', 'restructuring', 'transformation', 
        'governance', 'sustainability', 'vision', 'mission', 'policy', 'regulation', 'alliance', 'merger', 
        'acquisition', 'entry', 'exit', 'leadership', 'differentiation', 'disruption', 'innovation', 
        'resource', 'capability', 'globalization', 'scenario-planning', 'turnaround', 'pivot', 'consolidation', 
        'scaling', 'shareholder', 'stakeholder', 'profitability', 'pricing-strategy', 'supply-chain', 
        'distribution', 'partnership', 'long-term', 'investment-strategy', 'comparative-advantage', 'barrier', 
        'opportunity', 'threat', 'SWOT', 'PESTEL', 'game-theory', 'prisoner\'s-dilemma', 'Nash-equilibrium', 
        'payoff-structure', 'cooperative-strategy', 'competitive-strategy', 'decision-making', 'decision making', 'systematic'
    ]
    
    strategic_keywords_modest = [
        'resource-allocation', 'competitive-position', 'diversification-option', 'synergy', 'alignment', 
        'prioritization', 'policy-option', 'brand', 'market-share', 'growth-path', 'restructuring-option', 
        'capacity-planning', 'business-model', 'strategy-map', 'investment-plan', 'sustainability-option', 
        'R&D', 'market-entry', 'innovation-path', 'competitive-response', 'industry-trend', 'scaling-up', 
        'divestment', 'global-strategy', 'localization', 'expansion-plan', 'portfolio'
    ]
    
    strategic_keywords_weak = [
        'career', 'job', 'task', 'project', 'assignment', 'option', 'options',
        'planning', 'plan', 'planned', 'choice', 'choices', 'framework', 'frameworks',
        'decision', 'decisions', 'company', 'companies', 'industry', 'industries',
        'organization', 'organizations', 'corporate', 'enterprise'
    ]
    
    # Apply weighted scoring for strategic keywords
    for keyword in strategic_keywords_strong:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['strategic'] += 3
    
    for keyword in strategic_keywords_modest:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['strategic'] += 2
    
    for keyword in strategic_keywords_weak:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.80):
            course_concept_domains['strategic'] += 1
    
    # Negotiation indicators - Three-tier weighted system
    negotiation_keywords_strong = [
        'negotiate', 'negotiation', 'bargain', 'contract', 'settlement', 'concession', 'deadlock', 
        'mediation', 'arbitration', 'bargaining', 'BATNA', 'anchoring', 'integrative', 'distributive', 
        'bargaining-table', 'stalemate', 'mediator', 'negotiator', 'arbitration-panel', 
        'collective-bargaining', 'bargaining-power', 'mediation-talks', 'dispute-resolution', 'arbitration-case', 
        'mediator-role', 'adversarial', 'positional', 'interest-based', 'concession-trade', 
        'bargaining-zone', 'impasse', 'escalation', 'face-saving', 'negotiation-outcome', 'bargaining-leverage', 
        'distributive-bargain'
    ]
    
    negotiation_keywords_modest = [
        'merger', 'joint-venture', 'treaty', 'trade-talks', 'peace-talks', 'coalition', 'roundtable',
        # keep only negotiation-specific signals; remove generic terms like 'agreement' or 'deal'
        'deal-making', 'contract-terms', 'agreement-terms'
    ]
    
    negotiation_keywords_weak = [
        # remove overly generic terms that create false positives
        'compromise', 'mutual-gain'
    ]
    
    # Apply weighted scoring for negotiation keywords
    for keyword in negotiation_keywords_strong:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['negotiation'] += 3
    
    for keyword in negotiation_keywords_modest:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.85):
            course_concept_domains['negotiation'] += 2
    
    for keyword in negotiation_keywords_weak:
        if fuzzy_domain_match(query_lower, keyword, threshold=0.80):
            course_concept_domains['negotiation'] += 1
    

    

    
    # Normalize scores and filter out zero scores
    total_keywords = sum(course_concept_domains.values())
    if total_keywords == 0:
        # If no domain keywords found, return empty dict (will be treated as general)
        return {}
    else:
        # Convert to percentages
        for domain in course_concept_domains:
            course_concept_domains[domain] = course_concept_domains[domain] / total_keywords
    
    return course_concept_domains

def detect_query_domain(query: str) -> str:
    """
    Detect the primary domain of a query (backward compatibility).
    Returns: 'behavioral', 'technical', 'strategic', 'negotiation', or 'general'
    """
    domains = detect_course_concept_domains(query)
    # Return the domain with the highest score
    return max(domains, key=domains.get)

# DEPRECATED: get_top_ranked_concepts function removed to eliminate conflicts
# This function was causing issues with concept selection logic
# Use the new unified select_concepts function instead

def get_top_ranked_concepts_DEPRECATED(query: str, top_k: int = 3, custom_glossary: dict = None, skip_domain_filtering: bool = False) -> List[Tuple[str, str]]:
    """
    Extract concepts using semantic similarity scoring with SentenceTransformer embeddings.
    
    Args:
        query: The user's query text
        top_k: Maximum number of concepts to return (default 3, max 4)
        custom_glossary: Optional course-specific glossary to use instead of default
        
    Returns:
        List of (concept_name, definition) tuples ranked by relevance score
    """
    # Cap at maximum 4 concepts to maintain focus
    top_k = min(top_k, 4)
    global _concept_embeddings_cache
    
    # Use custom glossary if provided, otherwise use default
    glossary_to_use = custom_glossary if custom_glossary else CONCEPT_GLOSSARY
    
    try:
        # Load data lazily
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # Use semantic domain detection for more accurate classification
        query_domains = detect_domain_semantic(query)
        if query_domains:
            # Only use the strongest domain to avoid broadening perspectives
            primary_domain = max(query_domains, key=query_domains.get)
            # Convert to single-domain format to prevent multi-domain broadening
            query_domains = {primary_domain: query_domains[primary_domain]}
        else:
            primary_domain = 'general'
            query_domains = {}
        
        # Generate embedding for the query using OpenAI
        query_embedding = get_openai_embeddings([query])
        
        # Initialize or get cached concept embeddings
        if _concept_embeddings_cache is None:
            # Use more descriptive concept texts for better matching
            concept_texts = []
            for name, concept_data in glossary_to_use.items():
                # Handle both old string format and new dictionary format
                if isinstance(concept_data, str):
                    definition = concept_data
                else:
                    definition = concept_data["definition"]
                # Create a more focused text that emphasizes the definition over the name
                # This reduces false matches based on word overlap in concept names
                concept_text = f"{definition} {name.replace('-', ' ')}"
                concept_texts.append(concept_text)
            _concept_embeddings_cache = get_openai_embeddings(concept_texts)
        
        # Calculate cosine similarities using custom function
        similarities = batch_cosine_similarity(query_embedding[0], _concept_embeddings_cache)
        
        # Create list of (concept_name, definition, score) tuples with domain filtering
        concept_scores = []
        concept_names = list(glossary_to_use.keys())
        
        # Check if this is a visualization-related query
        query_lower = query.lower()
        is_visualization_query = any(word in query_lower for word in [
            'visualize', 'visualized', 'visualization', 'visual', 'visual manner',
            'visualize', 'visualized', 'visualization', 'visual', 'visual manner',
            'map out', 'mapping', 'diagram', 'chart', 'graph', 'tree', 'flow'
        ])
        
        # Check if this is a choice/option selection query (more specific keywords)
        is_choice_query = any(word in query_lower for word in [
            'choose', 'choosing', 'choice', 'choices', 'select', 'selecting', 'selection',
            'option', 'options', 'alternative', 'alternatives', 'between', 'versus', 'vs',
            'which', 'what', 'how to choose', 'how to select', 'evaluate options', 'compare options'
        ])
        
        # Enhanced pattern recognition for better concept selection
        detected_patterns = {}
        pattern_keywords = {
            'comparison': ['compare', 'versus', 'vs', 'between', 'choose', 'select', 'option', 'options', 'alternative', 'alternatives'],
            'analysis': ['analyze', 'evaluate', 'assess', 'examine', 'study', 'investigate', 'research'],
            'planning': ['plan', 'strategy', 'approach', 'method', 'process', 'framework'],
            'risk': ['risk', 'uncertainty', 'probability', 'chance', 'likelihood', 'scenario'],
            'optimization': ['optimize', 'maximize', 'minimize', 'best', 'optimal', 'efficient', 'efficiency'],
            'forecasting': ['forecast', 'predict', 'future', 'trend', 'projection', 'estimate']
        }
        
        for pattern, keywords in pattern_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > 0:
                detected_patterns[pattern] = matches / len(keywords)  # Normalized score
        
        for i, (concept_name, concept_data) in enumerate(glossary_to_use.items()):
            score = similarities[i]
            
            # Check if any aliases appear in the query for additional score boost
            alias_boost = 0.0
            if isinstance(concept_data, dict) and "aliases" in concept_data:
                for alias in concept_data["aliases"]:
                    if alias.lower() in query_lower:
                        alias_boost = 0.15  # Boost score by 0.15 if alias found
                        break
            
            # Apply alias boost to similarity score
            score += alias_boost
            
            # Apply keyword-based boosting for generic queries
            keyword_boost = 0.0
            query_lower = query.lower()
            
            # For generic "decision making process" queries, boost relevant concepts
            if any(word in query_lower for word in ['process', 'systematic', 'decision making', 'components']):
                # V1.6.6: Prioritize decision-making specific analytical tools over generic assessments
                # Tier 1: Core decision-making analytical tools (highest boost)
                if concept_name in ['decision tree', 'scenario analysis', 'monte carlo simulation', 'linear optimization', 'integer optimization', 'sensitivity analysis', 'expected value', 'utility functions']:
                    keyword_boost = 0.4  # Strong boost for core analytical tools
                # Tier 2: Strategic decision-making frameworks (decision-making specific)
                elif concept_name in ['scenario planning', 'competitive advantage analysis', 'porter\'s five forces', 'value chain analysis']:
                    keyword_boost = 0.3
                # Tier 3: Behavioral decision-making concepts
                elif concept_name in ['framing bias', 'cognitive behaviors', 'judgment intuitive bias', 'confirmation bias', 'anchoring bias']:
                    keyword_boost = 0.25
                # Tier 4: Generic assessment tools (lower boost to reduce dominance)
                elif concept_name in ['risk assessment', 'leadership assessment']:
                    keyword_boost = 0.0  # No boost for generic assessments
                # Tier 5: Negotiation concepts for decision making
                elif concept_name in ['batna', 'game theory', 'integrative negotiation']:
                    keyword_boost = 0.2
            
            # For uncertainty/risk queries, boost Monte Carlo simulation and related tools
            if any(word in query_lower for word in ['uncertainty', 'risk', 'tariff', 'volatile', 'unpredictable', 'probability']):
                if concept_name == 'monte carlo simulation':
                    keyword_boost = 0.5  # Strong boost for uncertainty queries
                elif concept_name in ['sensitivity analysis', 'scenario analysis', 'expected value', 'decision tree']:
                    keyword_boost = 0.3  # Moderate boost for related uncertainty tools
            
            score += keyword_boost
            
            # Apply pattern-based concept boosting (minimal overhead)
            pattern_boost = 0.0
            if detected_patterns:
                # Define concept-pattern relationships for boosting
                concept_patterns = {
                    'decision tree': ['comparison', 'planning'],
                    'swot analysis': ['analysis', 'planning'],
                    'monte carlo simulation': ['risk', 'forecasting'],
                    'scenario analysis': ['risk', 'planning'],
                    'linear optimization': ['optimization', 'analysis'],
                    'sensitivity analysis': ['analysis', 'risk'],
                    'expected value': ['risk', 'analysis'],
                    'utility functions': ['analysis', 'comparison'],
                    'competitive analysis': ['analysis', 'planning'],
                    'strategic positioning': ['planning', 'analysis'],
                    'forecasting': ['forecasting', 'analysis'],
                    'moving average': ['forecasting', 'analysis'],
                    'regression': ['forecasting', 'analysis']
                }
                
                # Check if this concept should be boosted based on detected patterns
                if concept_name in concept_patterns:
                    for pattern in concept_patterns[concept_name]:
                        if pattern in detected_patterns:
                            pattern_boost = max(pattern_boost, detected_patterns[pattern] * 0.1)  # Small boost
            
            # Apply pattern boost
            score += pattern_boost
            
            # Apply behavioral concept boosting for specific query types
            behavioral_boost = 0.0
            query_lower = query.lower()
            
            # Check for critique/feedback related keywords (negative presentation)
            critique_keywords = ['critique', 'criticism', 'feedback', 'unfair', 'unjust', 'negative', 'manager', 'employee', 'workplace', 'boss', 'bad news']
            if any(keyword in query_lower for keyword in critique_keywords):
                # Boost framing bias for critique-related queries (positive vs negative presentation)
                if concept_name == 'framing bias':
                    behavioral_boost = 0.35  # Increased boost for critique-related queries
                # Boost confirmation bias for critique-related queries
                elif concept_name == 'confirmation bias':
                    behavioral_boost = 0.30  # Increased boost
                # Boost anchoring bias for workplace feedback
                elif concept_name == 'anchoring bias':
                    behavioral_boost = 0.25  # Increased boost
                # Penalize mental accounting for critique-related queries (not money-related)
                elif concept_name == 'mental accounting':
                    behavioral_boost = -0.30  # Significant penalty - critiques are not about money
            
            # Check for money/financial related keywords
            money_keywords = ['money', 'financial', 'finance', 'budget', 'budgeting', 'cost', 'price', 'salary', 'salaries', 'investment', 'payment', 'expense', 'expenses', 'income', 'revenue', 'profit', 'loss', 'spending', 'spend', 'saving', 'save']
            if any(keyword in query_lower for keyword in money_keywords):
                # Boost mental accounting for money-related queries
                if concept_name == 'mental accounting':
                    behavioral_boost = 0.40  # Strong boost - money-related queries
                # Penalize framing bias for money-related queries (not about positive/negative presentation)
                elif concept_name == 'framing bias':
                    behavioral_boost = -0.20  # Moderate penalty - money queries are not about presentation framing
                # Penalize technical concepts for behavioral money queries
                elif concept_name in ['seasonal forecasting', 'aggregate planning', 'integrated optimization & simulation']:
                    behavioral_boost = -0.30  # Strong penalty - technical concepts not relevant for personal budgeting
            
            # Apply behavioral boost
            score += behavioral_boost
            
            # Apply generic concept penalty to avoid domination by overly generic concepts
            generic_penalty = 0.0
            generic_concepts = [
                'swot analysis',         # Generic strategic tool
                'competitive analysis',   # Generic business analysis
                'risk assessment',        # Generic assessment tool (could apply to many contexts)
                'leadership assessment',  # Generic assessment tool (could apply to many contexts)
                'strategic framing'       # Generic strategic concept (applies to all decision-making)
            ]
            
            if concept_name in generic_concepts:
                # Apply penalty based on how generic the concept is
                if concept_name == 'swot analysis':
                    generic_penalty = 0.20  # Increased penalty for generic SWOT
                elif concept_name == 'strategic framing':
                    generic_penalty = 0.15  # Strong penalty for generic strategic framing
                elif concept_name == 'competitive analysis':
                    generic_penalty = 0.08  # Light penalty
                elif concept_name in ['risk assessment', 'leadership assessment']:
                    generic_penalty = 0.25  # Significant penalty for generic assessments
            
            # Apply generic penalty
            score -= generic_penalty
            
            # Apply context-aware penalties for concepts that are inappropriate for certain query types
            context_penalty = 0.0
            
            # Check for communication/behavioral queries that shouldn't include bidding-specific concepts
            communication_keywords = ['convey', 'communicate', 'tell', 'inform', 'deliver', 'present', 'share', 'explain', 'discuss', 'talk', 'speak', 'message', 'news', 'feedback', 'criticism', 'boss', 'manager', 'supervisor', 'employee', 'colleague', 'team', 'workplace', 'meeting', 'conversation']
            if any(keyword in query_lower for keyword in communication_keywords):
                # Penalize bidding-specific concepts for communication queries
                if concept_name == "winner's curse":
                    context_penalty = 0.35  # Keep meaningful but not over-penalizing outside bidding contexts
                elif concept_name in ['batna', 'integrative negotiation', 'distributive negotiation']:
                    context_penalty = 0.30  # Moderate penalty - negotiation concepts not relevant for simple communication
            
            # Check for bidding/auction-specific queries that should include winner's curse
            bidding_keywords = ['bid', 'bidding', 'auction', 'tender', 'proposal', 'offer', 'compete', 'competitive bidding', 'overpay', 'overbid', 'winning bid', 'losing bid']
            if any(keyword in query_lower for keyword in bidding_keywords):
                # Boost winner's curse for bidding/auction-related queries
                if concept_name == "winner's curse":
                    context_penalty = -0.20  # Negative penalty = boost for bidding queries
            
            # Check for personal/individual queries that shouldn't include strategic business concepts
            personal_keywords = ['my', 'personal', 'individual', 'myself', 'I', 'me', 'own', 'private', 'personal decision', 'personal choice']
            if any(keyword in query_lower for keyword in personal_keywords):
                # Penalize strategic business concepts for personal queries
                if concept_name in ['porter\'s five forces', 'competitive advantage analysis', 'value chain analysis']:
                    context_penalty = 0.35  # Strong penalty - business strategy not relevant for personal decisions
            
            # Apply context penalty
            score -= context_penalty
            
            # LOWER THRESHOLD: Changed from 0.10 to 0.05 to capture more concepts for very generic queries
            if score > 0.05:  # Lower threshold to capture more concepts for very generic queries
                # Handle both old string format and new dictionary format
                if isinstance(concept_data, str):
                    definition = concept_data
                    is_core = False  # Default to False for old format
                else:
                    definition = concept_data["definition"]
                    is_core = concept_data.get("core", False)
                
                # Apply multi-domain filtering: calculate weighted score based on all detected domains
                concept_domain = CONCEPT_DOMAINS.get(concept_name, 'general')
                
                # Calculate domain multiplier based on all detected domains
                domain_multiplier = 0.5  # Base multiplier for irrelevant domains
                
                # Special handling for visualization queries - boost decision tree
                if is_visualization_query and concept_name == "decision tree":
                    domain_multiplier = 1.2  # Boost decision tree for visualization queries
                # Special handling for choice queries - boost decision tree
                elif is_choice_query and concept_name == "decision tree":
                    domain_multiplier = 1.4  # Strong boost for decision tree in choice queries
                elif query_domains:  # If specific domains are detected
                    if concept_domain in query_domains:
                        # Concept domain is detected in query - use weighted score
                        domain_score = query_domains[concept_domain]
                        if domain_score > 0.3:  # Strong domain match
                            domain_multiplier = 1.5
                        elif domain_score > 0.1:  # Moderate domain match
                            domain_multiplier = 1.2
                        else:  # Weak domain match
                            domain_multiplier = 1.0
                    elif concept_domain == 'general':
                        # General concepts get penalized when specific domains are detected
                        # The stronger the domain signals, the more we penalize general concepts
                        strongest_domain_score = max(query_domains.values())
                        if strongest_domain_score > 0.5:  # Strong domain signal
                            domain_multiplier = 0.6  # Significant penalty
                        elif strongest_domain_score > 0.3:  # Moderate domain signal
                            domain_multiplier = 0.7  # Moderate penalty
                        else:  # Weak domain signal
                            domain_multiplier = 0.8  # Light penalty
                    else:
                        # Concept domain is not detected in query - apply penalty
                        # BUT: Be less aggressive for core concepts that are very close to threshold
                        strongest_domain_score = max(query_domains.values())
                        
                        # Special handling for core concepts that are very close to threshold
                        if is_core and score > 0.45:  # Core concept very close to threshold
                            if strongest_domain_score > 0.8:  # Very strong domain signal
                                domain_multiplier = 0.8  # Light penalty instead of heavy
                            elif strongest_domain_score > 0.5:  # Strong domain signal
                                domain_multiplier = 0.9  # Very light penalty
                            else:  # Moderate domain signal
                                domain_multiplier = 1.0  # No penalty
                        else:
                            # Standard penalty for non-core or lower-scoring concepts
                            if strongest_domain_score > 0.5:  # Strong domain signal
                                domain_multiplier = 0.7  # Reduced penalty (was 0.6)
                            elif strongest_domain_score > 0.3:  # Moderate domain signal
                                domain_multiplier = 0.8  # Reduced penalty (was 0.7)
                            else:  # Weak domain signal
                                domain_multiplier = 0.9  # Reduced penalty (was 0.8)
                            # Concept domain is not detected in query - apply penalty
                            # BUT: Be less aggressive for core concepts that are very close to threshold
                            strongest_domain_score = max(query_domains.values())
                            
                            # Special handling for core concepts that are very close to threshold
                            if is_core and score > 0.45:  # Core concept very close to threshold
                                if strongest_domain_score > 0.8:  # Very strong domain signal
                                    domain_multiplier = 0.8  # Light penalty instead of heavy
                                elif strongest_domain_score > 0.5:  # Strong domain signal
                                    domain_multiplier = 0.9  # Very light penalty
                                else:  # Moderate domain signal
                                    domain_multiplier = 1.0  # No penalty
                            else:
                                # Standard penalty for non-core or lower-scoring concepts
                                if strongest_domain_score > 0.5:  # Strong domain signal
                                    domain_multiplier = 0.7  # Reduced penalty (was 0.6)
                                elif strongest_domain_score > 0.3:  # Moderate domain signal
                                    domain_multiplier = 0.8  # Reduced penalty (was 0.7)
                                else:  # Weak domain signal
                                    domain_multiplier = 0.9  # Reduced penalty (was 0.8)
                else:
                    # No specific domains detected - treat as general query
                    if concept_domain == 'general':
                        domain_multiplier = 1.0  # Neutral for general concepts
                    else:
                        domain_multiplier = 0.8  # Slight penalty for specific concepts in general queries
                
                adjusted_score = score * domain_multiplier
                
                # Apply core concept prioritization
                if is_core:
                    adjusted_score *= 1.2
                
                concept_scores.append((concept_name, definition, adjusted_score, is_core))
        
        # Sort by adjusted score (highest first)
        concept_scores.sort(key=lambda x: x[2], reverse=True)

        # Suppress negotiation concepts unless negotiation is the primary domain or explicit negotiation terms exist
        query_lower_for_neg = query.lower()
        explicit_neg_terms = ['negotiate', 'negotiation', 'bargain', 'batna', 'zopa', 'anchoring']
        negotiation_allowed = False
        if query_domains:
            primary_domain_tmp = max(query_domains, key=query_domains.get)
            if primary_domain_tmp == 'negotiation':
                negotiation_allowed = True
        if not negotiation_allowed and any(term in query_lower_for_neg for term in explicit_neg_terms):
            negotiation_allowed = True
        if not negotiation_allowed:
            concept_scores = [c for c in concept_scores if CONCEPT_DOMAINS.get(c[0], 'general') != 'negotiation']
        
        # DOMAIN-DRIVEN CONCEPT SELECTION
        if query_domains and not skip_domain_filtering:
            # Classify concepts by domain
            primary_domain = max(query_domains, key=query_domains.get)
            primary_score = query_domains[primary_domain]
            
            # Separate concepts by domain
            primary_domain_concepts = []
            secondary_domain_concepts = []
            other_domain_concepts = []
            
            for name, definition, score, is_core in concept_scores:
                concept_domain = CONCEPT_DOMAINS.get(name, 'general')
                
                if concept_domain == primary_domain:
                    primary_domain_concepts.append((name, definition, score, is_core))
                elif concept_domain in query_domains:
                    secondary_domain_concepts.append((name, definition, score, is_core))
                else:
                    other_domain_concepts.append((name, definition, score, is_core))
            
            # DOMAIN-BALANCED SELECTION LOGIC
            selected_concepts = []
            
            if primary_score > 0.8:  # Single domain - select 3 from primary
                selected_concepts = primary_domain_concepts[:3]
            else:  # Multi-domain - select 2 from primary + 1 from each secondary
                # Select 2 from primary domain
                selected_concepts = primary_domain_concepts[:2]
                
                # Select 1 from each secondary domain (highest scoring)
                secondary_domains = [d for d in query_domains.keys() if d != primary_domain and query_domains[d] > 0.3]
                for secondary_domain in secondary_domains:
                    secondary_concepts = [c for c in secondary_domain_concepts if CONCEPT_DOMAINS.get(c[0], 'general') == secondary_domain]
                    if secondary_concepts:
                        # Sort by score (highest first) and take the best one
                        secondary_concepts.sort(key=lambda x: x[2], reverse=True)
                        selected_concepts.append(secondary_concepts[0])
            
            # If we don't have enough concepts from domain-driven selection, fill with high-scoring concepts
            if len(selected_concepts) < top_k:
                remaining_concepts = [c for c in concept_scores if c not in selected_concepts]
                selected_concepts.extend(remaining_concepts[:top_k - len(selected_concepts)])
            
            # Take top_k concepts from selected
            final_concepts = selected_concepts[:top_k]
        else:
            # No specific domains detected OR skip_domain_filtering is True - use traditional selection
            final_concepts = concept_scores[:top_k]
        
        # Define high_quality_concepts based on final_concepts
        high_quality_concepts = final_concepts
        
        # Define missing threshold variables
        core_threshold = 0.35
        primary_threshold = 0.50
        secondary_threshold = 0.40
        
        # Define core_concepts_under_threshold
        core_concepts_under_threshold = [(name, definition, score, is_core) for name, definition, score, is_core in concept_scores 
                                       if score >= core_threshold and is_core and score < primary_threshold]
        
        # Add concept relevance validation
        def is_concept_relevant_to_query(concept_name: str, query: str, concept_domain: str) -> bool:
            """Validate if a concept is actually relevant to the query."""
            query_lower = query.lower()
            
            # Domain-specific relevance checks
            if concept_domain == 'behavioral':
                # For behavioral queries, ensure concepts relate to human behavior/psychology
                # Use the main behavioral keywords from the three-tier system
                behavioral_keywords_check = ['critique', 'criticism', 'feedback', 'manager', 'employee', 'workplace', 'bias', 'judgment', 'thinking', 'behavior', 'reaction', 'response', 'unfair', 'unjust', 'boss', 'bad news']
                if any(keyword in query_lower for keyword in behavioral_keywords_check):
                    # Mental accounting is about money - not relevant for workplace feedback
                    if concept_name == 'mental accounting':
                        return False
                    # Framing bias is about how options are presented - very relevant for critiques
                    if concept_name == 'framing bias':
                        return True
                    # Confirmation bias is relevant for critiques and feedback
                    if concept_name == 'confirmation bias':
                        return True
                    # Anchoring bias is relevant for workplace feedback
                    if concept_name == 'anchoring bias':
                        return True
                    # Other behavioral concepts are generally relevant
                    return True
            
            return True  # Default to relevant for other domains
        
        # Apply relevance filtering
        relevant_concepts = []
        for name, definition, score, is_core in high_quality_concepts:
            concept_domain = CONCEPT_DOMAINS.get(name, 'general')
            if is_concept_relevant_to_query(name, query, concept_domain):
                relevant_concepts.append((name, definition, score, is_core))
        
        # If we don't have enough relevant concepts, include some from under threshold
        if len(relevant_concepts) < 2:
            for name, definition, score, is_core in core_concepts_under_threshold:
                concept_domain = CONCEPT_DOMAINS.get(name, 'general')
                if is_concept_relevant_to_query(name, query, concept_domain):
                    relevant_concepts.append((name, definition, score, is_core))
                    if len(relevant_concepts) >= 3:
                        break
        
        high_quality_concepts = relevant_concepts
        
        # Smart domain-based concept selection with proper allocation rules
        selected_concepts = []
        
        if query_domains:  # Multi-domain or single-domain query
            # Sort domains by score (highest first)
            sorted_domains = sorted(query_domains.items(), key=lambda x: x[1], reverse=True)
            
            # Check if this is effectively a single domain (one domain has >60% weight)
            primary_domain = sorted_domains[0][0]
            primary_score = sorted_domains[0][1]
            
            if primary_score > 0.5:  # Single domain (one domain dominates)
                # Single domain: up to 3 concepts from primary domain
                domain_concepts = [(name, definition) for name, definition, score, is_core in high_quality_concepts 
                                 if CONCEPT_DOMAINS.get(name, 'general') == primary_domain][:3]
                selected_concepts = domain_concepts
                
                # If we don't have enough concepts, add more from primary domain
                if len(selected_concepts) < 3:
                    additional_primary = [(name, definition) for name, definition, score, is_core in concept_scores 
                                        if score >= core_threshold and CONCEPT_DOMAINS.get(name, 'general') == primary_domain 
                                        and (name, definition) not in selected_concepts][:3-len(selected_concepts)]
                    selected_concepts.extend(additional_primary)
                
                # Special case: For visualization queries, include decision tree if it's not already selected
                if is_visualization_query:
                    decision_tree_concept = next((c for c in concept_scores if c[0] == 'decision tree' and c[2] >= 0.50), None)
                    if decision_tree_concept and ('decision tree', decision_tree_concept[1]) not in selected_concepts:
                        # Add decision tree and remove the weakest concept if we have 3 already
                        if len(selected_concepts) >= 3:
                            selected_concepts = selected_concepts[:2]  # Keep only top 2
                        selected_concepts.append(('decision tree', decision_tree_concept[1]))
                
                # Special case: For choice queries, include decision tree if it's not already selected
                if is_choice_query:
                    decision_tree_concept = next((c for c in concept_scores if c[0] == 'decision tree' and c[2] >= 0.45), None)
                    if decision_tree_concept and ('decision tree', decision_tree_concept[1]) not in selected_concepts:
                        # Add decision tree and remove the weakest concept if we have 3 already
                        if len(selected_concepts) >= 3:
                            selected_concepts = selected_concepts[:2]  # Keep only top 2
                        selected_concepts.append(('decision tree', decision_tree_concept[1]))
                
            else:  # Multiple domains (no single domain dominates)
                # Multi-domain: 2 from primary domain, +1 from each additional domain, hard cap = 4 total
                # Get up to 2 concepts from primary domain (>= primary_threshold)
                primary_concepts = [(name, definition) for name, definition, score, is_core in high_quality_concepts 
                                  if CONCEPT_DOMAINS.get(name, 'general') == primary_domain][:2]
                selected_concepts.extend(primary_concepts)
                
                # Get up to 1 concept from each additional domain (>= secondary_threshold)
                for domain_name, domain_score in sorted_domains[1:]:
                    if domain_score > 0.15:  # Only include domains with meaningful weight
                        domain_concepts = [(name, definition) for name, definition, score, is_core in concept_scores 
                                         if score >= secondary_threshold and CONCEPT_DOMAINS.get(name, 'general') == domain_name][:1]
                        selected_concepts.extend(domain_concepts)
                
                # Enforce hard total cap of 4 tooltips maximum
                if len(selected_concepts) > 4:
                    selected_concepts = selected_concepts[:4]
                
                # If we don't have enough concepts, add more from primary domain
                if len(selected_concepts) < 4:
                    additional_primary = [(name, definition) for name, definition, score, is_core in concept_scores 
                                        if score >= core_threshold and CONCEPT_DOMAINS.get(name, 'general') == primary_domain 
                                        and (name, definition) not in selected_concepts][:4-len(selected_concepts)]
                    selected_concepts.extend(additional_primary)
                
                # Special case: For choice queries, include decision tree if it's not already selected
                if is_choice_query:
                    decision_tree_concept = next((c for c in concept_scores if c[0] == 'decision tree' and c[2] >= 0.45), None)
                    if decision_tree_concept and ('decision tree', decision_tree_concept[1]) not in selected_concepts:
                        # Add decision tree and remove the weakest concept if we have 4 already
                        if len(selected_concepts) >= 4:
                            selected_concepts = selected_concepts[:3]  # Keep only top 3
                        selected_concepts.append(('decision tree', decision_tree_concept[1]))
                
        else:  # General query (no specific domains detected)
            # General domain: cap at 2 concepts
            general_concepts = [(name, definition) for name, definition, score, is_core in high_quality_concepts 
                              if CONCEPT_DOMAINS.get(name, 'general') == 'general'][:2]
            selected_concepts = general_concepts
        
        # Post-filter override for core concepts
        # If we have weak matches and a core concept scores ≥ 0.35, promote it
        if len(selected_concepts) < 2:
            for name, definition, score, is_core in concept_scores:
                if is_core and score >= core_threshold and (name, definition) not in selected_concepts:
                    # Check if this core concept is better than the weakest selected
                    if not selected_concepts or score > min(s for n, d, s, ic in concept_scores if (n, d) in selected_concepts):
                        if selected_concepts and len(selected_concepts) >= 2:
                            # Replace weakest concept
                            weakest_concept = min(selected_concepts, key=lambda x: next(s for n, d, s, ic in concept_scores if (n, d) == x))
                            selected_concepts.remove(weakest_concept)
                        
                        selected_concepts.append((name, definition))
                        break
        
        # Fallback: if insufficient high-quality concepts, use domain-appropriate fallbacks
        if len(selected_concepts) < 2:
            if query_domains:  # Only use domain-restrictive fallback if domains were detected
                # Use domain-appropriate fallback concepts from templates
                fallback_concepts = generate_fallback_concepts(query)
                selected_concepts = fallback_concepts
            else:
                # General query fallback - use top concepts regardless of domain
                if core_concepts_under_threshold:
                    # Include core concepts that are just under threshold
                    fallback_concepts = [(name, definition) for name, definition, score, is_core in concept_scores[:min(2, top_k)]]
                    # Replace weakest with core concept if available
                    if len(fallback_concepts) > 0 and core_concepts_under_threshold:
                        weakest_score = min(score for name, definition, score, is_core in concept_scores[:min(2, top_k)] if (name, definition) in fallback_concepts)
                        best_core = max(core_concepts_under_threshold, key=lambda x: x[2])
                        if best_core[2] > weakest_score:
                            # Replace weakest concept with best core concept
                            fallback_concepts = [(name, definition) for name, definition, score, is_core in concept_scores[:min(2, top_k)] 
                                               if score > weakest_score and (name, definition) in fallback_concepts]
                            fallback_concepts.append((best_core[0], best_core[1]))
                    selected_concepts = fallback_concepts
                else:
                    selected_concepts = [(name, definition) for name, definition, score, is_core in concept_scores[:min(2, top_k)]]
        
        # Deduplicate selected concepts by name (case-insensitive)
        seen_names = set()
        deduplicated_concepts = []
        for name, definition in selected_concepts:
            if name.lower() not in seen_names:
                deduplicated_concepts.append((name, definition))
                seen_names.add(name.lower())
        
        selected_concepts = deduplicated_concepts
        
        return selected_concepts
        
    except Exception as e:
        # Error in semantic concept extraction - fallback to fuzzy matching
        # Fallback to fuzzy matching if semantic extraction fails
        return extract_concepts_with_fuzzy_matching(query, threshold=0.7)

def select_concepts(concept_scores: List[Tuple[str, str, float]], selected_domains: dict, primary_domain: str) -> List[Tuple[str, str]]:
    """
    V1666.6 concept selection function implementing new thresholds and allocation rules.
    
    Args:
        concept_scores: List of (concept_name, definition, score) tuples sorted by score
        selected_domains: Dict of selected domains and their scores
        primary_domain: The primary domain for allocation rules
        
    Returns:
        List of (concept_name, definition) tuples for UI display
    """
    
    # Group concepts by domain
    concepts_by_domain = {}
    for concept_name, definition, score in concept_scores:
        concept_domain = CONCEPT_DOMAINS.get(concept_name.lower(), 'general')
        if concept_domain not in concepts_by_domain:
            concepts_by_domain[concept_domain] = []
        concepts_by_domain[concept_domain].append((concept_name, definition, score))
    
    # Sort concepts within each domain by score (highest first)
    for domain in concepts_by_domain:
        concepts_by_domain[domain].sort(key=lambda x: x[2], reverse=True)
    
    # V1666.6 THRESHOLD RULES
    # 1. Primary domain concepts: keep if score ≥ 0.50
    # 2. Secondary domain concepts: keep if score ≥ 0.45  
    # 3. Core concept "grace zone": if primary domain score ≥ 0.35 but < 0.50, allow inclusion
    # 4. Grace zone applies ONLY to primary domain concepts, never to secondary domains
    
    # Apply thresholds first
    filtered_concepts_by_domain = {}
    for domain, concepts in concepts_by_domain.items():
        filtered_concepts = []
        is_primary_domain = domain == primary_domain
        
        for concept_name, definition, score in concepts:
            # Check if concept meets thresholds
            if is_primary_domain:
                # Primary domain: score ≥ 0.50 OR (score ≥ 0.35 AND is core concept)
                if score >= 0.50:
                    filtered_concepts.append((concept_name, definition, score))
                elif score >= 0.35:
                    # Check if this is a core concept for grace zone
                    concept_data = CONCEPT_GLOSSARY.get(concept_name, {})
                    if isinstance(concept_data, dict) and concept_data.get("core", False):
                        filtered_concepts.append((concept_name, definition, score))
            else:
                # Secondary domain: score ≥ 0.45 (no grace zone)
                if score >= 0.45:
                    filtered_concepts.append((concept_name, definition, score))
        
        if filtered_concepts:
            filtered_concepts_by_domain[domain] = filtered_concepts
    
    # V1666.6 DISPERSION PENALTY (Domain Coherence Rule)
    # If there are ≥2 primary domain concepts with score ≥ 0.60:
    #   - Allow at most 1 secondary domain concept, even if others meet thresholds
    # If the primary domain is weak (no concept ≥ 0.50) and multiple secondary domains barely qualify (≥0.45):
    #   - Keep at most 1 secondary domain concept total
    
    primary_concepts = filtered_concepts_by_domain.get(primary_domain, [])
    high_scoring_primary = [c for c in primary_concepts if c[2] >= 0.60]
    
    if len(high_scoring_primary) >= 2:
        # Strong primary domain: limit secondary domains to 1 concept total
        secondary_domains = {k: v for k, v in filtered_concepts_by_domain.items() if k != primary_domain}
        if len(secondary_domains) > 1:
            # Keep only the highest scoring secondary domain concept
            best_secondary_concept = None
            best_secondary_score = 0
            best_secondary_domain = None
            
            for domain, concepts in secondary_domains.items():
                if concepts and concepts[0][2] > best_secondary_score:
                    best_secondary_concept = concepts[0]
                    best_secondary_score = concepts[0][2]
                    best_secondary_domain = domain
            
            # Replace secondary domains with just the best one
            if best_secondary_domain:
                filtered_concepts_by_domain = {k: v for k, v in filtered_concepts_by_domain.items() if k == primary_domain}
                filtered_concepts_by_domain[best_secondary_domain] = [best_secondary_concept]
    
    # Check for weak primary domain scenario
    primary_strong_concepts = [c for c in primary_concepts if c[2] >= 0.50]
    if not primary_strong_concepts:
        # Weak primary domain: limit to 1 secondary domain concept total
        secondary_domains = {k: v for k, v in filtered_concepts_by_domain.items() if k != primary_domain}
        if len(secondary_domains) > 1:
            # Keep only the highest scoring secondary domain concept
            best_secondary_concept = None
            best_secondary_score = 0
            best_secondary_domain = None
            
            for domain, concepts in secondary_domains.items():
                if concepts and concepts[0][2] > best_secondary_score:
                    best_secondary_concept = concepts[0]
                    best_secondary_score = concepts[0][2]
                    best_secondary_domain = domain
            
            # Replace secondary domains with just the best one
            if best_secondary_domain:
                filtered_concepts_by_domain = {k: v for k, v in filtered_concepts_by_domain.items() if k == primary_domain}
                filtered_concepts_by_domain[best_secondary_domain] = [best_secondary_concept]
    
    # V1666.6 ALLOCATION RULES
    # Single-domain lens: up to 3 tooltips
    # Multi-domain lens: 2 from the primary domain, +1 from each additional domain
    # Hard cap: 4 total concepts
    
    selected_concepts = []
    
    if len(filtered_concepts_by_domain) == 1:
        # Single domain lens: up to 3 concepts
        domain = list(filtered_concepts_by_domain.keys())[0]
        domain_concepts = filtered_concepts_by_domain[domain]
        selected_concepts = [(name, definition) for name, definition, score in domain_concepts[:3]]
    else:
        # Multi-domain lens: 2 from primary + 1 from each additional domain
        domain_list = list(filtered_concepts_by_domain.keys())
        if primary_domain in domain_list:
            # Primary domain: up to 2 concepts
            primary_concepts = filtered_concepts_by_domain[primary_domain]
            selected_concepts = [(name, definition) for name, definition, score in primary_concepts[:2]]
            
            # Additional domains: 1 concept each
            for domain in domain_list:
                if domain != primary_domain:
                    domain_concepts = filtered_concepts_by_domain[domain]
                    if domain_concepts:
                        selected_concepts.append((domain_concepts[0][0], domain_concepts[0][1]))
        else:
            # Fallback if primary domain not in filtered results
            for domain in domain_list:
                domain_concepts = filtered_concepts_by_domain[domain]
                if domain_concepts:
                    selected_concepts.append((domain_concepts[0][0], domain_concepts[0][1]))
                    break  # Take first available domain
    
    # V1666.6 HARD CAP: 4 total concepts maximum
    selected_concepts = selected_concepts[:4]
    
    # V1666.6 DEDUPLICATION: Deduplicate for clarity
    seen_names = set()
    deduplicated_concepts = []
    for name, definition in selected_concepts:
        normalized_name = name.lower().replace('-', ' ').replace('_', ' ')
        if normalized_name not in seen_names:
            deduplicated_concepts.append((name, definition))
            seen_names.add(normalized_name)
    
    return deduplicated_concepts

def extract_concepts_with_fuzzy_matching(text: str, threshold: float = 0.8) -> List[Tuple[str, str]]:
    """
    Extract concepts from text using fuzzy string matching against the concept glossary.
    
    Args:
        text: The text to search for concepts
        threshold: Minimum similarity score (0.0 to 1.0) for fuzzy matching
        
    Returns:
        List of (concept_name, definition) tuples
    """
    import difflib
    
    # Normalize text for searching
    text_lower = text.lower()
    text_words = re.findall(r'\b\w+\b', text_lower)
    
    found_concepts = []
    used_concepts = set()
    
    # First, try exact matches
    for concept_name, definition in CONCEPT_GLOSSARY.items():
        if concept_name in text_lower and concept_name not in used_concepts:
            found_concepts.append((concept_name.title(), definition))
            used_concepts.add(concept_name)
    
    # Then try fuzzy matching for remaining concepts
    concept_names = list(CONCEPT_GLOSSARY.keys())
    for concept_name in concept_names:
        if concept_name in used_concepts:
            continue
            
        # Try to find similar concepts in the text
        matches = difflib.get_close_matches(concept_name, text_words, n=1, cutoff=threshold)
        if matches:
            matched_word = matches[0]
            # Check if the matched word appears in a meaningful context
            if len(matched_word) > 3:  # Avoid very short matches
                found_concepts.append((concept_name.title(), CONCEPT_GLOSSARY[concept_name]))
                used_concepts.add(concept_name)
    
    # Enhanced multi-word concept pattern matching
    for concept_name in concept_names:
        if concept_name in used_concepts:
            continue
            
        # Split multi-word concepts and check for partial matches
        concept_words = concept_name.split()
        if len(concept_words) > 1:
            # Check if most words in the concept appear in the text
            matching_words = sum(1 for word in concept_words if word in text_words)
            if matching_words >= len(concept_words) * 0.7:  # 70% of words must match
                found_concepts.append((concept_name.title(), CONCEPT_GLOSSARY[concept_name]))
                used_concepts.add(concept_name)
    
    # Additional pattern matching for common variations
    for concept_name in concept_names:
        if concept_name in used_concepts:
            continue
            
        # Check for singular/plural variations and common word forms
        concept_words = concept_name.split()
        for i, word in enumerate(concept_words):
            # Check singular/plural variations
            if word.endswith('s'):
                singular = word[:-1]
                if singular in text_words:
                    matching_words = sum(1 for w in concept_words if w in text_words or (w.endswith('s') and w[:-1] in text_words))
                    if matching_words >= len(concept_words) * 0.6:  # 60% of words must match
                        found_concepts.append((concept_name.title(), CONCEPT_GLOSSARY[concept_name]))
                        used_concepts.add(concept_name)
                        break
            else:
                plural = word + 's'
                if plural in text_words:
                    matching_words = sum(1 for w in concept_words if w in text_words or (w + 's') in text_words)
                    if matching_words >= len(concept_words) * 0.6:  # 60% of words must match
                        found_concepts.append((concept_name.title(), CONCEPT_GLOSSARY[concept_name]))
                        used_concepts.add(concept_name)
                        break
    
    # Special case matching for common variations
    special_matches = {
        "risk models": "risk assessment",
        "risk modeling": "risk assessment", 
        "risk analysis": "risk assessment",
        "scenario paths": "scenario planning",
        "scenario analysis": "scenario planning",
        "contingency plans": "contingency planning",
        "contingency strategies": "contingency planning"
    }
    
    for text_phrase, concept_key in special_matches.items():
        if text_phrase in text_lower and concept_key not in used_concepts:
            found_concepts.append((concept_key.title(), CONCEPT_GLOSSARY[concept_key]))
            used_concepts.add(concept_key)
    
    return found_concepts 

# ============================================================================
# LEGACY CODE CLEANUP - V1666.6 One-Call System
# ============================================================================
# The following legacy functions were removed during cleanup (2025-09-18):
# - SYSTEM_PROMPT_ANALYTICS: Replaced by one-call system prompt in generate_answer_one_call
# - calculate_optimal_tokens: Not used in one-call system
# - robust_api_call: Replaced by generate_answer_with_retry in one-call system  
# - merge_and_extend_with_story: Not used in one-call system
# - context_aware_fallbacks: Not used in one-call system
# - extract_sections_from_response: Not used in one-call system
# - format_fallback_response: Not used in one-call system
# - enforce_thinkpal_structure: Not used in one-call system
# 
# The current system uses:
# - generate_answer_one_call: Main one-call GPT integration
# - parse_gpt_output: Natural language to JSON parsing
# - validate_answer: Quality validation with retry logic
# - generate_answer_with_retry: Robust API calling with validation
# ============================================================================

def smart_context_truncation(docs: list, max_chars: int = 8000) -> str:
    """Smart context truncation with sentence boundaries"""
    combined = " ".join(docs)
    if len(combined) <= max_chars:
        return combined
    
    # Find sentence boundaries
    sentences = re.split(r'(?<=[.!?]) +', combined)
    truncated = ""
    
    for sentence in sentences:
        if len(truncated + sentence) <= max_chars:
            truncated += sentence + " "
        else:
            break
    
    return truncated.strip()

# Legacy calculate_optimal_tokens removed - not used in one-call system

# Legacy robust_api_call removed - replaced by generate_answer_with_retry in one-call system

# Legacy merge_and_extend_with_story removed - not used in one-call system

def clean_concepts_tools_practice(raw_items):
    """Ensure conceptsToolsPractice is always a list of {term, definition} objects with non-empty, non-placeholder definitions."""
    cleaned = []
    if not isinstance(raw_items, list):
        return []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        if 'term' not in item or 'definition' not in item:
            continue
        if not isinstance(item['term'], str) or not isinstance(item['definition'], str):
            continue
        term = item['term'].strip()
        definition = item['definition'].strip()
        if not term or len(term) < 2:
            continue
        if '<' in term or '>' in term:
            continue
        if not definition:
            continue
        placeholder_patterns = [
            '(no definition available)',
            'no content available.',
            'no definition available',
            'no definition',
            'undefined',
            'n/a',
            'tbd',
            'to be determined'
        ]
        if any(pattern in definition.lower() for pattern in placeholder_patterns):
            continue
        if '<' in definition or '>' in definition:
            continue
        cleaned.append({
            'term': term,
            'definition': definition
        })
    return cleaned

def strip_html_from_markdown(markdown_content: str) -> str:
    """Strip HTML tags from markdown content while preserving the text content."""
    # Remove tooltip spans but keep the inner text
    # Pattern: <span class="tooltip" data-tooltip="...">text</span> -> text
    markdown_content = re.sub(r'<span class="tooltip" data-tooltip="[^"]*">([^<]+)</span>', r'\1', markdown_content)
    
    # Remove any other HTML tags that might be present
    markdown_content = re.sub(r'<[^>]+>', '', markdown_content)
    
    # Clean up any extra whitespace that might result from tag removal
    markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
    
    return markdown_content

def normalize_tool_name(raw: str) -> str:
    """Normalize tool names for consistent matching with PREBUILT_TOOLTIPS."""
    # Remove markdown formatting (** or __)
    normalized = re.sub(r'\*\*|__', '', raw)
    # Strip leading/trailing spaces and collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized.strip())
    # Convert to lowercase for case-insensitive matching
    return normalized.lower()

def parse_tooltip_spans(content: str) -> list:
    """Parse tooltip spans from content and extract term/definition pairs."""
    concepts_tools = []
    # Pattern to match tooltip spans: <span class="tooltip" data-tooltip="Definition">Term</span>
    tooltip_pattern = r'<span class="tooltip" data-tooltip="([^"]+)">([^<]+)</span>'
    
    matches = re.findall(tooltip_pattern, content)
    for definition, term in matches:
        term = term.strip()
        definition = definition.strip()
        if term and definition and len(term) > 2:
            concepts_tools.append({
                "term": term,
                "definition": definition
            })
    return concepts_tools

def extract_tools_from_section(content: str, selected_domains: dict = None) -> list:
    concepts_tools = []
    section_match = re.search(r'\*\*Concepts/Tools\*\*', content, re.IGNORECASE)
    if not section_match:
        return []
    start_pos = section_match.end()
    tool_section = content[start_pos:].strip()
    
    # First, try to parse tooltip spans
    tooltip_concepts = parse_tooltip_spans(tool_section)
    concepts_tools.extend(tooltip_concepts)
    tooltip_terms = {item['term'].lower() for item in tooltip_concepts}
    
    # Parse the standard format: "Concept Name: Definition"
    # Modified to exclude bullet points to prevent duplicate extraction
    concept_lines = re.findall(r'^(?![-*]\s)([^:\n]+?):\s*([^\n]+)$', tool_section, re.MULTILINE)
    for concept_name, definition in concept_lines:
        concept_name = concept_name.strip()
        definition = definition.strip()
        
        # Skip if already found in tooltips
        if concept_name.lower() in tooltip_terms:
            continue
            
        # Skip if concept name is too short
        if len(concept_name) < 3:
            continue
            
        # Clean up the concept name
        clean_term = re.sub(r'\*\*|__', '', concept_name.strip())
        
        # V1.6.6 fix: Enforce domain filtering if selected_domains provided
        if selected_domains:
            concept_domain = CONCEPT_DOMAINS.get(clean_term.lower(), 'general')
            if concept_domain not in selected_domains:
                continue  # Skip concepts not from detected domains
        
        concepts_tools.append({
            "term": clean_term,
            "definition": definition
        })
    
    # Also try the old bullet point format as fallback
    tool_lines = re.findall(r'[-*]\s*([^:\n]+?)(?:\s*:\s*([^\n]+))?\s*$', tool_section, re.MULTILINE)
    numbered_lines = re.findall(r'\d+\.\s*([^:\n]+?)(?:\s*:\s*([^\n]+))?\s*$', tool_section, re.MULTILINE)
    tool_lines.extend(numbered_lines)
    
    for tool_name, tool_def in tool_lines:
        tool_name = tool_name.strip()
        if tool_name.lower() in tooltip_terms:
            continue
        
        # V1.6.6 fix: Enforce domain filtering if selected_domains provided
        if selected_domains:
            concept_domain = CONCEPT_DOMAINS.get(tool_name.lower(), 'general')
            if concept_domain not in selected_domains:
                continue  # Skip concepts not from detected domains
        
        if tool_def and tool_def.strip():
            definition = tool_def.strip()
        else:
            # Use concept glossary for definition
            concept_key = tool_name.lower().replace(' ', ' ')
            if concept_key in CONCEPT_GLOSSARY:
                concept_data = CONCEPT_GLOSSARY[concept_key]
                if isinstance(concept_data, dict):
                    definition = concept_data["definition"]
                else:
                    definition = concept_data
            else:
                continue
        if tool_name and len(tool_name) > 2:
            clean_term = re.sub(r'\*\*|__', '', tool_name.strip())
            concepts_tools.append({"term": clean_term, "definition": definition})
    
    cleaned_concepts = clean_concepts_tools_practice(concepts_tools)
    return cleaned_concepts

def extract_concepts_from_markdown(text: str) -> list:
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    concepts = []
    for line in lines:
        match = re.match(r'^(.+?):\s*(.+)$', line)
        if match:
            concept = match.group(1).strip()
            definition = match.group(2).strip()
            if len(concept) > 2 and len(definition) > 5:
                concepts.append((concept, definition))
    return concepts

def generate_fallback_concepts(query: str) -> List[str]:
    """Simplified fallback function - returns empty list since we use unified concept extraction."""
    return []

def deduplicate_concepts(concepts_section: str) -> str:
    """
    Remove duplicate concepts (case-insensitive) and limit to maximum 5 unique concepts.
    Preserves original order of appearance.
    
    Args:
        concepts_section: The Concepts/Tools section content
        
    Returns:
        Deduplicated and limited concepts section
    """
    lines = [line.strip() for line in concepts_section.strip().split('\n') if line.strip()]
    seen_concepts = set()
    deduplicated_lines = []
    
    for line in lines:
        if ':' not in line:
            continue
            
        # Extract concept name (before the first colon)
        concept_name = line.split(':', 1)[0].strip().lower()
        
        # Skip if we've already seen this concept (case-insensitive)
        if concept_name in seen_concepts:
            continue
            
        # Add to seen set and keep the line
        seen_concepts.add(concept_name)
        deduplicated_lines.append(line)
        
        # Stop after 5 unique concepts
        if len(deduplicated_lines) >= 5:
            break
    
    return '\n'.join(deduplicated_lines) 

def extract_application_field(query: str) -> str:
    """Infer the application field/type from the query for context-aware answer generation."""
    q = query.lower()
    
    # 8. Product Development & Innovation (check first to avoid conflicts)
    if any(word in q for word in ["product", "design", "prototype", "testing", "features", "roadmap", "user feedback"]):
        return "product_development_innovation"
    
    # 4. Technology Management (check before business to avoid conflicts)
    tech_keywords = ["technology", "digital", "software", "platform", "artificial intelligence", "automation", "cybersecurity", "data science"]
    # Special case for AI - check as whole word
    if any(word in q for word in tech_keywords) or ' ai ' in f' {q} ' or q.startswith('ai ') or q.endswith(' ai'):
        return "technology_management"
    
    # 3. Financial Decision-Making (check before business to avoid conflicts)
    if any(word in q for word in ["invest", "investment", "financial", "budget", "cost", "pricing", "valuation", "capital", "funding", "expenses", "profitability"]):
        return "financial_decision_making"
    
    # 10. Education & Learning (check before general terms)
    if any(word in q for word in ["education", "learning", "school", "teaching", "curriculum", "training", "students"]):
        return "education_learning"
    
    # 6. People, Talent & Career (check before general business terms)
    if any(word in q for word in ["hire", "hiring", "recruitment", "employee", "staff", "team", "leadership", "management", "culture", "retention", "job", "offer", "employment", "career", "salary", "compensation", "benefits", "talent"]):
        return "people_talent_career"
    
    # 1. Business & Markets
    if any(word in q for word in ["business", "company", "market", "competition", "growth", "branding", "marketing", "customer", "sales", "revenue", "profit"]):
        return "business_markets"
    
    # 2. Operations Management
    if any(word in q for word in ["production", "operations", "logistics", "supply", "manufacturing", "inventory", "process", "workflow"]):
        return "operations_management"
    
    # 5. Risk, Crisis & Resilience
    if any(word in q for word in ["risk", "uncertainty", "volatile", "unpredictable", "threat", "mitigation", "contingency", "disaster", "emergency", "safety", "resilience"]):
        return "risk_crisis_resilience"
    
    # 7. Policy & Regulatory
    if any(word in q for word in ["policy", "regulation", "compliance", "legal", "government", "legislation", "standards", "ethics"]):
        return "policy_regulatory"
    
    # 9. Sustainability & Environment
    if any(word in q for word in ["sustainability", "environmental", "climate", "carbon", "renewable", "conservation", "green"]):
        return "sustainability_environment"
    
    # 11. Healthcare & Medical
    if any(word in q for word in ["healthcare", "medical", "patient", "treatment", "diagnosis", "clinical", "hospital", "therapy"]):
        return "healthcare_medical"
    
    # 12. Military & Defense Decisions
    if any(word in q for word in ["military", "defense", "army", "navy", "air force", "marine", "security", "mission", "tactical", "combat", "deployment", "training exercise"]):
        return "military_defense"
    
    # 13. General Decision-Making (default)
    return "general"

# Legacy context_aware_fallbacks removed - not used in one-call system

def generate_course_domain_strategic_lens(query: str, course_domain: str, application_field: str = None) -> str:
    """Generate strategic lens based on course domain and application field."""
    
    # Base strategic lens templates by domain
    domain_lenses = {
        'behavioral': "Consider the human factors that influence decision-making, including cognitive biases, emotional responses, and social dynamics. Think about how different stakeholders might perceive and react to various options, and how group dynamics could affect the outcome. Balance rational analysis with an understanding of human behavior patterns.",
        
        'technical': "Apply systematic analytical frameworks to structure your decision-making process. Consider quantitative factors like costs, benefits, and probabilities, while also accounting for qualitative aspects like stakeholder impact and long-term implications. Use data-driven approaches to evaluate options objectively.",
        
        'strategic': "Think long-term and consider how this decision fits into broader strategic objectives. Evaluate not just immediate outcomes but also how this choice positions you for future opportunities and challenges. Consider competitive dynamics and how this decision might create or sustain competitive advantages.",
        
        'negotiation': "Approach this as a collaborative problem-solving opportunity where multiple parties have interests to balance. Consider what each stakeholder values most and how you can create value for all parties. Think about your alternatives and the other party's alternatives to understand the zone of possible agreement.",
        
        'general': "Structure your decision-making process systematically by clarifying your objectives, identifying key criteria, and evaluating alternatives against those criteria. Consider both immediate and long-term implications, and balance competing priorities thoughtfully."
    }
    
    # Get base lens for the domain
    base_lens = domain_lenses.get(course_domain, domain_lenses['general'])
    
    # Add application field specific considerations
    if application_field:
        field_considerations = {
            'people_talent_career': " Consider how this decision aligns with your career trajectory and personal values.",
            'startup': " Evaluate both the immediate feasibility and long-term growth potential of each option.",
            'financial_decision_making': " Balance risk and return while considering your financial goals and constraints.",
            'operations_management': " Consider both efficiency and resilience in your analysis.",
            'healthcare_medical': " Prioritize both immediate needs and long-term well-being.",
            'education_learning': " Weigh the investment in time and money against potential career benefits.",
            'relocation': " Consider both personal and professional factors in your decision.",
            'leadership': " Think about how this decision will affect team dynamics and organizational culture.",
            'ethics': " Consider the moral implications and stakeholder impact of your choice.",
            'business_markets': " Evaluate both short-term operational efficiency and long-term strategic positioning.",
            'technology_management': " Balance innovation potential with implementation challenges and user adoption.",
            'risk_crisis_resilience': " Consider both probability and impact in your risk assessment.",
            'project_management': " Balance scope, time, and cost constraints while maintaining quality.",
            'sustainability_environment': " Consider environmental, social, and governance factors alongside business objectives.",
            'innovation': " Balance breakthrough potential with implementation risk and market readiness.",
            'human_capital': " Consider both individual development and organizational needs.",
            'marketing': " Balance short-term sales targets with long-term brand building.",
            'globalization': " Consider cultural, political, and economic factors in different markets.",
            'admission': " Consider both academic fit and long-term career implications."
        }
        
        if application_field in field_considerations:
            base_lens += field_considerations[application_field]
    
    return base_lens

def generate_domain_aware_fallback_questions(query: str, domain: str) -> list:
    """Generate domain-aware fallback questions."""
    questions = []
    
    if domain == "job":
        questions = [
            "- How does this align with your long-term career goals?",
            "- What trade-offs exist between immediate benefits and future opportunities?",
            "- How might this decision affect your work-life balance?"
        ]
    elif domain == "startup":
        questions = [
            "- What is your risk tolerance for this decision?",
            "- How does this align with your vision for the company?",
            "- What resources and capabilities do you need to succeed?"
        ]
    elif domain == "finance":
        questions = [
            "- What is your time horizon for this investment?",
            "- How does this fit into your overall financial plan?",
            "- What is your comfort level with the associated risks?"
        ]
    elif domain == "operations":
        questions = [
            "- How might this decision affect your operational efficiency?",
            "- What contingency plans should you have in place?",
            "- How will this impact your stakeholders?"
        ]
    else:
        questions = [
            "- What are your main objectives in this decision?",
            "- What trade-offs exist between your options?",
            "- How might this decision affect others?"
        ]
    
    return questions

# Legacy extract_sections_from_response removed - not used in one-call system

def analyze_query_context(query_lower):
    """Analyze the semantic context of a query to identify decision-making scenarios."""
    context = {
        'decision_type': 'general',
        'scope': 'single',
        'domain': 'general',
        'urgency': 'normal'
    }
    
    # Decision type analysis
    if any(word in query_lower for word in ['job', 'offer', 'career', 'employment', 'hire', 'position']):
        context['decision_type'] = 'career'
    elif any(word in query_lower for word in ['bid', 'auction', 'tender', 'proposal', 'contract']):
        context['decision_type'] = 'bidding'
    elif any(word in query_lower for word in ['investment', 'portfolio', 'stock', 'bond', 'financial']):
        context['decision_type'] = 'investment'
    elif any(word in query_lower for word in ['project', 'initiative', 'program', 'campaign']):
        context['decision_type'] = 'project'
    elif any(word in query_lower for word in ['production', 'manufacturing', 'supply', 'operations']):
        context['decision_type'] = 'operations'
    
    # Scope analysis
    if any(word in query_lower for word in ['multiple', 'several', 'many', 'portfolio', 'array']):
        context['scope'] = 'multiple'
    elif any(word in query_lower for word in ['two', 'between', 'choose between', 'either']):
        context['scope'] = 'binary'
    
    # Domain analysis
    if any(word in query_lower for word in ['negotiate', 'bargain', 'deal', 'agreement']):
        context['domain'] = 'negotiation'
    elif any(word in query_lower for word in ['strategy', 'strategic', 'competitive', 'market']):
        context['domain'] = 'strategic'
    elif any(word in query_lower for word in ['bias', 'behavior', 'psychology', 'cognitive']):
        context['domain'] = 'behavioral'
    elif any(word in query_lower for word in ['model', 'analysis', 'quantitative', 'optimization']):
        context['domain'] = 'technical'
    
    return context

def analyze_concept_context(concept_name, definition):
    """Analyze the semantic context of a concept based on its definition."""
    context = {
        'decision_type': 'general',
        'scope': 'general',
        'domain': 'general',
        'specificity': 'general'
    }
    
    definition_lower = definition.lower()
    
    # Decision type analysis based on definition
    if any(word in definition_lower for word in ['bid', 'auction', 'tender', 'proposal', 'competitive bidding']):
        context['decision_type'] = 'bidding'
    elif any(word in definition_lower for word in ['job', 'career', 'employment', 'position', 'hiring']):
        context['decision_type'] = 'career'
    elif any(word in definition_lower for word in ['investment', 'portfolio', 'financial', 'asset']):
        context['decision_type'] = 'investment'
    elif any(word in definition_lower for word in ['project', 'initiative', 'program', 'multiple projects']):
        context['decision_type'] = 'project'
    elif any(word in definition_lower for word in ['production', 'manufacturing', 'supply', 'operations']):
        context['decision_type'] = 'operations'
    
    # Scope analysis
    if any(word in definition_lower for word in ['multiple', 'portfolio', 'array', 'collection', 'set of']):
        context['scope'] = 'multiple'
    elif any(word in definition_lower for word in ['single', 'individual', 'one', 'specific']):
        context['scope'] = 'single'
    elif any(word in definition_lower for word in ['two', 'between', 'either', 'choice between']):
        context['scope'] = 'binary'
    
    # Specificity analysis
    if any(word in definition_lower for word in ['specific', 'particular', 'narrow', 'focused']):
        context['specificity'] = 'specific'
    elif any(word in definition_lower for word in ['general', 'broad', 'universal', 'applicable']):
        context['specificity'] = 'general'
    
    return context

def calculate_context_penalty(query_context, concept_context):
    """Calculate penalty based on semantic context mismatch."""
    penalty = 0.0
    
    # Decision type mismatch penalty
    if query_context['decision_type'] != 'general' and concept_context['decision_type'] != 'general':
        if query_context['decision_type'] != concept_context['decision_type']:
            penalty += 0.12  # Moderate penalty for decision type mismatch
    
    # Scope mismatch penalty (only for specific decision types)
    if query_context['decision_type'] in ['career', 'investment', 'project']:
        if query_context['scope'] == 'binary' and concept_context['scope'] == 'multiple':
            penalty += 0.08  # Penalty for multi-scope concept in binary decision
        elif query_context['scope'] == 'multiple' and concept_context['scope'] == 'binary':
            penalty += 0.05  # Smaller penalty for binary concept in multi-scope decision
    
    # Domain mismatch penalty (only if both are specific)
    if query_context['domain'] != 'general' and concept_context['domain'] != 'general':
        if query_context['domain'] != concept_context['domain']:
            penalty += 0.06  # Small penalty for domain mismatch
    
    return min(penalty, 0.20)  # Cap penalty at 0.20

def parse_gpt_output(raw_text, application_field, model, elapsed):
    """Parse natural language GPT output into structured JSON format.
    Robustly extracts follow-up prompts across bullets, numbering, and question-mark sentences.
    """
    try:
        text = (raw_text or "").strip()
        if not text:
            return {"error": "Server issue, please try again later."}

        prompts: list[str] = []
        prompt_indices: list[int] = []

        bullet_pattern = re.compile(r'^[\-•\*]\s*(.+)')
        numbered_pattern = re.compile(r'^(?:\d+\.|\d+\))\s*(.+)')
        question_line_pattern = re.compile(r'^(.+\?)$')
        interrogatives = {"how", "what", "why", "which", "where", "who", "when"}

        label_match = re.search(r"\bfollow[-\s]?up\b[^\n]*prompts?\b[:]?", text, re.IGNORECASE)
        if label_match:
            lens_text_raw = text[:label_match.start()].rstrip()
            candidate_prompt_text = text[label_match.end():].strip()
        else:
            last_blank = text.rfind("\n\n")
            if last_blank != -1:
                lens_text_raw = text[:last_blank].rstrip()
                candidate_prompt_text = text[last_blank + 2:].strip()
            else:
                lens_text_raw = text
                candidate_prompt_text = ""

        candidate_lines = [ln.rstrip() for ln in candidate_prompt_text.splitlines()] if candidate_prompt_text else []
        offset_base = text.find(candidate_prompt_text) if candidate_prompt_text else len(text)

        for ln in candidate_lines:
            stripped = ln.strip()
            if not stripped:
                offset_base += len(ln) + 1
                continue
            m = bullet_pattern.match(stripped) or numbered_pattern.match(stripped) or question_line_pattern.match(stripped)
            if not m:
                offset_base += len(ln) + 1
                continue
            candidate = m.group(1).strip() if m else stripped
            if not candidate.endswith('?') or len(candidate) < 5:
                offset_base += len(ln) + 1
                continue
            first_word = candidate.split()[0].lower()
            if first_word not in interrogatives:
                offset_base += len(ln) + 1
                continue
            prompts.append(candidate)
            idx = text.find(stripped, offset_base)
            if idx != -1:
                prompt_indices.append(idx)
            offset_base += len(ln) + 1

        if not prompts and candidate_prompt_text:
            filtered = []
            for ln in candidate_lines:
                s = ln.strip()
                if not (s.endswith('?') and len(s) >= 5):
                    continue
                first_word = s.split()[0].lower() if s.split() else ""
                if first_word in interrogatives:
                    filtered.append(s)
            if len(filtered) >= 2:
                prompts.extend(filtered)

        question_pattern = re.compile(r'(?:^|[\s"“"\'\-])((?:How|What|Why|Which|Who|Where|When)[^?]*\?)', re.IGNORECASE)

        if not prompts:
            tail_text = candidate_prompt_text or text
            matches = question_pattern.findall(tail_text)
            prompts = [m.strip() for m in matches if m and len(m.strip()) >= 5]

        # Normalize candidates: split concatenated questions and remove prefacing narration
        normalized = []
        seen = set()
        for candidate in prompts:
            matches = question_pattern.findall(candidate)
            if matches:
                for q in matches:
                    cleaned = q.strip()
                    if cleaned and cleaned.lower() not in seen:
                        if not cleaned.endswith('?'):
                            cleaned += '?'
                        normalized.append(cleaned)
                        seen.add(cleaned.lower())
            else:
                cleaned = candidate.strip()
                if cleaned and cleaned.lower() not in seen:
                    if not cleaned.endswith('?'):
                        cleaned += '?'
                    normalized.append(cleaned)
                    seen.add(cleaned.lower())
        prompts = normalized

        # 3) Normalize count to 2–4 when possible
        if len(prompts) >= 5:
            prompts = prompts[:4]
        elif len(prompts) == 1:
            # Try to split by '?' inside the last paragraph to find more
            tail = text[text.rfind('\n\n') + 2 if '\n\n' in text else 0:]
            extras = [s.strip() + '?' for s in tail.split('?') if s.strip()]
            for ex in extras:
                if ex not in prompts and ex.endswith('?') and len(ex) >= 5:
                    prompts.append(ex)
                if len(prompts) >= 2:
                    break
        # Keep 2–4 prompts if available; if only one or zero, keep whatever we have
        if len(prompts) > 4:
            prompts = prompts[:4]

        # 4) Determine strategic lens boundary (before first prompt occurrence)
        if prompt_indices:
            lens_end = min(prompt_indices)
            strategic_lens = text[:lens_end].strip()
        else:
            strategic_lens = lens_text_raw.strip()

        # Safety fallback: if lens accidentally empty but we have content, take first two paragraphs
        if not strategic_lens:
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            strategic_lens = '\n\n'.join(parts[:2]).strip() if parts else text

        return {
            "strategicThinkingLens": strategic_lens,
            "followUpPrompts": prompts,
            "applicationField": application_field,
            "model": model,
            "processing_time": round(elapsed, 2)
        }
    except Exception:
        return {"error": "Server issue, please try again later."}

def validate_answer(parsed_output, require_behavioral: bool = False):
    """Validation aligned to Phase II policy.
    Accept answers ≥180 words as valid if key requirements are present.
    Retry only if <150 words or missing key requirements (example, behavioral cue when required).
    """
    lens = parsed_output.get("strategicThinkingLens", "")
    text_lower = lens.lower()
    word_count = len(lens.split())

    # Key requirements
    has_example = any(kw in text_lower for kw in [
        "for example", "for instance", "consider", "imagine", "case study"
    ])
    has_behavioral = (not require_behavioral) or any(
        kw in text_lower for kw in ["bias", "intuition", "overconfidence", "risk tolerance", "judgment"]
    )

    # Validity: ≥180 words and required cues present
    is_valid = (word_count >= 180) and has_example and has_behavioral

    # Retry condition: very short OR missing key cues
    should_retry = (word_count < 150) or (not has_example) or (require_behavioral and not has_behavioral)

    reason = (
        "Quality check passed" if is_valid else
        f"Validation: words={word_count}, has_example={has_example}, has_behavioral={has_behavioral}, should_retry={should_retry}"
    )
    return is_valid, should_retry, reason

def generate_answer_with_retry(user_prompt, base_prompt, require_behavioral=False, concepts=None, application_field="general", start_time=None):
    """Clean retry logic with quality validation"""
    system_prompt = base_prompt
    
    for attempt in range(2):  # First attempt + one retry
        try:
            # Use legacy OpenAI v0.28 API for Lambda compatibility
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6 if attempt == 0 else 0.8,
                max_tokens=1600
            )
            raw_output = response["choices"][0]["message"]["content"]
            
            # Parse natural language output instead of JSON
            parsed_output = parse_gpt_output(
                raw_output,
                application_field,
                "gpt-3.5-turbo",
                time.time() - (start_time or time.time())
            )
            
            # Validate quality with Phase II policy
            is_valid, should_retry, reason = validate_answer(parsed_output, require_behavioral)
            print(f"Validation attempt {attempt}: {reason}")
            if is_valid:
                return parsed_output
            elif attempt == 0 and should_retry:
                # Add reinforcement for retry
                system_prompt += """

IMPORTANT: Expand further. Minimum 250 words required.
Include a 6–8 sentence example (~100 words) woven naturally into the narrative.

CRITICAL: Maintain natural, conversational language. Avoid these mechanical patterns:
- "When facing X, it's essential to Y"
- "It is crucial to..."
- "One effective strategy is..."
- "Another valuable strategy is..."

Write like you're talking to a friend, not a textbook. Use contractions and natural flow.
"""
                continue  # Try retry
            else:
                # Either not eligible for retry or retry already used; return best-effort
                print(f"Returning best-effort answer. Reason: {reason}")
                return parsed_output
                
        except Exception as e:
            print(f"Exception in generate_answer_with_retry (attempt {attempt}): {e}")
            import traceback
            traceback.print_exc()
            if attempt == 0:
                continue  # Try retry
            # Final fallback: return a minimal best-effort structured answer instead of error
            fallback_lens = (
                "Here is a concise, practical answer focused on decisions, trade-offs, and next steps. "
                "Prioritize clarity of objectives, map options with consequences, and choose the highest-value path under constraints. "
                "Use a short example to ground the guidance, then identify two concrete actions to move forward."
            )
            fallback_followups = [
                "Which objectives matter most in this situation?",
                "What are the top two options and their biggest trade-offs?",
                "What evidence would most reduce uncertainty before committing?"
            ]
            return {
                "strategicThinkingLens": fallback_lens,
                "followUpPrompts": fallback_followups,
                "conceptsToolsPractice": concepts or [],
                "applicationField": application_field,
                "model": "gpt-3.5-turbo",
                "processing_time": round(time.time() - (start_time or time.time()), 2)
            }
    
    # Final safety net: return minimal structured answer instead of error
    fallback_followups = [
        "Which objective is most important right now?",
        "What are the top two options and key trade-offs?",
        "What evidence would most reduce uncertainty?"
    ]
    return {
        "strategicThinkingLens": (
            "Here is a concise best-effort answer focusing on objectives, options, and next steps. "
            "Clarify what success looks like, compare consequences across choices, and take a reversible next step."
        ),
        "followUpPrompts": fallback_followups,
        "conceptsToolsPractice": concepts or [],
        "applicationField": application_field,
        "model": "gpt-3.5-turbo",
        "processing_time": round(time.time() - (start_time or time.time()), 2)
    }

def generate_answer_one_call(user_query: str,
                             application_field: str,
                             primary_domains: List[str],
                             secondary_domains: List[str],
                             concepts: List[Tuple[str, str]] | List[Dict[str, str]] = None
                             ) -> Dict[str, Any]:
    """
    Generate strategic lens and follow-up prompts in ONE OpenAI call.
    Returns backend contract fields; caller appends conceptsToolsPractice.
    """
    start_time = time.time()
    
    # Build system prompt per specification
    system_prompt = """You are Engent Labs Decision-Making Tutor.

Tone: genuine, practical, engaging, clear, and positive. Write as if you are coaching a colleague—no lecture voice.

CRITICAL: Use natural openings (not "When facing…", "It's crucial…", "One effective strategy…"). Vary sentence rhythm and keep phrasing grounded.

Expectations:
– Craft a cohesive mini-essay (about three paragraphs) blending reasoning, a real-world example, and a forward-looking insight.
– The example must cite a publicly reported organization/person with a specific year and a concrete metric/action/outcome. No placeholders or hypothetical roles.
– Do not include headings before the essay.
– After the essay, insert a blank line, then the heading "Follow-up Prompts:". Provide 3–4 bullet questions on separate lines, each starting with "- " and beginning with How/What/Why/Which/Where/Who/When.
– Keep each question ≤120 characters. Do not output JSON or additional sections."""

    # Use provided concepts (extracted by the main process_query function)
    if concepts is None:
        concepts = []

    # Behavioral enforcement detection
    behavioral_indicators = [
        "judgment", "stress", "escalation", "negotiation", "personal", "career", 
        "anxious", "feel", "emotion", "psychological", "bias", "intuition"
    ]
    require_behavioral = any(indicator in user_query.lower() for indicator in behavioral_indicators)

    # Normalize concepts to list of {term, definition}
    norm_concepts: List[Dict[str, str]] = []
    
    for c in concepts:
        if isinstance(c, dict):
            term = c.get("term") or c.get("name") or ""
            definition = c.get("definition", "")
        else:
            term, definition = c[0], c[1] if len(c) > 1 else (c[0], "")
        if term:
            norm_concepts.append({"term": term, "definition": definition})

    # Shortlist for prompt injection (keep prompt focused)
    shortlist_k = CONFIG_V167B.get('SHORTLIST_K', 6)
    shortlist = norm_concepts[:shortlist_k]

    # Build a soft diversity hint from recent examples (avoid immediate repeats)
    avoid_list = []
    try:
        window = CONFIG_V167B.get('RECENT_EXAMPLES_AVOID_WINDOW', 5)
        avoid_list = RECENT_EXAMPLES_LRU[-window:]
    except Exception:
        avoid_list = []

    user_prompt = f"""
Here is the query context:

Query: {user_query}
Application field: {application_field}
Primary domain(s): {primary_domains}
Secondary domain(s): {secondary_domains}
Approved Glossary Shortlist (use ONLY if clearly relevant; exact spelling/definitions): {shortlist}

Generate a natural language response with:
- Exactly 3 paragraphs in this order: (1) reasoning/trade-off, (2) one specific real-world example with concrete details (company/year/outcome), (3) strategic insight.
- Keep the example organically integrated into the analysis (not a separate case block).
- End with 3–4 short, question-form follow-ups, each on its own line starting with "-". Include two generalization questions that broaden from the example back to the core concept (transferability, conditions, thresholds) and one or two questions tied to the named example (actions, trade-offs, outcomes). All follow-up prompts must come directly from this answer; no downstream logic will supplement them.
- Include behavioral insights if relevant

Opening and flow refinements (keep natural tone, do not change length):
- Begin by tying your reasoning explicitly to the user's query context (avoid boilerplate openers).
- In the real-world passage, include 1–2 analytical details (a specific action, a trade-off, or a measurable outcome). Do not invent facts.
- Use at least one connective phrase to bridge ideas (e.g., "Concretely…", "This illustrates…", "As a result…").
- Conclude with a clear takeaway or limitation (the "so what", when it might not hold, or what to watch).

Notes:
 - Choose at most 2–3 items from the Approved Glossary Shortlist ONLY if they are clearly evidenced in your answer (omit if weak).
 - Do NOT output any concept list; only the explanation and follow-up questions.
 - Use a specific, verifiable company/entity and year in the example; do not use placeholders (e.g., "XYZ", "Company A").
 - Use a well-known, publicly reported example (company/organization/person + year). Avoid hypothetical or composite cases.
 - Include one anchoring fact (e.g., named product/site/market) so the example feels concrete and verifiable.
 - Do not include explicit source names or citations.
 - If multiple suitable examples exist, avoid recently used pairs: {avoid_list}
 - If a tool naturally arises in your reasoning, name it once (only if it truly adds clarity).
"""

    try:
        if openai is None:
            raise RuntimeError("OpenAI SDK not available")
        
        parsed_output = None
        placeholder_flags = {
            "company x", "company y", "company a", "company b", "acme",
            "sample company", "example company", "a buyer", "a manager",
            "a marketing executive", "industry leader", "organization x",
            "hypothetical", "fictional"
        }

        strict_hint = (
            "\n\nSTRICT MODE: Use a well-documented example (e.g., Tesla's 2018 tariff response, Netflix's 2015 original "
            "content expansion, Apple's 2019 services pivot, Toyota's 2011 supply-chain recovery, IBM's 2014 cloud "
            "shift, Starbucks' 2016 Teavana decision) that fits the "
            "query. Name the organization/person and the year explicitly, and include a concrete metric/outcome. "
            "Do NOT use placeholders or generic labels."
        )

        for attempt in range(3):
            this_prompt = user_prompt
            if attempt > 0:
                this_prompt += strict_hint

            parsed_output = generate_answer_with_retry(this_prompt, system_prompt, require_behavioral, norm_concepts, application_field, start_time)
            lens_txt = parsed_output.get("strategicThinkingLens", "") if isinstance(parsed_output, dict) else ""

            ent, yr = _extract_entity_year(lens_txt)
            has_placeholder = any(flag in lens_txt.lower() for flag in placeholder_flags)
            recent_window = set(RECENT_EXAMPLES_LRU[-CONFIG_V167B.get('RECENT_EXAMPLES_AVOID_WINDOW', 5):])
            is_recent = (ent, yr) in recent_window if ent and yr else False

            if _validate_lens_quality(lens_txt) and not has_placeholder and not is_recent:
                break
            if attempt == 2:
                print({"lens_placeholder_warning": lens_txt[:200]})
        
        if "error" in parsed_output:
            # Return best-effort parsed output if present
            if isinstance(parsed_output, dict) and parsed_output.get("strategicThinkingLens"):
                return parsed_output
            return parsed_output

        processing_time = round(time.time() - start_time, 2)
        strategic_lens_out = parsed_output.get("strategicThinkingLens", "")
        strategic_lens_out = _de_mechanize_lens(strategic_lens_out)
        # V1.6.8: Conditional Lens enhancement (editor pass)
        try:
            if CONFIG_V167B.get('ALWAYS_ENHANCE_LENS', False):
                enhanced, triggered, reverted, reasons = enhance_lens_if_needed(strategic_lens_out, user_query, force=True)
            else:
                enhanced, triggered, reverted, reasons = enhance_lens_if_needed(strategic_lens_out, user_query)
            if triggered:
                print(f"Lens enhancement triggered; reasons={reasons}; reverted={reverted}")
            strategic_lens_out = enhanced
        except Exception:
            pass
        # Update recent examples LRU
        try:
            ent, yr = _extract_entity_year(strategic_lens_out)
            if ent and yr:
                RECENT_EXAMPLES_LRU.append((ent, yr))
                maxlen = CONFIG_V167B.get('RECENT_EXAMPLES_MAX', 20)
                if len(RECENT_EXAMPLES_LRU) > maxlen:
                    del RECENT_EXAMPLES_LRU[: len(RECENT_EXAMPLES_LRU) - maxlen]
        except Exception:
            pass
        # Sanitize follow-up prompts: concise, question-form, up to 4
        raw_fu = parsed_output.get("followUpPrompts", [])
        followups_out = _sanitize_followups(raw_fu, example_hint="")
        if len(followups_out) < 3:
            print(f"[followups] supplementing prompts for query='{user_query[:80]}'")
            followups_out = _supplement_followups(followups_out)
        else:
            followups_out = followups_out[:4]
        return {
            "strategicThinkingLens": strategic_lens_out,
            "followUpPrompts": followups_out,
            "conceptsToolsPractice": norm_concepts,  # glossary-only
            "applicationField": application_field,
            "model": "gpt-3.5-turbo",
            "processing_time": processing_time
        }
    except Exception as e:
        print(f"Exception in generate_answer_one_call: {e}")
        import traceback
        traceback.print_exc()
        # Graceful outer fallback with minimal structured content
        fallback_followups = [
            "What is the primary objective you are optimizing for?",
            "What are the top two options and their trade-offs?",
            "What evidence would most reduce uncertainty?"
        ]
        return {
            "strategicThinkingLens": (
                "A concise strategy answer could not be fully generated due to a temporary issue. "
                "Focus on clarifying objectives, mapping options and consequences, and choosing the best path under constraints."
            ),
            "followUpPrompts": fallback_followups,
            "conceptsToolsPractice": norm_concepts,
            "applicationField": application_field,
            "model": "gpt-3.5-turbo",
            "processing_time": round(time.time() - (start_time or time.time()), 2)
        }

def run_query_once(query: str) -> str:
    """Main entry point for one-call API"""
    try:
        result = process_query(query)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": "Server issue, please try again later."}, ensure_ascii=False)

def _de_mechanize_lens(text: str) -> str:
    """Remove mechanical subtitles and labels, soften stock phrases.
    - Remove 'Strategic Insight:'/'Insight:' and 'Reflective follow-up questions:' lines
    - Replace common stock phrases with more natural alternatives
    """
    try:
        # Remove common subtitle labels at paragraph starts
        text = re.sub(r"(^|\n\n)\s*(Strategic\s+Insight|Insight|Key\s+Insight)\s*:\s*", r"\1", text, flags=re.IGNORECASE)
        # Remove any explicit label preceding follow-ups if leaked into lens
        text = re.sub(r"\n\s*Reflective follow-up questions:\s*\n?", "\n\n", text, flags=re.IGNORECASE)
        # Soften stock phrases (non-destructive replacements)
        replacements = {
            "it's crucial to": "you can",
            "it is crucial to": "you can",
            "one effective strategy is": "one approach is",
            "another valuable strategy is": "another approach is",
            "in such instances": "in these situations",
        }
        for k, v in replacements.items():
            text = re.sub(rf"\b{re.escape(k)}\b", v, text, flags=re.IGNORECASE)
        return text
    except Exception:
        return text

def _sanitize_followups(followups: list, example_hint: str = "") -> list:
    """Normalize follow-ups to short, question-form items.
    - Target max ~140 chars; avoid mid-word truncation by cutting at the last space/punctuation before the limit
    - Prefer the first question-sentence if present; otherwise trim a single concise question ending with '?'
    - Drop blanks/duplicates and cap at 4 items
    """
    cleaned = []
    seen = set()
    for item in followups or []:
        if not isinstance(item, str):
            continue
        s = item.strip()
        if not s:
            continue
        # Take up to the first question mark if present
        qm_idx = s.find('?')
        if qm_idx != -1:
            s = s[:qm_idx+1]
        # Trim excessive length gently to ~140 chars without cutting mid-word
        MAX_LEN = 140
        if len(s) > MAX_LEN:
            candidate = s[:MAX_LEN]
            # Prefer to cut at punctuation or space
            cut_points = [candidate.rfind(ch) for ch in ['?', '.', '!', ';', ':', '—', '-', ',',' ']]
            cut_at = max(cp for cp in cut_points)
            if cut_at > 0:
                s = candidate[:cut_at].rstrip()
            else:
                s = candidate.rstrip()
        # Ensure ends with a question mark
        if not s.endswith('?'):
            s = s.rstrip('.').rstrip() + '?'
        key = s.lower()
        if key in seen:
            continue
        if s:
            s = s[0].upper() + s[1:]
        seen.add(key)
        cleaned.append(s)
        if len(cleaned) >= 4:
            break
    return cleaned

def _supplement_followups(followups: list[str]) -> list[str]:
    templates = [
        "How would you apply this reasoning in your own context?",
        "What conditions might change whether this approach works?",
        "Which metrics or signals would you monitor to gauge success?",
        "Where else could this insight deliver value if adapted?"
    ]
    idx = 0
    while len(followups) < 3 and idx < len(templates):
        followups.append(templates[idx])
        idx += 1
    return followups[:4]

def _validate_lens_quality(text: str) -> bool:
    """Lightweight validator for Lens quality: typically 2–3 paragraphs, includes a named entity, a year, and a numeric element."""
    try:
        paras = [p.strip() for p in (text or '').split('\n\n') if p.strip()]
        # Prefer readability: about 3 paragraphs (allow 1–4)
        if not (1 <= len(paras) <= 4):
            return False
        lens_lower = text.lower()
        # Year pattern
        has_year = re.search(r"\b(19|20)\d{2}\b", text) is not None
        # Numeric element (generic number anywhere)
        has_number = re.search(r"\d", text) is not None
        # Company/entity heuristic (proper noun + Inc/Corp/Ltd or known brands)
        has_company = bool(re.search(r"\b([A-Z][a-z]+\s(?:Inc|Corp|LLC|Ltd))\b", text)) or any(b in text for b in ["Tesla", "Apple", "Toyota", "Samsung", "GE", "Siemens", "Ford", "GM"])
        return has_year and has_number and has_company
    except Exception:
        return False


def _contains_placeholder_example(text: str) -> bool:
    try:
        lowered = (text or "").lower()
        return any(phrase in lowered for phrase in PLACEHOLDER_PHRASES)
    except Exception:
        return False

def _extract_entity_year(text: str) -> tuple[str, str]:
    """Best-effort extraction of (entity, year) from lens text."""
    entity = ""
    year = ""
    try:
        m_year = re.search(r"\b(19|20)\d{2}\b", text)
        if m_year:
            year = m_year.group(0)
        # Try proper noun + Inc/Corp/LLC/Ltd
        m_ent = re.search(r"\b([A-Z][A-Za-z0-9&.'-]+\s(?:Inc|Corp|LLC|Ltd))\b", text)
        if m_ent:
            entity = m_ent.group(1)
        else:
            # fallback to known brands
            brands = ["Tesla", "Apple", "Toyota", "Samsung", "GE", "Siemens", "Ford", "GM", "Coca-Cola", "McDonald's", "Unilever", "Nestlé", "Maersk", "UPS", "DHL"]
            for b in brands:
                if b in text:
                    entity = b
                    break
    except Exception:
        pass
    return entity, year

# ---------------- V1.6.8 Lens Enhancement (Second Call) ----------------

LENS_TRANSITION_TOKENS = [
    "concretely", "this illustrates", "stepping back", "as a result",
    "in practice", "in turn", "against that backdrop", "building on this",
    "looking ahead", "over time", "ultimately", "going forward", "in doing so"
]

LENS_INSIGHT_TOKENS = [
    "so ", "therefore", "shows how", "reveals why", "lesson",
    "what to watch", "implication", "in practice", "looking ahead",
    "going forward", "one caution"
]

def _has_transition(text: str) -> bool:
    tl = text.lower()
    return any(tok in tl for tok in LENS_TRANSITION_TOKENS)

def _has_closing_insight(text: str) -> bool:
    tail = (text or "")[-600:].lower()
    return any(tok in tail for tok in LENS_INSIGHT_TOKENS)

def _is_generic_opening(text: str, query: str) -> bool:
    try:
        first = (text or "").strip().split("\n\n", 1)[0]
        opener = first[:220].lower()
        generic_patterns = ["when facing", "when it comes", "it's important to", "it's crucial to", "one effective", "in such instances"]
        if any(p in opener for p in generic_patterns):
            # Allow pass if query terms appear in opener
            qt = query.lower().split()
            if not any(qw in opener for qw in qt[:5]):
                return True
        return False
    except Exception:
        return False

def _is_shallow_example(text: str) -> bool:
    # Missing any hint of action/trade-off/outcome terms
    tl = text.lower()
    analytic = ["localiz", "dual", "postpon", "trade-off", "constraint", "cost", "lead time", "outcome", "shift", "diversif"]
    return not any(tok in tl for tok in analytic)

def _needs_enhancement(lens_text: str, query: str) -> list:
    reasons = []
    if _is_generic_opening(lens_text, query):
        reasons.append("generic_opening")
    if _is_shallow_example(lens_text):
        reasons.append("shallow_example")
    if not _has_transition(lens_text):
        reasons.append("choppy_transition")
    if not _has_closing_insight(lens_text):
        reasons.append("missing_insight")
    words = len((lens_text or "").split())
    if words < 170:
        reasons.append("too_short")
    return reasons

def _validate_enhanced_lens(text: str) -> bool:
    if not text or len(text.strip()) < 60:
        return False
    # Entity/year and numeric element should remain
    ent, yr = _extract_entity_year(text)
    if not (ent and yr):
        return False
    if re.search(r"\d", text) is None:
        return False
    # Transitions and closure
    if not _has_transition(text):
        return False
    if not _has_closing_insight(text):
        return False
    # Paragraphs: allow 2–4; reject bullets/labels
    paras = [p for p in text.split("\n\n") if p.strip()]
    if not (1 <= len(paras) <= 5):
        return False
    if re.search(r"^\s*[-*] ", text, flags=re.MULTILINE):
        return False
    if re.search(r"^\s*#+\s", text, flags=re.MULTILINE):
        return False
    if "Reflective" in text:
        return False
    return True

def enhance_lens_if_needed(lens_text: str, query: str, force: bool = False) -> tuple[str, bool, bool, list]:
    """Return (final_lens, triggered, reverted, reasons). Never raises."""
    try:
        reasons = _needs_enhancement(lens_text, query) if not force else ["forced"]
        if not reasons and not force:
            return lens_text, False, False, []
        # Build editor prompts
        system_prompt = (
            "You are an editor improving clarity, pacing, and depth while preserving every idea, fact, entity, year, and metric. "
            "Rewrite the lens as a short Harvard Business Review–style commentary: open with a confident situational hook, weave the example into the analysis, vary sentence rhythm, and finish with a forward-looking note. "
            "Do not add citations or remove facts. Return only the rewritten Lens as plain text."
        )
        base_user_prompt = (
            "Polish this Strategic Thinking Lens into a fluent mini-essay that sounds like advice shared among colleagues. "
            "Preserve every fact and example, but feel free to reorder or rephrase sentences for flow. "
            "Aim for a grounded, conversational voice with smooth transitions, and finish with a forward-looking takeaway that ties the example back to practical implications. "
            "Return only the Lens as continuous prose (no labels, bullets, or citations).\n\n"
            f"Query: {query}\n\nLens:\n{lens_text}"
        )

        banned_tokens = ["for example", "concretely", "it's", "it is"]

        def _content_loss(candidate_text: str, original_text: str) -> bool:
            ent_orig, yr_orig = _extract_entity_year(original_text)
            ent_new, yr_new = _extract_entity_year(candidate_text)
            if ent_orig and ent_new and ent_orig != ent_new:
                return True
            if yr_orig and yr_new and yr_orig != yr_new:
                return True
            if yr_orig and not yr_new:
                return True
            if ent_orig and not ent_new:
                return True
            return False

        retry_reasons: list[str] = []
        best_candidate = lens_text

        for style_pass in range(2):
            user_prompt = base_user_prompt
            if style_pass == 1:
                user_prompt += "\n\nAdjustment: Aim for an even more fluid tone and keep every factual detail intact."

            enhanced = generate_answer_with_retry(user_prompt, system_prompt, False, [], "decision", time.time())
            candidate = enhanced.get("strategicThinkingLens", "") if isinstance(enhanced, dict) else (enhanced if isinstance(enhanced, str) else "")

            if candidate:
                best_candidate = candidate

            if _content_loss(candidate, lens_text):
                retry_reasons.append("content_loss")
                continue

            if len(candidate.split()) < max(1, int(0.8 * len(lens_text.split()))):
                retry_reasons.append("short_output")

            if not _validate_enhanced_lens(candidate):
                retry_reasons.append("style_check")

            lowered = candidate.lower()
            repeats = {tok: lowered.count(tok) for tok in banned_tokens if lowered.count(tok) > 1}
            if repeats:
                print({"style_warning": repeats})

            return candidate, True, False, reasons or ["forced"]

        print({"editor_retry_reasons": retry_reasons})
        return best_candidate, True, False, reasons or ["forced"]
    except Exception:
        return lens_text, False, False, []

def process_query(query: str, course_config: dict = None) -> str:
    """
    Main query processing function - generates structured ThinkPal responses.
    
    Args:
        query: User's question
        course_config: Optional course-specific configuration
        
    Returns:
        Formatted ThinkPal response with all sections
    """
    try:
        # Load data lazily with V1.6.6.6 temporary caching
        # TEMPORARY: Using cached data loading to avoid repeated ~24s loads
        # This will be replaced with proper multi-course architecture in V1.6.7
        index, metadata, documents, file_names, model, nlp = load_course_data_cached("decision")
        
        # ✅ Relevance filter to reject off-topic queries before GPT call
        score, debug = compute_relevance_score(query)
        if score < 2:
            # Query rejected due to low relevance
            return (
                "⚠️ This question doesn't appear to be related to the course. "
                "Try asking about decision-making tools, strategies, or intuitive judgment."
            )
        
        # Use unified semantic extraction for consistent domain/field/concept selection
        unified_results = unified_semantic_extraction(query)
        
        # Keep selected_domains as a dict with scores (V1.6.6 fix)
        if unified_results and isinstance(unified_results, dict):
            selected_domains = unified_results  # Keep as dict with scores
            primary_domain = max(selected_domains, key=selected_domains.get) if selected_domains else 'general'
        else:
            selected_domains = {'general': 1.0}  # Keep as dict
            primary_domain = 'general'
        
        # V1.6.6 fix: selected_domains now properly maintained as dict with scores
        
        
        
        
        
        application_field = 'general'  # Not implemented yet
        entities = {}  # Not implemented yet
        
        # UNIFIED CONCEPT EXTRACTION FLOW
        # Step 0: Load glossary and perform exact/fuzzy phrase detection (high precision)
        
        # Load course glossary directly
        with open('courses/decision/glossary.json', 'r', encoding='utf-8') as f:
            glossary_to_use = json.load(f)
        
        # Build normalized phrase index: concept names + aliases → canonical concept
        def _normalize_text(s: str) -> str:
            return re.sub(r"\s+", " ", s.lower().replace('-', ' ').replace('_', ' ')).strip()

        phrase_to_concept = {}
        for concept_name, concept_data in glossary_to_use.items():
            canonical = concept_name
            base_norm = _normalize_text(concept_name)
            phrase_to_concept[base_norm] = canonical
            # Add simple plural variant for single-token names (e.g., auction -> auctions)
            if len(base_norm.split()) == 1 and len(base_norm) > 2:
                if not base_norm.endswith('s'):
                    phrase_to_concept[base_norm + 's'] = canonical
                if base_norm.endswith('y'):
                    phrase_to_concept[base_norm[:-1] + 'ies'] = canonical
            if isinstance(concept_data, dict) and 'aliases' in concept_data:
                for alias in concept_data['aliases']:
                    an = _normalize_text(alias)
                    phrase_to_concept[an] = canonical
                    # Add plural variants for single-token aliases
                    if len(an.split()) == 1 and len(an) > 2:
                        if not an.endswith('s'):
                            phrase_to_concept[an + 's'] = canonical
                        if an.endswith('y'):
                            phrase_to_concept[an[:-1] + 'ies'] = canonical

        query_norm = _normalize_text(query)

        # Whole-phrase exact match: word-boundary contains of any concept phrase (>=2 chars)
        forced_concepts = set()
        for phrase, canonical in phrase_to_concept.items():
            if len(phrase) < 2:
                continue
            # word-boundary search
            if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", query_norm):
                forced_concepts.add(canonical)

        # Conservative fuzzy match for small variations (>= 0.85) for multi-word phrases only
        def _fuzzy_ratio(a: str, b: str) -> float:
            # Simple normalized similarity using SequenceMatcher
            try:
                from difflib import SequenceMatcher
                return SequenceMatcher(None, a, b).ratio()
            except Exception:
                return 0.0

        for phrase, canonical in phrase_to_concept.items():
            if canonical in forced_concepts:
                continue
            # Only attempt fuzzy for phrases with at least two tokens to avoid single-word noise like "framing"
            if len(phrase.split()) < 2:
                continue
            if _fuzzy_ratio(phrase, query_norm) >= 0.85:
                forced_concepts.add(canonical)

        # Ensure parent domains for forced concepts are represented in selected_domains
        for c in forced_concepts:
            d = CONCEPT_DOMAINS.get(c, 'general')
            if d not in selected_domains:
                # add with conservative score so allocation rules can pick it when relevant
                selected_domains[d] = 0.6
        
        # Step 1: Score all glossary concepts
        # Get query embedding
        query_embedding = get_openai_embeddings([query])
        
        # Get concept embeddings
        concept_texts = []
        concept_names = []
        for name, concept_data in glossary_to_use.items():
            if isinstance(concept_data, str):
                definition = concept_data
            else:
                definition = concept_data["definition"]
            concept_text = f"{definition} {name.replace('-', ' ')}"
            concept_texts.append(concept_text)
            concept_names.append(name)
        
        concept_embeddings = get_openai_embeddings(concept_texts)
        similarities = batch_cosine_similarity(query_embedding[0], concept_embeddings)
        
        # Step 2: Score all concepts with complete scoring logic
        concept_scores = []
        for i, (concept_name, concept_data) in enumerate(glossary_to_use.items()):
            score = similarities[i]
            
            # Handle both old string format and new dictionary format
            if isinstance(concept_data, str):
                definition = concept_data
                is_core = False
            else:
                definition = concept_data["definition"]
                is_core = concept_data.get("core", False)
            
            # Store base similarity for logging
            base_similarity = score
            
            # Apply alias boost: +0.15 if query contains any alias
            alias_boost = 0.0
            if isinstance(concept_data, dict) and "aliases" in concept_data:
                for alias in concept_data["aliases"]:
                    if alias.lower() in query.lower():
                        alias_boost = 0.15
                        break
            score += alias_boost
            
            # Apply pattern boost: +0.15 for each regex pattern match
            pattern_boost = 0.0
            if isinstance(concept_data, dict) and "patterns" in concept_data:
                for pattern in concept_data["patterns"]:
                    if re.search(pattern, query, re.IGNORECASE):
                        pattern_boost += 0.15
            score += pattern_boost
            
            # Apply generic concept penalties (stronger penalties)
            generic_penalty = 0.0
            if concept_name == 'swot analysis':
                generic_penalty = 0.20
            elif concept_name == 'strategic framing':
                generic_penalty = 0.15
            elif concept_name == 'competitive advantage analysis':
                generic_penalty = 0.10
            elif concept_name in ['risk assessment', 'leadership assessment']:
                generic_penalty = 0.25
            elif concept_name == 'porter\'s five forces':
                generic_penalty = 0.05  # Small penalty to balance with other strategic frameworks
            score -= generic_penalty
            
            # Apply query-context boost: boost concepts that match query intent
            context_boost = 0.0
            query_lower = query.lower()
            
            # For uncertainty queries, boost uncertainty-related tools with consistent scoring
            # Use fuzzy matching for uncertainty-related keywords
            uncertainty_keywords = ['uncertainty', 'uncertain', 'volatile', 'unpredictable', 'probability', 'probabilistic', 'unpredict', 'unpredicting']
            has_uncertainty = any(word in query_lower for word in uncertainty_keywords)
            
            if has_uncertainty:
                if concept_name in ['monte carlo simulation', 'decision tree', 'scenario analysis']:
                    context_boost = 0.25  # Equal boost for primary uncertainty tools
                elif concept_name in ['sensitivity analysis', 'expected value', 'utility functions']:
                    context_boost = 0.2  # Moderate boost for secondary uncertainty tools
            
            # Boost concepts related to evaluation/decision-making when query mentions evaluation
            if 'evaluation' in query_lower or 'evaluate' in query_lower:
                if concept_name in ['value creation', 'cost-benefit analysis', 'expected value']:
                    context_boost = 0.03  # Small boost for evaluation-related concepts
            
            # Boost concepts related to options/alternatives when query mentions options
            if 'option' in query_lower or 'alternative' in query_lower:
                if concept_name in ['value creation', 'scenario analysis', 'decision tree']:
                    context_boost = max(context_boost, 0.03)  # Don't double-boost
            
            # Apply systematic context relevance analysis
            context_penalty = 0.0
            
            # Analyze semantic context mismatch between query and concept definition
            query_context = analyze_query_context(query_lower)
            concept_context = analyze_concept_context(concept_name, definition)
            
            # Calculate context relevance penalty based on semantic mismatch
            context_penalty = calculate_context_penalty(query_context, concept_context)
            
            score += context_boost - context_penalty

            # Conservative filtering: prefer fewer but more accurate concepts
            # If concept was not exact/fuzzy forced, require stronger baseline later
            
            # Apply core boost: multiplier 1.2x for core concepts
            final_score = score
            if is_core:
                final_score *= 1.2
            
            
            # Use final score
            score = final_score
            
            concept_scores.append((concept_name, definition, score))
        
        # Sort by score (highest first)
        concept_scores.sort(key=lambda x: x[2], reverse=True)
        
        # Step 3: Filter by selected domains with conservative thresholds
        filtered_concept_scores = []
        for concept_name, definition, score in concept_scores:
            concept_domain = CONCEPT_DOMAINS.get(concept_name.lower(), 'general')
            if concept_domain in selected_domains:
                # Keep if forced by exact/fuzzy matching
                if concept_name in forced_concepts:
                    filtered_concept_scores.append((concept_name, definition, score))
                    continue
                # Otherwise, enforce conservative thresholds (same as V1666.6 but stricter for secondaries on low scores)
                if concept_domain == primary_domain:
                    if score >= 0.50:
                        filtered_concept_scores.append((concept_name, definition, score))
                else:
                    if score >= 0.45:
                        filtered_concept_scores.append((concept_name, definition, score))

        # Additional conservative rule: avoid mapping single-word query "framing" to "framing bias"
        q_tokens = query_norm.split()
        if len(q_tokens) == 1 and q_tokens[0] == 'framing':
            filtered_concept_scores = [t for t in filtered_concept_scores if t[0].lower() != 'framing bias']
        
        
        # Step 4: Use unified select_concepts function for allocation
        domain_list = list(selected_domains.keys())
        primary_domain = domain_list[0] if domain_list else 'general'
        concepts = select_concepts(filtered_concept_scores, selected_domains, primary_domain)

        # Ensure forced concepts are included (respect hard cap and dedup later in select_concepts output)
        if forced_concepts:
            # Merge definitions for forced concepts
            name_to_def = {n: d for (n, d) in concepts}
            for fc in forced_concepts:
                if fc not in name_to_def and fc in glossary_to_use:
                    cdata = glossary_to_use[fc]
                    fdef = cdata if isinstance(cdata, str) else cdata.get('definition', fc)
                    concepts.append((fc, fdef))
            # Cap will be enforced downstream in Concepts/Tools rendering
        
        # Check if we need fallback concepts (should be disabled)
        if len(concepts) < 2:
            pass  # Fallback is disabled
        
        # Prepare domains for one-call generation
        domain_items = sorted(selected_domains.items(), key=lambda x: x[1], reverse=True)
        primary_domains_list = [domain_items[0][0]] if domain_items else ["general"]
        secondary_domains_list = [d for d, _ in domain_items[1:]] if len(domain_items) > 1 else []

        # One-call answer generation using tuned prompt
        one_call = generate_answer_one_call(
            user_query=query,
            application_field=application_field,
            primary_domains=primary_domains_list,
            secondary_domains=secondary_domains_list,
            concepts=concepts
        )

        # If one-call returned an error-like structure, map accordingly
        if isinstance(one_call, dict) and one_call.get("strategicThinkingLens") is not None:
            strategic_lens = one_call.get("strategicThinkingLens", "")
            followups = one_call.get("followUpPrompts", [])
        else:
            return json.dumps({"error": "Server issue, please try again later."}, ensure_ascii=False)

        # Map to frontend contract and return JSON string
        concepts_tools = [{"term": n, "definition": d} for (n, d) in concepts]
        final_answer = {
            "strategicLens": strategic_lens,
            "followupPrompts": followups,
            "conceptsToolsPractice": concepts_tools
        }
        return json.dumps(final_answer, ensure_ascii=False)
        
    except Exception as e:
        # Error in process_query - returning fallback response
        import traceback
        traceback.print_exc()
        return json.dumps({"error": "Server issue, please try again later."}, ensure_ascii=False)

def process_query_structured(query: str, course_config: dict = None) -> dict:
    """
    V1.6.6: Process query and return structured data for Lambda function.
    Eliminates need for Lambda to re-parse GPT response.
    
    Args:
        query: User's question
        course_config: Optional course-specific configuration
        
    Returns:
        Dictionary with structured response data
    """
    try:
        # Detect application field early and ensure it's always set
        try:
            application_field = extract_application_field_semantic(query, None)
        except:
            application_field = extract_application_field(query)
        
        if not application_field:
            application_field = "general"  # Safe default
        
        # Get the full answer and authoritative concepts from process_query
        process_result_str = process_query(query, course_config)
        
        # Parse the JSON string returned by process_query
        try:
            process_result = json.loads(process_result_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse process_query result: {e}")
        
        # Extract the structured data from process_query result
        # process_query returns: {"strategicLens": "...", "followupPrompts": [...], "conceptsToolsPractice": [...]}
        strategic_lens = process_result.get("strategicLens", "")
        followup_prompts = process_result.get("followupPrompts", [])
        concepts_tools_practice = process_result.get("conceptsToolsPractice", [])
        
        # For backward compatibility, create answer from strategicLens
        answer = strategic_lens
        
        
        # Extract structured data that Lambda function needs
        # 1. Strategic Thinking Lens (already extracted above)
        strategic_thinking_lens = strategic_lens
        
        # 2. Follow-up Prompts (already extracted above)
        # follow_up_prompts is already set from process_result.get("followupPrompts", [])
        
        # 3. Concepts/Tools (already extracted above)
        # concepts_tools_practice is already set from process_result.get("conceptsToolsPractice", [])
        
        # Application field already extracted from process_query
        
        # FORCE concepts to be included even if GPT didn't generate them
        if not concepts_tools_practice:
            pass  # This should not happen
        
        return {
            "answer": answer,
            "strategicThinkingLens": strategic_thinking_lens,
            "followUpPrompts": followup_prompts,
            "conceptsToolsPractice": concepts_tools_practice,
            "applicationField": application_field,
            "model": "gpt-3.5-turbo"
        }
        
    except Exception as e:
        # Error in process_query_structured - returning fallback response with error details
        import traceback
        error_details = str(e)
        traceback_str = traceback.format_exc()
        
        # Log the error for debugging
        print(f"ERROR in process_query_structured: {error_details}")
        print(f"Traceback: {traceback_str}")
        
        return {
            "answer": f"I apologize, but I encountered an error processing your query: {error_details}. Please try again.",
            "strategicThinkingLens": "",
            "followUpPrompts": [],
            "conceptsToolsPractice": [],
            "applicationField": "general",
            "model": "error",
            "error_details": error_details
        }

# Legacy enforce_thinkpal_structure removed - not used in one-call system

# Legacy format_fallback_response removed - not used in one-call system

def detect_domain_semantic(query: str) -> dict:
    """
    Legacy semantic domain detection function.
    Returns raw domain scores that are then processed by cluster-based selection.
    
    Note: This function is called by unified_semantic_extraction which applies
    the improved cluster-based logic for final domain selection.
    """
    try:
        # Load data lazily
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # 79 updated domain-specific reference queries (hardcoded for performance)
        domain_references = {
            'strategic': [
                "How do I decide whether to expand capacity now or wait until demand is clearer?",
                "My forecasting model fits historical data but fails during shocks. How should I improve it?",
                "Why do managers keep funding projects even when the numbers show it's a loss?",
                
                "A government must decide whether to protect one industry or open markets for growth. What frameworks apply?",
                "A predictive analytics tool shows customer churn risk, but leaders ignore it due to optimism bias. How should I respond?",
                "Two competitors must decide whether to invest early in unproven technology. How should timing be evaluated?",
                "Why do employees compete under a data-driven bonus system but stop collaborating?",
                "A company considers outsourcing IT services. What should it weigh when making the decision?",
                "Why do teams get overconfident after one successful project, ignoring future risks?",
                "In a merger negotiation, how can both sides avoid focusing only on dividing the pie?",
                "A forecasting model suggests demand will grow, but historical accuracy is low. How should leaders proceed?",
                "Why do groups often fall into groupthink when making strategic choices?",
                "What explains why managers stick to original plans even when data proves them wrong?",
                "How do I implement a systematic decision-making process for strategic planning?",
                "When evaluating a new product launch, how should scenario analysis be applied?",
                "What strategic risks emerge when executives react too quickly to competitor moves?",
                "How can sensitivity analysis help in deciding between alternative investment options?",
                "Why do employees resist shutting down failing projects, despite evidence?",
                "What is the role of framing effects in shaping public policy decisions?",
                "Why do leaders prefer short-term fixes over long-term solutions?",
                "How can cognitive biases distort risk assessments in strategy sessions?",
                "A predictive model for pricing performs poorly out of sample. What actions should be taken?",
                "A company debates whether to centralize or decentralize decision-making. What frameworks apply?",
                "How can simulation models support strategic planning in volatile markets?",
                "Why do leaders resist external advice when making strategic choices?",
                "What steps should analysts take to validate a demand forecasting model?",
                "How do sunk cost effects distort exit decisions in business strategy?",
                "A predictive analytics model suggests resource reallocation, but leadership resists. Why?",
                
                "Why do organizations often copy competitors without testing assumptions?",
                "What role does loss aversion play in delaying strategic exits?",
                "A firm must decide between global expansion and domestic consolidation. What strategic tools apply?",
                "How can Monte Carlo simulation support decisions under uncertainty?",
                "What explains why firms delay adopting new technologies even when data supports it?",
                "How can executives avoid escalation of commitment in large projects?",
                "Why do organizations default to industry benchmarks instead of running independent analysis?",
                "What frameworks help evaluate first-mover versus late-mover advantage in new markets?",
                "How should firms decide between diversification and focusing on a single core business?",
                "What are the trade-offs between vertical integration and outsourcing in global supply chains?",
                "How can scenario planning guide capacity investments under uncertainty?",
                "What strategic risks arise when companies imitate competitor moves without independent analysis?",
                "What role does Monte Carlo simulation play in evaluating risky investment projects?",
                "Why does multicollinearity in predictors weaken strategic forecasting accuracy?",
                "How does confirmation bias distort how executives interpret market signals?",
                "Why do sunk costs cause leaders to continue failing projects?",
                "What explains escalation of commitment in large infrastructure investments?",
                "How does groupthink affect strategic committee decisions?",
                "What are the key differences between distributive and integrative negotiation strategies?",
                "What is the role of BATNA (Best Alternative to a Negotiated Agreement) in contract talks?",
                "How should negotiators handle multi-party coalitions with conflicting agendas?",
                "In labor talks, what strategies reduce deadlock while protecting long-term relationships?",
            ],
            'technical': [
                "How do I decide whether to expand capacity now or wait until demand is clearer?",
                "My forecasting model fits historical data but fails during shocks. How should I improve it?",
                "My regression model shows high R², but it's driven mostly by seasonal cycles. What should I check?",
                "A predictive analytics tool shows customer churn risk, but leaders ignore it due to optimism bias. How should I respond?",
                "Two competitors must decide whether to invest early in unproven technology. How should timing be evaluated?",
                "Our data shows customers say one thing in surveys but act differently in purchases. How should I interpret this?",
                "Why do employees compete under a data-driven bonus system but stop collaborating?",
                "A company considers outsourcing IT services. What should it weigh when making the decision?",
                "A forecasting model suggests demand will grow, but historical accuracy is low. How should leaders proceed?",
                "What explains why managers stick to original plans even when data proves them wrong?",
                "When evaluating a new product launch, how should scenario analysis be applied?",
                "A company overestimates market size by relying on biased survey samples. How can this be corrected?",
                "How can sensitivity analysis help in deciding between alternative investment options?",
                "A regression model shows strong correlation but weak causation. What should analysts do?",
                "How do I implement a systematic decision-making process for strategic planning?",
                "A predictive model for pricing performs poorly out of sample. What actions should be taken?",
                "In data-driven decision processes, why do managers sometimes ignore statistical significance?",
                "How can simulation models support strategic planning in volatile markets?",
                "What steps should analysts take to validate a demand forecasting model?",
                "A predictive analytics model suggests resource reallocation, but leadership resists. Why?",
                "How should regression diagnostics be applied when multicollinearity appears?",
                "Why do managers overweight recent performance when evaluating employees?",
                "A firm must decide between global expansion and domestic consolidation. What strategic tools apply?",
                "Why do leaders interpret ambiguous data to fit pre-existing beliefs?",
                "How can Monte Carlo simulation support decisions under uncertainty?",
                
                "What explains why firms delay adopting new technologies even when data supports it?",
                "Why do organizations default to industry benchmarks instead of running independent analysis?",
                "How can scenario planning guide capacity investments under uncertainty?",
                "How do you run regression diagnostics when residuals are not normally distributed?",
                "What role does Monte Carlo simulation play in evaluating risky investment projects?",
                "How can clustering algorithms reveal hidden customer segments in large datasets?",
                "Why does multicollinearity in predictors weaken strategic forecasting accuracy?",
                "How should predictive models be validated to ensure out-of-sample performance?",
                "Why do managers overweight recent events when making forecasts?",
            ],
            'behavioral': [
                "Why do managers keep funding projects even when the numbers show it's a loss?",
                "Why do people fall into the splitting-pie trap during negotiation?",
                "A predictive analytics tool shows customer churn risk, but leaders ignore it due to optimism bias. How should I respond?",
                "Our data shows customers say one thing in surveys but act differently in purchases. How should I interpret this?",
                "Why do employees compete under a data-driven bonus system but stop collaborating?",
                "Why do teams get overconfident after one successful project, ignoring future risks?",
                "In a merger negotiation, how can both sides avoid focusing only on dividing the pie?",
                "Why do groups often fall into groupthink when making strategic choices?",
                "What explains why managers stick to original plans even when data proves them wrong?",
                "In cross-cultural negotiations, how do different communication styles affect outcomes?",
                "A company overestimates market size by relying on biased survey samples. How can this be corrected?",
                "What strategic risks emerge when executives react too quickly to competitor moves?",
                "Why do employees resist shutting down failing projects, despite evidence?",
                "How do I implement a systematic decision-making process for strategic planning?",
                "What is the role of framing effects in shaping public policy decisions?",
                "Why do leaders prefer short-term fixes over long-term solutions?",
                "How can cognitive biases distort risk assessments in strategy sessions?",
                "What explains why people anchor to initial information during negotiations?",
                "In data-driven decision processes, why do managers sometimes ignore statistical significance?",
                "In high-stakes negotiations, how do emotions influence concessions?",
                "Why do leaders resist external advice when making strategic choices?",
                "How do sunk cost effects distort exit decisions in business strategy?",
                "A predictive analytics model suggests resource reallocation, but leadership resists. Why?",
                
                "Why do organizations often copy competitors without testing assumptions?",
                "What role does loss aversion play in delaying strategic exits?",
                "Why do managers overweight recent performance when evaluating employees?",
                "In union negotiations, how do anchoring effects shape expectations?",
                "Why do leaders interpret ambiguous data to fit pre-existing beliefs?",
                
                "What explains why firms delay adopting new technologies even when data supports it?",
                "How can executives avoid escalation of commitment in large projects?",
                "Why do organizations default to industry benchmarks instead of running independent analysis?",
                "What strategic risks arise when companies imitate competitor moves without independent analysis?",
                "How does confirmation bias distort how executives interpret market signals?",
                "Why do sunk costs cause leaders to continue failing projects?",
                "What explains escalation of commitment in large infrastructure investments?",
                "How does groupthink affect strategic committee decisions?",
                "Why do managers overweight recent events when making forecasts?",
                "How can anchoring offers shape expectations in joint venture negotiations?",
            ],
            'negotiation': [
                "In a merger negotiation, how can both sides avoid focusing only on dividing the pie?",
                "In cross-cultural negotiations, how do different communication styles affect outcomes?",
                "In high-stakes negotiations, how do emotions influence concessions?",
                "In union negotiations, how do anchoring effects shape expectations?",
                "What explains why people anchor to initial information during negotiations?",
                "How can executives avoid escalation of commitment in large projects?",
                "Why do organizations default to industry benchmarks instead of running independent analysis?",
                "What strategic risks arise when companies imitate competitor moves without independent analysis?",
                "How does confirmation bias distort how executives interpret market signals?",
                "Why do sunk costs cause leaders to continue failing projects?",
                "What explains escalation of commitment in large infrastructure investments?",
                "How does groupthink affect strategic committee decisions?",
                "Why do managers overweight recent events when making forecasts?",
                "How can anchoring offers shape expectations in joint venture negotiations?",
            ],
        }

        
        # Generate embeddings for query and domain references using OpenAI
        query_embedding = get_openai_embeddings([query])
        
        domain_scores = {}
        
        for domain, references in domain_references.items():
            # Skip domains with no references to avoid API errors
            if not references or len(references) == 0:
                domain_scores[domain] = 0.0
                continue
                
            # Encode all reference texts for this domain using OpenAI
            reference_embeddings = get_openai_embeddings(references)
            
            # Calculate similarities between query and all references using custom function
            similarities = batch_cosine_similarity(query_embedding[0], reference_embeddings)
            
            # Take the maximum similarity as the domain score
            max_similarity = max(similarities)
            domain_scores[domain] = max_similarity
        
        # Normalize scores to sum to 1.0
        total_score = sum(domain_scores.values())
        if total_score > 0:
            domain_scores = {domain: score / total_score for domain, score in domain_scores.items()}
        
        return domain_scores
        
    except Exception as e:
        # Error in semantic domain detection - using fallback
        # Fallback to keyword-based detection
        return detect_course_concept_domains(query)

def unified_semantic_extraction(query: str) -> dict:
    """
    Unified semantic extraction system for consistent domain, application field, 
    concept, and entity extraction using semantic similarity.
    """
    try:
        # Load data lazily
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # 1. HYBRID DOMAIN DETECTION (combines semantic + keyword methods)
        selected_domains = hybrid_domain_detection(query)
        
        # Return hybrid detection result
        return selected_domains
        
    except Exception as e:
        # Error in unified semantic extraction - using fallback
        # Fallback to individual methods
        return {}

def extract_application_field_semantic(query: str, model) -> str:
    """
    Hybrid semantic + keyword-based application field detection.
    Returns: the most relevant field with fallback to keyword logic if semantic confidence is low.
    """
    # Application field reference texts for semantic matching
    application_references = {
        'business_markets': [
            "business strategy and market analysis",
            "competitive positioning and growth",
            "brand management and marketing",
            "customer acquisition and sales",
            "revenue optimization and profit"
        ],
        'operations_management': [
            "production planning and capacity",
            "supply chain optimization",
            "logistics and inventory management",
            "manufacturing process improvement",
            "workflow optimization"
        ],
        'financial_decision_making': [
            "investment analysis and valuation",
            "budget planning and cost control",
            "capital allocation decisions",
            "funding and financing options",
            "profitability assessment"
        ],
        'technology_management': [
            "technology adoption and implementation",
            "digital transformation strategy",
            "AI and automation decisions",
            "cybersecurity planning",
            "data science and analytics"
        ],
        'risk_crisis_resilience': [
            "risk assessment and mitigation",
            "crisis management planning",
            "disaster response and recovery",
            "safety and security measures",
            "resilience building strategies"
        ],
        'people_talent_career': [
            "talent acquisition and recruitment",
            "employee development and retention",
            "leadership and team management",
            "career planning and advancement",
            "compensation and benefits"
        ],
        'policy_regulatory': [
            "regulatory compliance and standards",
            "policy development and implementation",
            "legal risk management",
            "government relations",
            "ethical governance"
        ],
        'product_development_innovation': [
            "product design and development",
            "prototype testing and validation",
            "feature prioritization",
            "user feedback integration",
            "innovation roadmap planning"
        ],
        'sustainability_environment': [
            "environmental impact assessment",
            "sustainability strategy development",
            "climate action planning",
            "renewable energy adoption",
            "conservation initiatives"
        ],
        'education_learning': [
            "educational program design",
            "curriculum development",
            "student learning outcomes",
            "teaching methodology",
            "training effectiveness"
        ],
        'healthcare_medical': [
            "patient diagnosis protocols and medical imaging",
            "surgical treatment planning and procedures",
            "clinical care pathways and patient outcomes",
            "healthcare facility management and accreditation",
            "medical device implementation and FDA compliance"
        ],
        'military_defense': [
            "military strategy and tactics",
            "defense planning and operations",
            "mission execution and deployment",
            "combat readiness and training",
            "security and intelligence"
        ]
    }

    # Encode query using OpenAI
    query_embedding = get_openai_embeddings([query])
    field_scores = {}

    for field, examples in application_references.items():
        example_embeddings = get_openai_embeddings(examples)
        similarities = batch_cosine_similarity(query_embedding[0], example_embeddings)
        similarity = max(similarities)
        field_scores[field] = similarity

    # Get best semantic match
    semantic_field = max(field_scores, key=field_scores.get)
    semantic_score = field_scores[semantic_field]

    # Keyword-based fallback scoring (lightweight)
    def extract_application_field_keywords(query: str) -> Tuple[str, float]:
        q = query.lower()
        field_keywords = {
            'business_markets': ["business", "company", "market", "competition", "growth", "branding", "marketing", "customer", "sales", "revenue", "profit"],
            'operations_management': ["production", "operations", "logistics", "supply", "manufacturing", "inventory", "process", "workflow"],
            'financial_decision_making': ["investment", "financial", "budget", "cost", "pricing", "valuation", "capital", "funding", "expenses", "profitability"],
            'technology_management': ["technology", "innovation", "digital", "software", "platform", "AI", "artificial intelligence", "automation", "cybersecurity", "data science"],
            'risk_crisis_resilience': ["risk", "uncertainty", "volatile", "unpredictable", "threat", "mitigation", "contingency", "disaster", "emergency", "safety", "resilience"],
            'people_talent_career': ["hiring", "recruitment", "employee", "staff", "team", "leadership", "management", "culture", "retention", "job", "offer", "employment", "career", "salary", "compensation", "benefits"],
            'policy_regulatory': ["policy", "regulation", "compliance", "legal", "government", "legislation", "standards", "ethics"],
            'product_development_innovation': ["product", "design", "prototype", "testing", "features", "roadmap", "user feedback"],
            'sustainability_environment': ["sustainability", "environmental", "climate", "carbon", "renewable", "conservation", "green"],
            'education_learning': ["education", "learning", "school", "teaching", "curriculum", "training", "students"],
            'healthcare_medical': ["healthcare", "medical", "patient", "treatment", "diagnosis", "clinical", "hospital", "therapy"],
            'military_defense': ["military", "defense", "army", "navy", "air force", "marine", "security", "mission", "tactical", "combat", "deployment", "training exercise"]
        }

        best_field = "general"
        max_matches = 0
        for field, keywords in field_keywords.items():
            matches = sum(1 for word in keywords if word in q)
            if matches > max_matches:
                best_field = field
                max_matches = matches

        keyword_score = min(max_matches / 5.0, 1.0)  # Normalize
        return best_field, keyword_score

    keyword_field, keyword_score = extract_application_field_keywords(query)

    # Final decision: semantic vs keyword
    if max(semantic_score, keyword_score) < 0.5:
        return 'general'
    elif keyword_score > semantic_score:
        return keyword_field
    else:
        return semantic_field

def extract_entities_semantic(query: str, model, nlp) -> dict:
    """
    Extract entities using both NLP and semantic similarity for better accuracy.
    """
    entities = {}
    
    # Use spaCy for basic entity extraction if available
    if nlp is not None:
        doc = nlp(query)
        
        # Extract named entities
        for ent in doc.ents:
            entities[ent.text] = {
                'type': ent.label_,
                'confidence': 0.8,  # spaCy confidence
                'method': 'nlp'
            }
    
    # Use semantic similarity to identify domain-specific entities
    domain_entities = {
        'behavioral': ['manager', 'team', 'colleague', 'employee', 'stakeholder'],
        'technical': ['model', 'algorithm', 'system', 'data', 'analysis'],
        'strategic': ['strategy', 'plan', 'approach', 'method', 'framework'],
        'negotiation': ['deal', 'agreement', 'contract', 'settlement', 'proposal']
    }
    
    # Check for domain-specific entities using semantic similarity
    query_embedding = get_openai_embeddings([query])
    
    for domain, entity_list in domain_entities.items():
        entity_embeddings = get_openai_embeddings(entity_list)
        similarities = batch_cosine_similarity(query_embedding[0], entity_embeddings)
        
        for i, entity in enumerate(entity_list):
            similarity = similarities[i]
            if similarity > 0.3:  # Threshold for entity detection
                entities[entity] = {
                    'type': 'DOMAIN_ENTITY',
                    'confidence': similarity,
                    'method': 'semantic',
                    'domain': domain
                }
    
    return entities

def detect_domain_clusters_improved(domain_scores: dict, method: str = "general") -> list:
    """
    Improved cluster detection with method-specific parameters for semantic, keyword, and hybrid.
    
    Args:
        domain_scores: Dictionary with domain names as keys and scores as values
        method: "semantic", "keyword", or "hybrid" for method-specific parameters
        
    Returns:
        List of clusters, each cluster is a list of (domain, score) tuples
    """
    if not domain_scores:
        return []
    
    # Remove general domain to reduce noise before clustering
    # General domain should only be picked as fallback if no specific domains are selected
    filtered_scores = {domain: score for domain, score in domain_scores.items() if domain != 'general'}
    
    if not filtered_scores:
        return []
    
    # Method-specific clustering parameters
    cluster_params = {
        "semantic": {
            "primary_gap": 0.10,      # Slightly looser clustering for normalized semantic scores (0.3-1.0)
            "secondary_gap": 0.08,    # Slightly looser secondary cluster detection
            "weak_threshold": 0.25    # Lowered quality bar to include behavioral domain
        },
        "keyword": {
            "primary_gap": 0.20,      # Moderate clustering for normalized keyword scores (0.1-1.0)
            "secondary_gap": 0.15,    # Moderate secondary cluster detection
            "weak_threshold": 0.25    # Standard quality bar for keyword
        },
        "hybrid": {
            "primary_gap": 0.12,      # Balanced clustering for hybrid (combines both methods)
            "secondary_gap": 0.10,    # Balanced secondary detection
            "weak_threshold": 0.30    # Balanced quality requirements
        }
    }
    
    params = cluster_params.get(method, cluster_params["semantic"])
    
    # Sort domains by score (highest first)
    sorted_domains = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
    
    clusters = []
    current_cluster = [sorted_domains[0]]
    
    for i in range(1, len(sorted_domains)):
        current_score = sorted_domains[i][1]
        prev_score = sorted_domains[i-1][1]
        gap = prev_score - current_score
        
        # Determine which gap threshold to use based on cluster position
        if len(clusters) == 0:  # First cluster (primary)
            gap_threshold = params["primary_gap"]
        else:  # Subsequent clusters (secondary)
            gap_threshold = params["secondary_gap"]
        
        if gap <= gap_threshold:
            current_cluster.append(sorted_domains[i])
        else:
            clusters.append(current_cluster)
            current_cluster = [sorted_domains[i]]
    
    clusters.append(current_cluster)
    return clusters

def select_domains_by_clusters_improved(domain_scores: dict, method: str = "general", max_domains: int = 3) -> dict:
    """
    Improved domain selection using cluster-based logic with method-specific parameters.
    
    Args:
        domain_scores: Dictionary with domain names as keys and scores as values
        method: "semantic", "keyword", or "hybrid" for method-specific parameters
        max_domains: Maximum number of domains to select (default 3, rarely 4)
        
    Returns:
        Dictionary of selected domains with their scores
    """
    if not domain_scores:
        return {}
    
    # Method-specific selection parameters
    selection_params = {
        "semantic": {
            "primary_min_score": 0.45,    # Higher threshold for normalized semantic scores (0.3-1.0)
            "secondary_min_score": 0.25,  # Lowered secondary threshold to include behavioral domain
            "weak_rejection": True        # Reject secondary cluster if it contains weak domains
        },
        "keyword": {
            "primary_min_score": 0.30,    # Standard threshold for normalized keyword scores (0.1-1.0)
            "secondary_min_score": 0.25,  # Standard secondary threshold for keyword
            "weak_rejection": True        # Reject secondary cluster if it contains weak domains
        },
        "hybrid": {
            "primary_min_score": 0.38,    # Balanced threshold for hybrid (combines both methods)
            "secondary_min_score": 0.30,  # Balanced secondary threshold for hybrid
            "weak_rejection": True        # Reject secondary cluster if it contains weak domains
        }
    }
    
    params = selection_params.get(method, selection_params["semantic"])
    
    # Detect clusters
    clusters = detect_domain_clusters_improved(domain_scores, method)
    
    if not clusters:
        return {}
    
    selected_domains = {}
    
    # Always include primary cluster (first cluster)
    primary_cluster = clusters[0]
    primary_avg_score = sum(score for _, score in primary_cluster) / len(primary_cluster)
    
    if primary_avg_score >= params["primary_min_score"]:
        for domain, score in primary_cluster:
            selected_domains[domain] = score
    
    # Check secondary cluster if we have room and it meets criteria
    if len(clusters) > 1 and len(selected_domains) < max_domains:
        secondary_cluster = clusters[1]
        secondary_avg_score = sum(score for _, score in secondary_cluster) / len(secondary_cluster)
        
        # Check if secondary cluster meets minimum score requirement
        if secondary_avg_score >= params["secondary_min_score"]:
            # Check for weak domains if weak rejection is enabled
            if params["weak_rejection"]:
                weak_domains = [domain for domain, score in secondary_cluster 
                              if score < params["secondary_min_score"]]
                
                if not weak_domains:  # No weak domains, safe to include
                    for domain, score in secondary_cluster:
                        if len(selected_domains) < max_domains:
                            selected_domains[domain] = score
            else:
                # Weak rejection disabled, include all domains in secondary cluster
                for domain, score in secondary_cluster:
                    if len(selected_domains) < max_domains:
                        selected_domains[domain] = score
    
    # Rare case: if we have room and a third cluster with strong scores
    if len(clusters) > 2 and len(selected_domains) < max_domains:
        third_cluster = clusters[2]
        third_avg_score = sum(score for _, score in third_cluster) / len(third_cluster)
        
        # Only include third cluster if it has very strong scores (rare case for 4 domains)
        if third_avg_score >= params["primary_min_score"] and len(selected_domains) < 4:
            for domain, score in third_cluster:
                if len(selected_domains) < 4:  # Hard cap at 4
                    selected_domains[domain] = score
    
    return selected_domains

def select_domains_cluster_based_semantic(scores: dict) -> dict:
    """
    Cluster-based domain selection for semantic detection (updated to use improved logic).
    
    Parameters:
    - Uses improved cluster detection with method-specific parameters
    - Max domains: 3
    - Purpose: Identify the most semantically relevant domains
    """
    return select_domains_by_clusters_improved(scores, "semantic", max_domains=3)

def select_domains_cluster_based_keyword(scores: dict) -> dict:
    """
    Cluster-based domain selection for keyword detection (updated to use improved logic).
    
    Parameters:
    - Uses improved cluster detection with method-specific parameters
    - Max domains: 4
    - Purpose: Capture relevant domains based on keyword matches
    """
    return select_domains_by_clusters_improved(scores, "keyword", max_domains=4)

def select_domains_cluster_based_hybrid(scores: dict) -> dict:
    """
    Cluster-based domain selection for hybrid detection (updated to use improved logic).
    
    Parameters:
    - Uses improved cluster detection with method-specific parameters
    - Max domains: 3
    - Purpose: Final selection after combining semantic and keyword methods
    """
    return select_domains_by_clusters_improved(scores, "hybrid", max_domains=3)

def detect_domains_from_phrase_matching(query: str) -> dict:
    """
    Detect domains based on exact phrase matches with concept glossary.
    This provides strong signals when exact concept phrases are found in the query.
    
    Args:
        query: User's query text
        
    Returns:
        Dictionary of domains with scores based on phrase matches
    """
    try:
        # Load course glossary
        with open('courses/decision/glossary.json', 'r', encoding='utf-8') as f:
            glossary_to_use = json.load(f)
        
        # Normalize query for matching
        def _normalize_text(s: str) -> str:
            return re.sub(r"\s+", " ", s.lower().replace('-', ' ').replace('_', ' ')).strip()
        
        query_norm = _normalize_text(query)
        domain_scores = {}
        
        # Check each concept in the glossary for exact phrase matches
        for concept_name, concept_data in glossary_to_use.items():
            # Get the concept's domain
            concept_domain = CONCEPT_DOMAINS.get(concept_name.lower(), 'general')
            if concept_domain == 'general':
                continue  # Skip general domain concepts
            
            # Check if the concept name appears in the query
            concept_norm = _normalize_text(concept_name)
            if concept_norm in query_norm:
                # Exact match found - give strong signal
                if concept_domain not in domain_scores:
                    domain_scores[concept_domain] = 0
                domain_scores[concept_domain] += 1.0  # Strong signal for exact matches
            
            # Check aliases for exact matches
            if isinstance(concept_data, dict) and 'aliases' in concept_data:
                for alias in concept_data['aliases']:
                    alias_norm = _normalize_text(alias)
                    if alias_norm in query_norm:
                        if concept_domain not in domain_scores:
                            domain_scores[concept_domain] = 0
                        domain_scores[concept_domain] += 0.8  # Slightly lower signal for alias matches
        
        # Normalize scores to 0-1 range
        if domain_scores:
            max_score = max(domain_scores.values())
            if max_score > 0:
                domain_scores = {domain: score / max_score for domain, score in domain_scores.items()}
        
        return domain_scores
        
    except Exception as e:
        print(f"Error in detect_domains_from_phrase_matching: {e}")
        return {}

def hybrid_domain_detection(query: str) -> dict:
    """
    Improved hybrid domain detection combining semantic, keyword, and phrase matching methods with cluster-based selection.
    
    Args:
        query: User's query text
        
    Returns:
        Dictionary of selected domains with combined scores
    """
    try:
        # Step 1: Get domain scores from all methods
        semantic_scores = detect_domain_semantic(query)
        keyword_scores = detect_course_concept_domains(query)
        
        # Step 1.5: Get phrase matching signals from concept glossary
        phrase_scores = detect_domains_from_phrase_matching(query)
        
        # Step 2: Normalize scores within each method to prevent keyword dominance
        # Keyword scores can be much higher due to weighted scoring (3×strong + 2×modest + 1×weak)
        # Semantic scores are typically 0-1 cosine similarities
        # Phrase scores are typically 0-1 based on exact matches
        
        normalized_semantic = {}
        normalized_keyword = {}
        normalized_phrase = {}
        
        # Normalize semantic scores (already 0-1, just ensure max = 1.0)
        if semantic_scores:
            semantic_max = max(semantic_scores.values())
            if semantic_max > 0:
                normalized_semantic = {domain: score / semantic_max for domain, score in semantic_scores.items()}
            else:
                normalized_semantic = semantic_scores
        
        # Normalize keyword scores (can be 0-15+, normalize to 0-1)
        if keyword_scores:
            keyword_max = max(keyword_scores.values())
            if keyword_max > 0:
                normalized_keyword = {domain: score / keyword_max for domain, score in keyword_scores.items()}
            else:
                normalized_keyword = keyword_scores
        
        # Normalize phrase scores (already 0-1, just ensure max = 1.0)
        if phrase_scores:
            phrase_max = max(phrase_scores.values())
            if phrase_max > 0:
                normalized_phrase = {domain: score / phrase_max for domain, score in phrase_scores.items()}
            else:
                normalized_phrase = phrase_scores
        
        # Step 3: Apply cluster-based selection to each normalized method independently
        semantic_selected = select_domains_by_clusters_improved(normalized_semantic, "semantic", max_domains=3)
        keyword_selected = select_domains_by_clusters_improved(normalized_keyword, "keyword", max_domains=3)
        phrase_selected = select_domains_by_clusters_improved(normalized_phrase, "phrase", max_domains=3)
        
        # Step 4: Combine normalized scores with improved logic to prevent false positives
        combined_scores = {}
        
        # Get all unique domains from all three methods
        all_domains = set(semantic_selected.keys()) | set(keyword_selected.keys()) | set(phrase_selected.keys())
        
        for domain in all_domains:
            semantic_score = semantic_selected.get(domain, 0)
            keyword_score = keyword_selected.get(domain, 0)
            phrase_score = phrase_selected.get(domain, 0)
            
            # V1.6.6 fix: Use average of all methods for fair comparison
            raw_semantic_score = semantic_scores.get(domain, 0)
            min_semantic_threshold = 0.30  # Minimum raw semantic score to consider
            
            # Count how many methods identified this domain
            method_count = sum(1 for score in [semantic_score, keyword_score, phrase_score] if score > 0)
            
            # If phrase matching found the domain, give it strong weight (exact concept matches are very reliable)
            if phrase_score > 0:
                if method_count >= 2:
                    # Multiple methods agree - use weighted average with phrase matching getting extra weight
                    combined_scores[domain] = (phrase_score * 1.5 + semantic_score + keyword_score) / (method_count + 0.5)
                else:
                    # Only phrase matching found it - still include it (exact matches are reliable)
                    combined_scores[domain] = phrase_score
            # If both semantic and keyword methods identify the domain, use average (most reliable)
            elif keyword_score > 0 and semantic_score > 0:
                combined_scores[domain] = (keyword_score + semantic_score) / 2
            # If only keyword detection found the domain, use keyword score
            elif keyword_score > 0:
                combined_scores[domain] = keyword_score
            # If only semantic detection found the domain, require minimum raw semantic score
            elif raw_semantic_score >= min_semantic_threshold:
                combined_scores[domain] = semantic_score
            # Otherwise, exclude the domain (prevents false positives from semantic detection)
        
        # Step 5: Apply final cluster-based selection to combined scores
        if combined_scores:
            final_selected = select_domains_by_clusters_improved(combined_scores, "hybrid", max_domains=3)
            
            # Final check: if no specific domains are selected, return general as fallback
            # This ensures general domain is only picked when no behavioral, technical, strategic, or negotiation domains are selected
            if not final_selected:
                return {'general': 1.0}
            
            return final_selected
        
        # If both methods failed, return general as fallback
        return {'general': 1.0}
        
    except Exception as e:
        # Error in hybrid domain detection - using fallback
        # Fallback to semantic detection
        try:
            return detect_domain_semantic(query)
        except:
            # Final fallback to keyword detection
            return detect_course_concept_domains(query)

# Main execution for testing
if __name__ == "__main__":
    try:
        # Interactive mode
        while True:
            try:
                query = input("\nAsk a question (or type 'exit'): ")
            except (EOFError, KeyboardInterrupt):
                break
            
            if query.strip().lower() == "exit":
                break
            
            if not query.strip():
                # Please enter a non-empty question
                continue
            
            answer = process_query(query)
            # Test output removed for deployment
            
    except KeyboardInterrupt:
        pass 

def _title_case_term(term: str) -> str:
    try:
        return term.title()
    except Exception:
        return term

def _reorder_and_titlecase_concepts(lens_text: str, concepts: list) -> list:
    """Move lens-mentioned terms to front (substring match), preserve others, title-case terms for display."""
    try:
        lens_paras = [p.strip() for p in (lens_text or '').split('\n\n') if p.strip()]
        lens_core = '\n'.join(lens_paras[:2]).lower()
        mentioned, unmentioned = [], []
        for item in concepts or []:
            if not isinstance(item, dict):
                continue
            term = (item.get('term') or '')
            definition = item.get('definition')
            display_term = _title_case_term(term)
            new_item = {"term": display_term, "definition": definition}
            if term and term.lower() in lens_core:
                mentioned.append(new_item)
            else:
                unmentioned.append(new_item)
        return mentioned + unmentioned
    except Exception:
        out = []
        for item in concepts or []:
            if isinstance(item, dict):
                out.append({"term": _title_case_term(item.get('term') or ''), "definition": item.get('definition')})
        return out

_DENSITY_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "so", "because",
    "with", "without", "to", "for", "of", "in", "on", "at", "by", "from", "as",
    "is", "are", "was", "were", "be", "been", "being", "that", "this", "these",
    "those", "it", "its", "it's", "into", "about", "over", "under", "while", "when",
    "where", "who", "whom", "which", "what", "why", "how", "also", "can", "may",
    "might", "should", "would", "could", "will", "shall", "do", "does", "did", "have",
    "has", "had", "your", "their", "our", "we", "you", "let", "let's"
}


def _content_density_ratio(text: str) -> float:
    """Approximate information density via content-word ratio."""
    tokens = re.findall(r"[A-Za-z0-9']+", text)
    if not tokens:
        return 0.0
    content_tokens = 0
    for tok in tokens:
        lower = tok.lower()
        if lower.isdigit():
            content_tokens += 1
            continue
        if len(lower) <= 2:
            continue
        if lower in _DENSITY_STOPWORDS:
            continue
        content_tokens += 1
    return content_tokens / len(tokens)