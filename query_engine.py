#!/usr/bin/env python3
"""
Clean Query Engine - Produces only user-facing output without developer information
V1.6.5 Clean Version - No Streaming Support
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

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Global variables for lazy loading
_index = None
_metadata = None
_documents = None
_file_names = None
_model = None
_nlp = None

def load_data_lazily():
    """Load data only when needed"""
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

# Decision frameworks
FRAMEWORKS = {
    "decision tree": "A visual tool that maps out different options and their potential outcomes.",
    "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats.",
    "prospect theory": "Shows how people often value avoiding losses more than achieving gains."
}

# Add a list of analytical tools and their definitions for prompt injection
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
    "supply chain risk management": {"definition": "Identifying and mitigating risks in procurement and distribution", "core": False, "aliases": ['supply chain', 'procurement risk', 'distribution risk']},
    "leadership assessment": {"definition": "A systematic evaluation of leadership skills, styles, and effectiveness in decision-making contexts", "core": False, "aliases": ['leadership evaluation', 'leadership skills', 'management assessment']},
    "cognitive behaviors": {"definition": "Patterns of thinking and perception that influence decision-making, often studied to improve judgment and reduce bias", "core": True, "aliases": ['cognitive behavior', 'thinking patterns', 'mental models', 'cognitive bias']},
    "judgment intuitive bias": {"definition": "Systematic errors in thinking that affect decisions and judgments, often unconsciously", "core": True, "aliases": ['cognitive bias', 'judgment bias', 'thinking errors', 'decision bias']},
    "negotiation term sheet": {"definition": "A document outlining the key terms and conditions of a negotiation or agreement before final contracts are drafted", "core": True, "aliases": ['term sheet', 'negotiation terms', 'agreement terms', 'deal sheet']},
    "value creation": {"definition": "The process of generating benefits that exceed the costs for stakeholders in a decision or transaction", "core": True, "aliases": ['value generation', 'benefit creation', 'stakeholder value']},
    "risk tolerance assessment": {"definition": "An evaluation of an individual's or organization's willingness to accept risk in pursuit of objectives", "core": False, "aliases": ['risk tolerance', 'risk appetite', 'risk willingness']},
    "human-computer integration": {"definition": "The collaboration between humans and computer systems to enhance decision-making and problem-solving capabilities", "core": False, "aliases": ['human computer', 'human machine', 'computer integration']},
    "competitive advantage analysis": {"definition": "A strategic evaluation of factors that allow an organization to outperform its competitors", "core": True, "aliases": ['competitive advantage', 'competitive analysis', 'advantage analysis']},
    "value chain analysis": {"definition": "A process of analyzing the activities that add value to a product or service from conception to delivery", "core": True, "aliases": ['value chain', 'chain analysis', 'value analysis', 'activity-based analysis', 'value creation activities', 'value activities', 'chain of activities']},
    "investigative negotiation": {"definition": "A negotiation approach that focuses on uncovering underlying interests and information to create mutually beneficial outcomes", "core": True, "aliases": ['investigative', 'interest-based negotiation', 'information gathering', 'uncover interests', 'underlying interests', 'investigative negotiation']},
    "seasonal analysis": {"definition": "A forecasting method that identifies and models repeating patterns or cycles in time series data", "core": False, "aliases": ['seasonal patterns', 'seasonality', 'cyclical analysis', 'seasonality modeling', 'repeating patterns', 'cycles', 'seasonal forecasting', 'cyclical patterns', 'seasonal']},
    "regression": {"definition": "A statistical technique for estimating relationships among variables and predicting future values based on historical data", "core": True, "aliases": ['regression analysis', 'statistical regression', 'prediction model', 'forecast', 'historical', 'trends', 'future values', 'predict based on history', 'statistical prediction', 'forecasting']},
    "moving average": {"definition": "A method that smooths time series data by averaging values over a specified number of periods to identify trends", "core": False, "aliases": ['moving averages', 'trend smoothing', 'time series smoothing']},
    "semi-quantitative forecast": {"definition": "A forecasting approach that combines qualitative judgment with quantitative data for more robust predictions", "core": False, "aliases": ['semi quantitative', 'mixed forecasting', 'qualitative quantitative']},
    "profitability analysis": {"definition": "An assessment of the ability of a project or business to generate earnings compared to its costs and expenses", "core": True, "aliases": ['profitability', 'earnings analysis', 'financial performance']},
    "prospect theory": {"definition": "Shows how people often value avoiding losses more than achieving gains", "core": True, "aliases": ['prospect', 'loss aversion', 'gain loss']},
    "solver-based simulation": {"definition": "A computational approach that uses algorithms to find optimal or feasible solutions under constraints and uncertainty", "core": True, "aliases": ['solver simulation', 'algorithmic optimization', 'computational optimization']},
    "confirmation bias": {"definition": "Favoring evidence that supports existing beliefs", "core": True, "aliases": ['selective evidence bias', 'favor confirming information', 'seek confirming evidence', 'ignore contradicting', 'favor existing beliefs', 'confirm beliefs', 'favor confirming']},
    "anchoring bias": {"definition": "Relying too heavily on initial information", "core": True, "aliases": ['initial value bias', 'rely on first information', 'first piece of information', 'anchor on initial', 'stick to first impression', 'initial reference point', 'first information']},
    "framing bias": {"definition": "Decisions shaped by how options are presented", "core": True, "aliases": ['context framing']},
    "representative heuristic": {"definition": "Judging probability based on similarity", "core": True, "aliases": ['representativeness bias', 'judge by similarity', 'similar to past', 'based on similarity', 'judge probability by similarity']},
    "endowment effect": {"definition": "Valuing owned items higher than market value", "core": True, "aliases": ['ownership bias', 'value own work higher', 'overvalue own', 'my work is worth more', 'value my creation higher', 'own work more valuable', 'personal attachment', 'value own']},
    "status quo bias": {"definition": "Preference for maintaining the current state", "core": True, "aliases": ['resistance to change', 'status quo', 'maintaining current', 'not want to give up', 'reluctant to change', 'prefer current', 'refuse to change', 'stick with current', 'keep current', "don't want to change", 'prefer existing', 'stick to current']},
    "escalation of commitment": {"definition": "Continuing investment in failing endeavors", "core": True, "aliases": ['sunk cost fallacy', 'legacy project', 'continuing investment', 'failing project', 'persistent investment', 'keep investing', 'already spent', 'time investment', 'continue despite failure', 'invest more in failing', 'keep going despite problems', 'legacy']},
    "mental accounting": {"definition": "Treating money differently depending on its source", "core": True, "aliases": ['psychological budgeting']},
    "game theory": {"definition": "Strategic analysis of competitive interactions", "core": True, "aliases": ['strategic games', 'payoff analysis', 'competitive interactions', 'strategic analysis', 'competitive strategy', 'strategic thinking', 'competitive analysis', 'strategic interactions', 'game theory']},
    "winner's curse": {"definition": "Overpaying or overcommitting in competitive bidding", "core": True, "aliases": ['overpaying', 'competitive bidding', 'overcommitting', 'bidding war', 'auction', 'competitive situation', 'overbid', 'competitive overpayment', "winner's curse"]},
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
    "leadership assessment": "behavioral",
    "risk tolerance assessment": "behavioral",
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
    "solver-based simulation": "technical",
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
    
    # Technical/analytical concepts
    
    # Negotiation concepts
    "batna": "negotiation",
    "reservation point": "negotiation",
    "zopa": "negotiation",
    "investigative negotiation": "negotiation",
    "negotiation term sheet": "negotiation",
    "game theory": "negotiation",
    "winner's curse": "negotiation",
    "integrative negotiation": "negotiation",
    "distributive negotiation": "negotiation",
    
    # General decision-making concepts (can apply to multiple domains)
    "decision tree": "technical",
    "risk assessment": "technical",
    "contingency planning": "general",
    "grow model": "general",
    "ooda loop": "general",
    "supply chain risk management": "general",
    "human-computer integration": "technical"
}

# Global cache for concept embeddings to improve performance
_concept_embeddings_cache = None

def clear_concept_cache():
    """Clear the concept embeddings cache to force re-initialization with new format."""
    global _concept_embeddings_cache
    _concept_embeddings_cache = None
    print("🗑️ Concept embeddings cache cleared") 

def detect_course_concept_domains(query: str) -> dict:
    """
    Detect multiple course concept domains of a query based on keyword analysis.
    Returns: Dictionary with course concept domain names as keys and confidence scores as values.
    """
    query_lower = query.lower()
    course_concept_domains = {
        'behavioral': 0,
        'technical': 0,
        'strategic': 0,
        'negotiation': 0
    }
    
    # Behavioral/psychological indicators
    behavioral_keywords = [
        'team', 'teams', 'conflict', 'conflicts', 'value', 'values', 'behavior', 'behaviour',
        'psychology', 'psychological', 'bias', 'biases', 'cognitive', 'cognition',
        'judgment', 'judgement', 'leadership', 'personality', 'personalities',
        'motivation', 'motivational', 'emotion', 'emotional', 'human', 'people',
        'individual', 'group', 'social', 'interpersonal', 'communication',
        'behave', 'behaving', 'behaved', 'psychologic', 'cognitively', 'judge', 'judging',
        'lead', 'leading', 'led', 'motivate', 'motivating', 'motivated', 'feel', 'feeling',
        'felt', 'interact', 'interacting', 'interacted', 'communicate', 'communicating'
    ]
    for keyword in behavioral_keywords:
        if keyword in query_lower:
            course_concept_domains['behavioral'] += 1
    
    # Technical/analytical indicators
    technical_keywords = [
        'model', 'modeling', 'modeled', 'simulation', 'simulate', 'simulating', 'simulated',
        'forecast', 'forecasting', 'forecasted', 'optimization', 'optimize', 'optimizing', 
        'optimized', 'optimum', 'optimization strategy', 'optimization strategies',
        'maximization', 'maximize', 'maximizing', 'maximized', 'maximum', 'minimization', 
        'minimize', 'minimizing', 'minimized', 'minimum', 'simulation strategy', 'simulation strategies',
        'analysis', 'analyze', 'analyzing', 'analyzed', 'analytical',
        'data', 'statistical', 'statistics', 'mathematical', 'mathematics',
        'algorithm', 'algorithms', 'uncertainty', 'uncertain', 'uncertainties', 'probability', 
        'probabilistic', 'probable', 'calculate', 'calculation', 'calculating', 'calculated',
        'compute', 'computation', 'computing', 'computed', 'numerical', 'numeric',
        'assess', 'assessment', 'assessing', 'assessed', 'evaluate', 'evaluation', 
        'evaluating', 'evaluated', 'measure', 'measurement', 'measuring', 'measured',
        'determine', 'determining', 'determined', 'estimate', 'estimating', 'estimated',
        'predict', 'predicting', 'predicted', 'prediction', 'predictions',
        'production', 'demand', 'storage', 'capacity', 'inventory', 'supply chain',
        'operations', 'operational', 'manufacturing', 'logistics', 'distribution',
        # Technical implementation keywords
        'implement', 'implementation', 'implementing', 'implemented', 'deploy', 'deployment',
        'deploying', 'deployed', 'install', 'installation', 'installing', 'installed',
        'configure', 'configuration', 'configuring', 'configured', 'setup', 'set up',
        'integrate', 'integration', 'integrating', 'integrated', 'develop', 'development',
        'developing', 'developed', 'build', 'building', 'built', 'create', 'creating', 'created',
        'design', 'designing', 'designed', 'architecture', 'architectural', 'system', 'systems',
        'technical', 'technically', 'technology', 'technological', 'digital', 'automation',
        'automated', 'automate', 'automating', 'programming', 'program', 'programmed',
        'coding', 'code', 'coded', 'software', 'hardware', 'infrastructure', 'platform',
        # Enhanced technical keywords for analysis and evaluation
        'choose', 'choosing', 'chose', 'chosen', 'choice', 'choices', 'select', 'selecting', 'selected',
        'compare', 'comparing', 'compared', 'comparison', 'compare options', 'compare alternatives',
        'option', 'options', 'alternative', 'alternatives', 'approach', 'approaches',
        'method', 'methods', 'methodology', 'methodologies', 'technique', 'techniques',
        'tool', 'tools', 'framework', 'frameworks', 'process', 'processes', 'procedure', 'procedures',
        'strategy', 'strategies', 'strategic', 'strategically', 'plan', 'planning', 'planned',
        'decision', 'decisions', 'decide', 'deciding', 'decided', 'decision-making', 'decision making',
        'evaluate', 'evaluating', 'evaluated', 'evaluation', 'assess', 'assessing', 'assessed', 'assessment',
        'analyze', 'analyzing', 'analyzed', 'analysis', 'analytical', 'analytically',
        'examine', 'examining', 'examined', 'examination', 'investigate', 'investigating', 'investigated',
        'study', 'studying', 'studied', 'research', 'researching', 'researched',
        'test', 'testing', 'tested', 'experiment', 'experimenting', 'experimented',
        'trial', 'trials', 'pilot', 'piloting', 'piloted', 'prototype', 'prototyping', 'prototyped',
        'launch', 'launching', 'launched', 'release', 'releasing', 'released', 'deploy', 'deploying', 'deployed',
        'product', 'products', 'service', 'services', 'solution', 'solutions',
        'project', 'projects', 'initiative', 'initiatives', 'campaign', 'campaigns',
        'visualize', 'visualizing', 'visualized', 'visualization', 'visual', 'visually',
        'map', 'mapping', 'mapped', 'diagram', 'diagrams', 'chart', 'charts', 'graph', 'graphs',
        'tree', 'trees', 'flow', 'flows', 'flowchart', 'flowcharts', 'structure', 'structures',
        'model', 'modeling', 'modeled', 'models', 'framework', 'frameworks',
        'matrix', 'matrices', 'grid', 'grids', 'table', 'tables', 'list', 'lists',
        'categorize', 'categorizing', 'categorized', 'classification', 'classify', 'classifying', 'classified',
        'organize', 'organizing', 'organized', 'organization', 'structure', 'structuring', 'structured',
        'prioritize', 'prioritizing', 'prioritized', 'priority', 'priorities', 'rank', 'ranking', 'ranked',
        'score', 'scoring', 'scored', 'rating', 'ratings', 'rate', 'rating', 'rated',
        'weight', 'weighting', 'weighted', 'weighted analysis', 'weighted evaluation',
        'criteria', 'criterion', 'factor', 'factors', 'consideration', 'considerations',
        'metric', 'metrics', 'measure', 'measures', 'measuring', 'measured', 'measurement',
        'performance', 'perform', 'performing', 'performed', 'efficiency', 'effective', 'effectiveness',
        'cost', 'costs', 'costing', 'costed', 'benefit', 'benefits', 'beneficial',
        'risk', 'risks', 'risky', 'uncertainty', 'uncertain', 'uncertainties',
        'probability', 'probable', 'probabilistic', 'likely', 'likelihood',
        'scenario', 'scenarios', 'outcome', 'outcomes', 'result', 'results',
        'impact', 'impacts', 'effect', 'effects', 'consequence', 'consequences',
        'timeline', 'timelines', 'schedule', 'schedules', 'timing', 'time', 'timing',
        'resource', 'resources', 'budget', 'budgets', 'funding', 'fund', 'funds',
        'team', 'teams', 'staff', 'personnel', 'expertise', 'skills', 'capabilities',
        'technology', 'technological', 'technical', 'technically', 'digital', 'automation',
        'platform', 'platforms', 'system', 'systems', 'infrastructure', 'architecture'
    ]
    for keyword in technical_keywords:
        if keyword in query_lower:
            course_concept_domains['technical'] += 1
    
    # Strategic indicators
    strategic_keywords = [
        'strategy', 'strategic', 'strategically', 'market', 'markets', 'marketing',
        'competitive', 'competition', 'competitor', 'competitors', 'compete', 'competing',
        'advantage', 'advantageous', 'positioning', 'position', 'positioned', 'positioning',
        'business', 'businesses', 'organization', 'organizations', 'organize', 'organizing',
        'company', 'companies', 'industry', 'industries', 'industrial',
        'expansion', 'expand', 'expanding', 'expanded', 'growth', 'grow', 'growing', 'grown',
        'planning', 'plan', 'planned', 'corporate', 'enterprise', 'enterprising',
        'swot', 'value chain', 'profitability', 'profitable', 'stakeholder', 'stakeholders',
        'alignment', 'align', 'aligning', 'aligned', 'competitive advantage', 'market analysis', 
        'strategic analysis', 'business strategy', 'business strategies', 'corporate strategy', 
        'corporate strategies', 'strategic planning', 'competitive position', 'market position', 
        'market share', 'competitive edge', 'business model', 'business plan', 'strategic thinking', 
        'strategic decision', 'decision strategy', 'decision strategies', 'optimal strategy', 'optimal strategies', 
        'long-term', 'long term', 'career', 'careers', 'professional', 'profession', 'job', 'jobs',
        'offer', 'offers', 'offering', 'offered', 'opportunity', 'opportunities', 'choice', 'choices',
        'choose', 'choosing', 'chose', 'chosen', 'decide', 'deciding', 'decided', 'decision',
        'compare', 'comparing', 'compared', 'comparison', 'evaluate', 'evaluating', 'evaluated',
        'assessment', 'assess', 'assessing', 'assessed', 'option', 'options', 'alternative', 'alternatives',
        # Investment and financial keywords
        'investment', 'investments', 'invest', 'investing', 'invested', 'portfolio', 'portfolios',
        'financial', 'finance', 'financing', 'fund', 'funds', 'funding', 'funded',
        'return', 'returns', 'revenue', 'revenues', 'profit', 'profits', 'profitable',
        'wealth', 'wealthy', 'asset', 'assets', 'capital', 'equity', 'stock', 'stocks',
        'bond', 'bonds', 'mutual fund', 'mutual funds', 'etf', 'etfs', 'dividend', 'dividends',
        # Education and academic keywords
        'college', 'colleges', 'university', 'universities', 'school', 'schools', 'academic',
        'academics', 'education', 'educational', 'learning', 'learn', 'learned', 'studying',
        'study', 'studies', 'course', 'courses', 'program', 'programs', 'degree', 'degrees',
        'major', 'majors', 'minor', 'minors', 'curriculum', 'curricula', 'tuition', 'scholarship',
        'scholarships', 'admission', 'admissions', 'enroll', 'enrollment', 'enrolled',
        'graduate', 'graduation', 'undergraduate', 'graduate school', 'graduate schools',
        'skill', 'skills', 'development', 'training', 'certification'
    ]
    for keyword in strategic_keywords:
        if keyword in query_lower:
            course_concept_domains['strategic'] += 1
    
    # Negotiation indicators
    negotiation_keywords = [
        'negotiate', 'negotiation', 'negotiating', 'negotiated', 'negotiator', 'negotiators',
        'agreement', 'agree', 'agreeing', 'agreed', 'disagree', 'disagreeing', 'disagreed',
        'bargain', 'bargaining', 'bargained', 'bargaining strategy', 'bargaining strategies', 
        'negotiation strategy', 'negotiation strategies', 'contract', 'contracts', 'contracting', 'contracted', 
        'settlement', 'settle', 'settling', 'settled', 'compromise', 'compromising', 'compromised',
        'proposal', 'proposals', 'propose', 'proposing', 'proposed',
        'counteroffer', 'counteroffers', 'counter-offer', 'counter-offers',
        'terms', 'term', 'condition', 'conditions', 'concession', 'concessions',
        'deadlock', 'impasse', 'deadlocked', 'win-win', 'win win', 'zero-sum', 'zero sum'
    ]
    for keyword in negotiation_keywords:
        if keyword in query_lower:
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

def get_top_ranked_concepts(query: str, top_k: int = 3, custom_glossary: dict = None) -> List[Tuple[str, str]]:
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
        
        # Detect multiple domains for better concept filtering
        query_domains = detect_course_concept_domains(query)
        if query_domains:
            primary_domain = max(query_domains, key=query_domains.get)
        else:
            primary_domain = 'general'
        
        # Generate embedding for the query
        query_embedding = model.encode([query])
        
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
            _concept_embeddings_cache = model.encode(concept_texts)
        
        # Calculate cosine similarities
        similarities = util.pytorch_cos_sim(query_embedding, _concept_embeddings_cache)[0]
        
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
            score = similarities[i].item()
            
            # Check if any aliases appear in the query for additional score boost
            alias_boost = 0.0
            if isinstance(concept_data, dict) and "aliases" in concept_data:
                for alias in concept_data["aliases"]:
                    if alias.lower() in query_lower:
                        alias_boost = 0.15  # Boost score by 0.15 if alias found
                        break
            
            # Apply alias boost to similarity score
            score += alias_boost
            
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
            
            # Apply generic concept penalty to avoid domination by overly generic concepts
            generic_penalty = 0.0
            generic_concepts = [
                'swot analysis',         # Generic strategic tool
                'competitive analysis'    # Generic business analysis
            ]
            
            if concept_name in generic_concepts:
                # Apply penalty based on how generic the concept is
                if concept_name == 'swot analysis':
                    generic_penalty = 0.10  # Moderate penalty
                elif concept_name == 'competitive analysis':
                    generic_penalty = 0.08  # Light penalty
            
            # Apply generic penalty
            score -= generic_penalty
            
            if score > 0.20:  # Lower threshold to 0.20 to capture more concepts
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
                                domain_multiplier = 0.6  # Significant penalty
                            elif strongest_domain_score > 0.3:  # Moderate domain signal
                                domain_multiplier = 0.7  # Moderate penalty
                            else:  # Weak domain signal
                                domain_multiplier = 0.8  # Light penalty
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
        
        # Determine threshold based on domain situation
        if query_domains:
            # Check if this is effectively a single domain (one domain has >80% weight)
            sorted_domains = sorted(query_domains.items(), key=lambda x: x[1], reverse=True)
            primary_score = sorted_domains[0][1]
            
            if primary_score > 0.8:  # Single domain - use higher threshold
                primary_threshold = 0.50
                secondary_threshold = 0.40
                core_threshold = 0.35
            else:  # Multi-domain - use proper thresholds
                primary_threshold = 0.50  # Primary domain concepts
                secondary_threshold = 0.40  # Secondary domain concepts
                core_threshold = 0.35  # Core concepts just under threshold
        else:  # General query - use higher threshold
            primary_threshold = 0.50
            secondary_threshold = 0.40
            core_threshold = 0.35
        
        # Filter to only high-quality concepts with appropriate threshold
        high_quality_concepts = [(name, definition, score, is_core) for name, definition, score, is_core in concept_scores if score >= primary_threshold]
        
        # Check if we have core concepts that are just under the threshold but should be included
        core_concepts_under_threshold = [(name, definition, score, is_core) for name, definition, score, is_core in concept_scores if score >= core_threshold and is_core and score < primary_threshold]
        
        # Smart domain-based concept selection with proper allocation rules
        selected_concepts = []
        
        if query_domains:  # Multi-domain or single-domain query
            # Sort domains by score (highest first)
            sorted_domains = sorted(query_domains.items(), key=lambda x: x[1], reverse=True)
            
            # Check if this is effectively a single domain (one domain has >80% weight)
            primary_domain = sorted_domains[0][0]
            primary_score = sorted_domains[0][1]
            
            if primary_score > 0.8:  # Single domain (one domain dominates)
                # Single domain: up to 3 concepts from primary domain
                domain_concepts = [(name, definition) for name, definition, score, is_core in high_quality_concepts 
                                 if CONCEPT_DOMAINS.get(name, 'general') == primary_domain][:3]
                selected_concepts = domain_concepts
                
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
                    if domain_score > 0.1:  # Only include domains with meaningful weight
                        domain_concepts = [(name, definition) for name, definition, score, is_core in concept_scores 
                                         if score >= secondary_threshold and CONCEPT_DOMAINS.get(name, 'general') == domain_name][:1]
                        selected_concepts.extend(domain_concepts)
                
                # Enforce hard total cap of 4 tooltips maximum
                if len(selected_concepts) > 4:
                    selected_concepts = selected_concepts[:4]
                
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
        
        # Fallback: if insufficient high-quality concepts, use top concepts regardless of domain
        if len(selected_concepts) < 2:
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
        print(f"❌ Error in semantic concept extraction: {e}")
        # Fallback to fuzzy matching if semantic extraction fails
        return extract_concepts_with_fuzzy_matching(query, threshold=0.7)

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

# 1. V1.6.3 System Prompt - ThinkPal Decision Coach
SYSTEM_PROMPT_ANALYTICS = """You are ThinkPal: Decision Coach, a structured GPT tutor that helps students think through complex decisions using strategic logic, analytical tools, and human behavior awareness.

Your job is to generate thoughtful, well-structured answers to student decision-making questions using the following format:

---

**Strategic Thinking Lens**

This is the analytical core. Write **2 well-developed paragraphs** (around **120–160 words**). This section should cover **1–3 relevant domains**, include **tradeoffs**, and be approximately **50% of the answer**. Avoid overloading with bullets or headers. Do **not** use literal framework terms like "strategic mindset" or "human behavior awareness." Instead, express those ideas naturally (e.g. "thinking long-term," "anticipating stakeholder reactions," etc.). Focus on strategic thinking, analytical tools, and human behavior awareness relevant to the query.

---

**Story in Action**

Provide a short 3–4 sentence example. Must mirror the ideas in the Strategic Thinking Lens without being longer or more detailed.

---

**Follow-up Prompts**

Offer 2–4 reflective questions. These should invite deeper thinking and not repeat the above content.

---

**Concepts/Tools**

List 2–3 course concepts using this exact format:

Concept Name: Short definition
Concept Name: Short definition

Definitions must be on the same line as the concept name. Do not use dashes, bullets, or multiline formatting. These appear as tooltips in the UI. Do not define them elsewhere in the answer.

If the query is narrow or course-specific concepts do not apply, include broader decision-making concepts such as: Stakeholder Alignment, Strategic Framing, or Risk Assessment.

---

Formatting Rules:
- Use markdown-style headers (e.g., **Strategic Thinking Lens**) to label each section.
- Break long answers into clear paragraphs.
- Do not mention that you are an AI.
- Output must sound natural, helpful, and avoid sounding like a framework summary. Your goal is to guide the student into thinking strategically — not just to label what they're doing."""

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

def calculate_optimal_tokens(query_length: int, context_length: int) -> int:
    """Calculate optimal token limit based on input size"""
    total_input = query_length + context_length
    if total_input > 6000:
        return 800
    elif total_input > 3000:
        return 1000
    else:
        return 1200

def robust_api_call(client, system_prompt: str, user_message: str, max_tokens: int = 0, max_retries: int = 3):
    """Handle API calls with retries using system/user message structure"""
    tokens_to_use = max_tokens if max_tokens > 0 else openai_max_tokens
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=1.2,  # Increased for more variety
                max_tokens=tokens_to_use
            )
            return response, None
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 * (2 ** attempt))
            else:
                return None, str(e)
    return None, "Max retries exceeded"

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

def extract_tools_from_section(content: str) -> list:
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
    concept_lines = re.findall(r'^([^:\n]+?):\s*([^\n]+)$', tool_section, re.MULTILINE)
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
    """Generate fallback concepts based on query keywords when no valid concepts are extracted."""
    query_lower = query.lower()
    fallback_concepts = []
    
    # Keyword-based concept mapping
    keyword_concepts = {
        "risk": ["Risk Assessment: Systematic evaluation of potential threats and their impact on decision outcomes", "Stakeholder Alignment: Ensuring all parties' interests are considered and balanced"],
        "planning": ["Strategic Framing: Structuring the decision problem to clarify objectives and alternatives", "Scenario Analysis: Exploring different future possibilities to prepare for uncertainty"],
        "career": ["Career Path Analysis: Evaluating long-term professional development and growth opportunities", "Personal Values Assessment: Aligning decisions with core personal and professional values"],
                    "finance": ["Risk Tolerance Assessment: Understanding your comfort level with financial uncertainty"],
        "negotiation": ["Stakeholder Alignment: Ensuring all parties' interests are considered and balanced", "Value Creation: Identifying opportunities to create mutual benefits in negotiations"],
        "uncertainty": ["Scenario Analysis: Exploring different future possibilities to prepare for uncertainty", "Risk Assessment: Systematic evaluation of potential threats and their impact"],
        "strategy": ["Strategic Framing: Structuring the decision problem to clarify objectives and alternatives", "Competitive Analysis: Understanding your position relative to alternatives and competitors"],
        "team": ["Stakeholder Alignment: Ensuring all parties' interests are considered and balanced", "Leadership Assessment: Evaluating leadership styles and their impact on team decisions"],
        "supply": ["Supply Chain Risk Management: Identifying and mitigating risks in procurement and distribution", "Stakeholder Alignment: Ensuring all parties' interests are considered and balanced"],
        "management": ["Leadership Assessment: Evaluating leadership styles and their impact on organizational decisions", "Strategic Framing: Structuring the decision problem to clarify objectives and alternatives"]
    }
    
    # Find matching keywords and add corresponding concepts
    for keyword, concepts in keyword_concepts.items():
        if keyword in query_lower:
            for concept in concepts:
                if concept not in fallback_concepts:
                    fallback_concepts.append(concept)
                    if len(fallback_concepts) >= 3:
                        break
            if len(fallback_concepts) >= 3:
                break
    
    # If no keyword matches, use general fallbacks
    if len(fallback_concepts) < 2:
        general_fallbacks = [
            "Strategic Framing: Structuring the decision problem to clarify objectives and alternatives",
            "Stakeholder Alignment: Ensuring all parties' interests are considered and balanced",
            "Risk Assessment: Systematic evaluation of potential threats and their impact on decision outcomes"
        ]
        for concept in general_fallbacks:
            if concept not in fallback_concepts:
                fallback_concepts.append(concept)
                if len(fallback_concepts) >= 2:
                    break
    
    return fallback_concepts[:3]  # Return max 3 concepts

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
    
    # Operations - check FIRST to avoid conflicts with other fields
    if any(word in q for word in ["production", "capacity", "forecast", "uncertainty", "simulation", "scenario", 
                                  "linear programming", "supply chain", "monte carlo", "solver", "modeling", 
                                  "constraints", "variables", "mathematical", "computational", 
                                  "statistical", "analysis", "planning", "supplier"]) and not any(word in q for word in ["AI", "artificial intelligence", "machine learning", "automation", "digital", "software", "platform", "risk", "risks", "crisis", "mitigation", "negotiate", "negotiation"]):
        return "operations"
    
    # Business detection - new field for general business decisions
    if any(word in q for word in ["business strategy", "business model", "business decision", "business risk", 
                                  "business implication", "business impact", "business consideration", 
                                  "business trade-off", "business optimization", "business efficiency"]) and not any(word in q for word in ["startup", "entrepreneur", "founder", "launch", "venture", "job", "career", "employment", "esg", "sustainability", "environmental"]):
        return "business"
    
    if any(word in q for word in ["invest", "investment", "portfolio", "stocks", "bonds", "finance", "retirement"]):
        return "finance"
    
    # Technology detection - expanded keywords (check BEFORE startup to avoid conflicts)
    if any(word in q for word in ["technology", "AI", "automation", "digital", "software", "adopt", "platform",
                                  "artificial intelligence", "machine learning", "automate", "system", "algorithm", "algorithms"]) and not any(word in q for word in ["startup", "entrepreneur", "founder", "launch", "venture", "project", "projects", "milestone", "milestones", "deliverable", "deliverables"]):
        return "technology"
    
    # Risk Management detection - check BEFORE operations to avoid conflicts
    if any(word in q for word in ["risk", "risks", "threat", "threats", 
                                  "hazard", "exposure", "liability", "contingency", "resilience", 
                                  "crisis", "volatility", "probability", "scenario", "mitigation", 
                                  "insurance", "compliance", "regulatory risk", "supply chain risk", "supply chain risks"]) and not any(word in q for word in ["health", "medical", "doctor", "wellness", "fitness", "production", "capacity", "forecast", "simulation", "currency"]):
        return "risk_management"
    
    # Project Management detection - check BEFORE technology to avoid conflicts
    if any(word in q for word in ["project", "projects", "task", "tasks", "milestone", "milestones", 
                                  "schedule", "scheduling", "timeline", "deliverable", "deliverables", 
                                  "work breakdown", "wbs", "pmo", "program management", 
                                  "critical path", "gantt", "deadline", "resource allocation", 
                                  "scope", "budget", "stakeholders", "execution", "software development project", "development project"]) and not any(word in q for word in ["startup", "entrepreneur", "founder", "launch", "venture", "AI", "automation", "digital", "r&d", "research"]):
        return "project_management"
    
    if any(word in q for word in ["team", "leader", "leadership", "conflict", "manager", "staff"]) and not any(word in q for word in ["employee", "retention", "engagement", "talent", "hiring", "recruiting", "workforce", "human capital"]):
        return "leadership"
    
    # Human Capital Strategy detection - check BEFORE innovation to avoid conflicts
    if any(word in q for word in ["human capital", "workforce", "talent", "hiring", "recruiting", 
                                  "recruitment", "staffing", "onboarding", "training", "development", 
                                  "retention", "turnover", "succession planning", 
                                  "diversity", "inclusion", "equity", "hr", "human resources", 
                                  "performance management", "upskilling", "reskilling", 
                                  "employee engagement", "employee retention", "morale", "benefits"]) and not any(word in q for word in ["job", "career", "employment", "offer", "opportunity", "research", "development", "prototype", "innovation"]):
        return "human_capital"
    
    # Marketing & Customer Strategy detection - check BEFORE innovation to avoid conflicts
    if any(word in q for word in ["marketing", "market", "customer", "client", "consumer", 
                                  "brand", "branding", "reputation", "loyalty", "segmentation", 
                                  "target market", "advertising", "promotion", "pricing", 
                                  "positioning", "product launch", "demand", "sales", "revenue", 
                                  "campaign", "conversion", "customer journey", "feedback", 
                                  "retention", "acquisition"]) and not any(word in q for word in ["startup", "entrepreneur", "founder", "launch", "venture", "research", "development", "prototype", "innovation", "market entry", "emerging economies"]):
        return "marketing"
    
    # Globalization & International Trade detection - check BEFORE marketing to avoid conflicts
    if any(word in q for word in ["global", "international", "worldwide", "cross-border", "foreign", 
                                  "export", "import", "tariff", "tariffs", "quota", "customs", 
                                  "trade agreement", "fta", "currency", "exchange rate", 
                                  "foreign investment", "fdi", "localization", "multinational", 
                                  "outsourcing", "offshoring", "supply chain disruption", 
                                  "geopolitical", "sanctions", "market entry", "emerging economies"]) and not any(word in q for word in ["marketing", "customer", "brand", "advertising", "promotion"]):
        return "globalization"
    
    # Education detection - check BEFORE innovation to avoid conflicts
    if any(word in q for word in ["degree", "masters", "certification", "training", "course", "education", "skills", "online course", "skill development"]) and not any(word in q for word in ["r&d", "research", "prototype", "innovation", "new technology", "product development"]):
        return "education"
    
    # Innovation & R&D detection - check BEFORE startup to avoid conflicts
    if any(word in q for word in ["innovation", "innovate", "innovating", "r&d", "research", "development", 
                                  "prototype", "prototyping", "product design", "product development", 
                                  "patent", "intellectual property", "ip", "lab", "experimentation", 
                                  "new technology", "breakthrough", "discovery", "pilot program", 
                                  "beta test", "iteration", "competing r&d", "r&d projects", "competing projects"]) or ("competing" in q and "r&d" in q) or ("competing" in q and "research" in q):
        return "innovation"
    
    # Sustainability & ESG detection - check BEFORE startup to avoid conflicts
    if any(word in q for word in ["sustainability", "sustainable", "esg", "environment", "environmental", 
                                  "green", "carbon", "emissions", "footprint", "renewable", 
                                  "csr", "corporate social responsibility", "ethical sourcing", 
                                  "climate", "ecological", "compliance", "governance", 
                                  "responsibility", "social impact", "stakeholder trust", "esg initiatives"]) and not any(word in q for word in ["startup", "entrepreneur", "founder", "launch", "venture"]):
        return "sustainability"
    
    if any(word in q for word in ["admission", "college", "university", "school"]):
        return "admission"
    
    if any(word in q for word in ["relocate", "move", "relocation", "city", "country", "immigrate"]):
        return "relocation"
    
    # Ethics detection - expanded keywords
    if any(word in q for word in ["ethics", "values", "integrity", "social issue", "mission", "responsibility", 
                                  "ethical", "dilemma", "moral", "right", "wrong"]):
        return "ethics"
    
    if any(word in q for word in ["health", "wellness", "doctor", "insurance", "medical", "fitness", "mental health"]):
        return "health"
    
    # Job detection - more specific keywords to avoid false positives
    if any(word in q for word in ["job offer", "job opportunity", "employment offer", "position offer"]) or        (any(word in q for word in ["job", "position", "employment"]) and 
        any(word in q for word in ["offer", "opportunity", "accept", "choose", "decide", "compare"])):
        return "job"
    
    if any(word in q for word in ["negotiate", "negotiation", "deal", "partner", "agreement", "batna", "supplier", "vendor", "contract"]) and not any(word in q for word in ["production", "capacity", "forecast", "simulation", "supply chain", "operations"]):
        return "operations"
    
    # Startup detection - expanded keywords
    if any(word in q for word in ["startup", "product", "entrepreneur", "founder", "business model", "new business", 
                                  "launch", "venture", "company"]) and not any(word in q for word in ["esg", "sustainability", "environmental", "green", "carbon", "emissions"]):
        return "startup"
    
    return "general"

def context_aware_fallbacks(query: str):
    """Generate context-aware fallback content for each ThinkPal V1.6.3 section based on the query application field."""
    # Use course concept domain-aware logic for Strategic Thinking Lens
    course_concept_domains = detect_course_concept_domains(query)
    application_field = extract_application_field(query)
    
    # Determine primary course concept domain for Strategic Thinking Lens
    if course_concept_domains:
        primary_course_domain = max(course_concept_domains, key=course_concept_domains.get)
    else:
        primary_course_domain = 'general'
    
    # Generate Strategic Thinking Lens based on course concept domain and application field
    strategic_lens = generate_course_domain_strategic_lens(query, primary_course_domain, application_field)
    
    # Use application field for Story in Action and other sections
    if application_field == "admission":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Sarah, a high school senior, compares three college offers using a weighted scoring model. She lists her priorities—academic reputation, cost, campus culture, and location. After visiting each campus and speaking with current students, she weighs the value of strong alumni networks against the appeal of lower tuition. Sarah ultimately chooses the school that best balances her career goals and financial constraints.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Decision Tree: Mapping out options and outcomes\n- Weighted Scoring Model: Comparing choices using weighted criteria"
        }
    if application_field == "job":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Alex, a software engineer, receives two job offers and creates a decision matrix to compare them systematically. He evaluates growth opportunities, compensation packages, company culture, and work-life balance. One offer provides an immediate salary boost, while the other offers mentorship programs and clear advancement paths. After consulting with mentors and considering his long-term career vision, Alex chooses the role that best aligns with his professional goals and personal values.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Weighted Scoring Model: Structured option comparison\n- Pros and Cons List: Simple evaluation of positives and negatives"
        }
    if application_field == "startup":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Maria, an entrepreneur, evaluates two product ideas using Lean Canvas methodology. She conducts thorough market research to understand customer demand, assesses resource requirements, and analyzes potential risks for each option. One path offers quick entry into a crowded market with established demand, while the other focuses on innovative features with slower market adoption. After consulting with industry experts and considering her risk tolerance, Maria selects the option that best balances immediate feasibility with long-term growth potential.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Lean Canvas: One-page business planning tool\n- SWOT Analysis: Assessing strengths, weaknesses, opportunities, and threats"
        }

    if application_field == "operations":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Lisa, an operations manager, models multiple supply chain scenarios using Monte Carlo simulation to account for demand uncertainty. She compares cost efficiency with operational flexibility, analyzing how different scenarios affect both short-term performance and long-term resilience. Her comprehensive analysis reveals that the most resilient plan balances steady operational costs with the adaptability needed to respond to demand fluctuations and supply disruptions.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Scenario Analysis: Exploring possible futures\n- Monte Carlo Simulation: Modeling uncertainty through random sampling"
        }
    if application_field == "finance":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "James, a mid-career professional, weighs investing in index funds versus keeping money in a money market account. He analyzes historical returns, considers his risk tolerance, and balances immediate liquidity needs with long-term growth potential. After consulting with a financial advisor and reviewing his emergency fund, James decides on an allocation that reflects both financial stability and the opportunity cost of being too conservative.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Risk Assessment: Evaluating potential threats\n- Expected Value: Estimating average outcomes under uncertainty"
        }
    if application_field == "health":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Maya, a young professional, compares three health insurance plans using a decision matrix. She carefully weighs monthly premiums, provider network coverage, emergency care benefits, and prescription drug coverage. After researching each plan's reputation and reading customer reviews, Maya balances affordability with comprehensive coverage, ensuring both immediate health security and long-term financial stability for unexpected medical expenses.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Risk Tolerance Assessment: Measuring comfort with uncertainty"
        }
    if application_field == "education":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Daniel debates pursuing a master's degree versus earning industry certifications. He compares tuition costs, time commitments, and potential career impact for each option. After researching salary data and consulting with professionals in his field, Daniel weighs the long-term credibility of a degree against the faster skill acquisition of certifications, ultimately choosing the option best aligned with his career goals and financial constraints.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Opportunity Cost: Value of the next-best alternative\n- Strategic Framing: Structuring the decision problem clearly"
        }
    if application_field == "relocation":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Emily and her partner consider relocating to a new city for career opportunities. They conduct thorough research on job markets, cost of living differences, and quality of life factors in both locations. Their scenario analysis reveals better career growth potential in the new city but significantly less family support and higher living costs. They must carefully balance immediate quality of life considerations with long-term career and financial prospects.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Scenario Planning: Preparing for multiple futures\n- Stakeholder Alignment: Balancing the interests of key people"
        }
    if application_field == "leadership":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Mark, a team leader, notices rising conflict between two departments over resource allocation and project priorities. He facilitates structured dialogue sessions, balances empathy with clear authority, and establishes transparent communication channels. His systematic approach not only resolves the immediate conflict but also restores trust and collaboration while strengthening the long-term team culture and preventing similar issues.",
            'Follow-up Prompts': ["- What factors might drive this conflict?", "- How can you balance empathy with authority?"],
            'Concepts/Tools': "- Stakeholder Alignment: Ensuring balanced interests\n- Leadership Assessment: Evaluating leadership effectiveness"
        }
    if application_field == "ethics":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Jordan, a nonprofit director, faces mounting pressure to take a public stance on a controversial social issue that directly impacts her organization's mission. She carefully weighs mission alignment, stakeholder trust, donor relationships, and long-term organizational reputation. After consulting with board members and legal counsel, Jordan crafts a values-driven but diplomatically balanced statement that protects the organization's integrity while maintaining credibility with all stakeholders.",
            'Follow-up Prompts': ["- How does this align with your values?", "- What are the risks of taking a public stance?"],
            'Concepts/Tools': "- Strategic Framing: Clarifying objectives and risks\n- Value Creation: Generating benefits that exceed costs"
        }
    if application_field == "business":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Michael, a business analyst, evaluates strategic options using a comprehensive decision framework. He analyzes market conditions, competitive dynamics, and resource constraints to identify the optimal path forward. By weighing short-term operational efficiency against long-term strategic positioning, Michael develops a balanced approach that maximizes value creation while managing risk exposure.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- SWOT Analysis: Assessing strengths, weaknesses, opportunities, and threats\n- Decision Matrix: Structured evaluation of multiple criteria"
        }
    if application_field == "technology":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Carlos, a small business owner, considers adopting AI-powered customer support tools to improve efficiency and reduce response times. He carefully weighs the potential efficiency gains against employee training requirements, customer experience impacts, and implementation costs. After consulting with his team and researching similar implementations, Carlos's decision hinges on balancing the speed of technology adoption with his organization's readiness for change and ability to maintain service quality.",
            'Follow-up Prompts': ["- What long-term benefits could technology bring?", "- What barriers might slow adoption?"],
            'Concepts/Tools': "- Human-Computer Integration: Enhancing decisions with technology"
        }
    if application_field == "risk_management":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Lisa, a risk manager, evaluates potential threats to her organization's supply chain. She conducts a comprehensive risk assessment, identifying vulnerabilities in supplier relationships, geopolitical factors, and natural disaster scenarios. By developing contingency plans and monitoring early warning indicators, Lisa creates a resilient framework that balances risk mitigation costs with potential impact severity.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Risk Assessment Matrix: Evaluating probability and impact\n- Scenario Planning: Preparing for multiple futures"
        }
    if application_field == "project_management":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "David, a project manager, faces competing stakeholder demands while managing a critical software development project. He uses work breakdown structures to identify dependencies, critical path analysis to optimize timelines, and stakeholder management techniques to align expectations. By balancing scope, time, and cost constraints, David delivers the project successfully while maintaining team morale and stakeholder satisfaction.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Critical Path Analysis: Identifying project bottlenecks\n- Stakeholder Management: Balancing competing interests"
        }
    if application_field == "sustainability":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Emma, a sustainability director, navigates the complex trade-offs between environmental responsibility and business profitability. She evaluates carbon footprint reduction initiatives, assesses stakeholder expectations, and balances short-term costs with long-term brand value. By integrating ESG considerations into strategic decision-making, Emma creates value for both shareholders and society.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Triple Bottom Line: People, Planet, Profit\n- ESG Framework: Environmental, Social, Governance criteria"
        }
    if application_field == "innovation":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Alex, an R&D manager, evaluates competing innovation projects with limited resources. He assesses market potential, technical feasibility, and strategic alignment for each option. By balancing breakthrough potential with implementation risk, Alex prioritizes projects that offer the best combination of innovation impact and organizational capability.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Innovation Portfolio: Balancing risk and reward\n- Stage-Gate Process: Systematic innovation evaluation"
        }
    if application_field == "human_capital":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Sarah, an HR director, develops a comprehensive talent strategy to address skill gaps and improve retention. She analyzes workforce demographics, identifies critical roles, and designs development programs that balance individual growth with organizational needs. By aligning human capital investments with business strategy, Sarah creates a sustainable competitive advantage.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Talent Pipeline: Building future capabilities\n- Succession Planning: Ensuring leadership continuity"
        }
    if application_field == "marketing":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Mike, a marketing director, evaluates customer acquisition strategies across multiple channels. He analyzes customer lifetime value, conversion rates, and brand positioning to optimize marketing spend. By balancing short-term sales targets with long-term brand building, Mike creates a sustainable competitive advantage in crowded markets.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- Customer Lifetime Value: Long-term customer worth\n- Brand Positioning: Distinctive market position"
        }
    if application_field == "globalization":
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Maria, a global operations director, evaluates market entry strategies for emerging economies. She analyzes political risks, currency fluctuations, and cultural differences while assessing market potential and competitive dynamics. By balancing local adaptation with global scale, Maria creates sustainable competitive advantages in diverse markets.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, application_field),
            'Concepts/Tools': "- PESTEL Analysis: Political, Economic, Social, Technological, Environmental, Legal factors\n- Cultural Intelligence: Adapting to local contexts"
        }
    # General fallback - but try to infer context from the query
    # For follow-up questions about trade-offs, objectives, etc., use strategic context
    if any(word in query.lower() for word in ["trade-off", "trade-offs", "trade off", "trade offs", "objectives", "goals", "priorities", "options", "alternatives", "choices"]):
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "A strategic decision-maker systematically evaluates their options by creating a comprehensive framework. They identify key criteria, research alternatives thoroughly, and use analytical tools to compare trade-offs. After weighing both immediate impacts and long-term consequences, they make an informed choice that balances competing priorities and aligns with their strategic objectives.",
            'Follow-up Prompts': generate_domain_aware_fallback_questions(query, "strategic"),
            'Concepts/Tools': "- Strategic Framing: Structuring the decision problem clearly\n- Trade-off Analysis: Comparing competing priorities systematically"
        }
    else:
        return {
            'Strategic Thinking Lens': strategic_lens,
            'Story in Action': "Someone facing a complex decision creates a systematic framework to evaluate their options. They list their priorities, research available alternatives, and use structured tools to compare trade-offs. After considering both immediate consequences and long-term implications, they make a well-informed choice that balances multiple competing factors and aligns with their core values.",
            'Follow-up Prompts': ["- What are your main objectives?", "- What trade-offs exist between your options?"],
            'Concepts/Tools': "- Decision Matrix: Comparing alternatives systematically\n- Pros and Cons List: Evaluating positives and negatives"
        }

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
            'job': " Consider how this decision aligns with your career trajectory and personal values.",
            'startup': " Evaluate both the immediate feasibility and long-term growth potential of each option.",
            'finance': " Balance risk and return while considering your financial goals and constraints.",
            'operations': " Consider both efficiency and resilience in your analysis.",
            'health': " Prioritize both immediate needs and long-term well-being.",
            'education': " Weigh the investment in time and money against potential career benefits.",
            'relocation': " Consider both personal and professional factors in your decision.",
            'leadership': " Think about how this decision will affect team dynamics and organizational culture.",
            'ethics': " Consider the moral implications and stakeholder impact of your choice.",
            'business': " Evaluate both short-term operational efficiency and long-term strategic positioning.",
            'technology': " Balance innovation potential with implementation challenges and user adoption.",
            'risk_management': " Consider both probability and impact in your risk assessment.",
            'project_management': " Balance scope, time, and cost constraints while maintaining quality.",
            'sustainability': " Consider environmental, social, and governance factors alongside business objectives.",
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
        # Load data lazily
        index, metadata, documents, file_names, model, nlp = load_data_lazily()
        
        # Extract concepts using semantic similarity
        concepts = get_top_ranked_concepts(query, top_k=3, custom_glossary=course_config.get('glossary') if course_config else None)
        
        # Detect application field for context-aware generation
        application_field = extract_application_field(query)
        
        # Generate context-aware fallback content
        fallback_content = context_aware_fallbacks(query)
        
        # Build user message with context
        user_message = f"Query: {query}\n\n"
        
        # Add relevant concepts as context
        if concepts:
            concept_context = "Relevant concepts to consider:\n"
            for concept_name, definition in concepts:
                concept_context += f"- {concept_name}: {definition}\n"
            user_message += concept_context + "\n"
        
        # Add application field context
        user_message += f"Application field: {application_field}\n\n"
        
        # Add analytical tools context
        tools_context = "Available analytical tools:\n"
        for tool_name, tool_def in ANALYTICAL_TOOLS[:5]:  # Limit to top 5 tools
            tools_context += f"- {tool_name}: {tool_def}\n"
        user_message += tools_context + "\n"
        
        # Make API call
        response, error = robust_api_call(
            client=client,
            system_prompt=SYSTEM_PROMPT_ANALYTICS,
            user_message=user_message,
            max_tokens=calculate_optimal_tokens(len(query), len(user_message))
        )
        
        if error:
            print(f"❌ API call failed: {error}")
            # Return fallback content
            return format_fallback_response(fallback_content)
        
        # Extract response content
        answer_raw = response.choices[0].message.content.strip()
        
        # Ensure proper structure
        answer = enforce_thinkpal_structure(answer_raw, query)
        
        # Extract and validate concepts/tools
        concepts_tools = extract_tools_from_section(answer)
        
        # If no valid concepts extracted, use fallback
        if not concepts_tools:
            fallback_concepts = generate_fallback_concepts(query)
            if fallback_concepts:
                # Replace concepts section with fallback
                answer = re.sub(
                    r'\*\*Concepts/Tools\*\*.*?(?=\n\n|$)',
                    f'**Concepts/Tools**\n\n' + '\n'.join(fallback_concepts),
                    answer,
                    flags=re.DOTALL
                )
        
        return answer
        
    except Exception as e:
        print(f"❌ Error in process_query: {e}")
        traceback.print_exc()
        # Return fallback content
        fallback_content = context_aware_fallbacks(query)
        return format_fallback_response(fallback_content)

def enforce_thinkpal_structure(answer: str, query: str = "") -> str:
    """Ensure the answer follows ThinkPal structure with all required sections."""
    
    # Check if answer already has proper structure
    if re.search(r'\*\*Strategic Thinking Lens\*\*', answer, re.IGNORECASE) and \
       re.search(r'\*\*Story in Action\*\*', answer, re.IGNORECASE) and \
       re.search(r'\*\*Follow-up Prompts\*\*', answer, re.IGNORECASE) and \
       re.search(r'\*\*Concepts/Tools\*\*', answer, re.IGNORECASE):
        return answer
    
    # If not, generate fallback content
    fallback_content = context_aware_fallbacks(query)
    return format_fallback_response(fallback_content)

def format_fallback_response(fallback_content: dict) -> str:
    """Format fallback content into proper ThinkPal structure."""
    sections = []
    
    if 'Strategic Thinking Lens' in fallback_content:
        sections.append(f"**Strategic Thinking Lens**\n\n{fallback_content['Strategic Thinking Lens']}")
    
    if 'Story in Action' in fallback_content:
        sections.append(f"**Story in Action**\n\n{fallback_content['Story in Action']}")
    
    if 'Follow-up Prompts' in fallback_content:
        prompts = fallback_content['Follow-up Prompts']
        if isinstance(prompts, list):
            prompts_text = '\n'.join(prompts)
        else:
            prompts_text = prompts
        sections.append(f"**Follow-up Prompts**\n\n{prompts_text}")
    
    if 'Concepts/Tools' in fallback_content:
        sections.append(f"**Concepts/Tools**\n\n{fallback_content['Concepts/Tools']}")
    
    return '\n\n'.join(sections)

# Main execution for testing
if __name__ == "__main__":
    try:
        # Interactive mode
        while True:
            try:
                query = input("\nAsk a question (or type 'exit'): ")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Exiting. Goodbye!")
                break
            
            if query.strip().lower() == "exit":
                print("👋 Exiting. Goodbye!")
                break
            
            if not query.strip():
                print("⚠️ Please enter a non-empty question.")
                continue
            
            answer = process_query(query)
            print(f"{answer}")
            
    except KeyboardInterrupt:
        print("\n👋 Exiting. Goodbye!") 