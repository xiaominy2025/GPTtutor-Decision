#!/usr/bin/env python3
"""
Clean Expanded Entities Module for V1.6.5.1
Comprehensive entity extraction and classification for decision-making queries
WITH STOPLIST FILTERING to remove generic terms
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import lru_cache

# ============================================================================
# STOPLIST LOADING
# ============================================================================

def load_entity_stoplist() -> set:
    """Load the entity stoplist to filter out generic terms"""
    try:
        with open("entity_stoplist.json", "r", encoding="utf-8") as f:
            stoplist_data = json.load(f)
        return set(stoplist_data.get("all_stoplist_terms", []))
    except Exception as e:
        print(f"⚠️ Warning: Could not load entity stoplist: {e}")
        # Fallback to basic stoplist
        return {
            "decision", "management", "planning", "budget", "business", "leadership", "organization",
            "strategy", "analysis", "assessment", "evaluation", "consideration", "approach"
        }

# Load stoplist at module level
ENTITY_STOPLIST = load_entity_stoplist()

# ============================================================================
# PRECOMPILED REGEX PATTERNS (Performance Optimization)
# ============================================================================

# Precompile all regex patterns at module load time for performance
PRECOMPILED_PATTERNS = {}

def _precompile_patterns():
    """Precompile all regex patterns for performance optimization"""
    global PRECOMPILED_PATTERNS
    
    for category, subcategories in EXPANDED_ENTITIES.items():
        PRECOMPILED_PATTERNS[category] = {}
        for subcategory, config in subcategories.items():
            PRECOMPILED_PATTERNS[category][subcategory] = [
                re.compile(pattern, re.IGNORECASE) for pattern in config["patterns"]
            ]

# ============================================================================
# CLEANED EXPANDED ENTITIES DEFINITIONS
# ============================================================================

EXPANDED_ENTITIES = {
    # Timeframe Entities - Focused on specific time indicators
    "timeframe": {
        "short_term": {
            "patterns": [
                r"\b(immediate|urgent|quick|fast|soon|now|today|this week|this month|short term|short-term)\b",
                r"\b(within \d+ (days?|weeks?|months?))\b",
                r"\b(within the next \d+ (days?|weeks?|months?))\b",
                r"\b(asap|as soon as possible)\b"
            ],
            "examples": ["immediate action", "urgent decision", "quick response", "this week"]
        },
        "medium_term": {
            "patterns": [
                r"\b(medium term|medium-term|next quarter|next few months|coming months)\b",
                r"\b(within \d+ to \d+ months)\b",
                r"\b(quarterly|monthly)\b"
            ],
            "examples": ["medium term strategy", "next quarter", "coming months"]
        },
        "long_term": {
            "patterns": [
                r"\b(long term|long-term|long run|long run|future|years?|annual|yearly)\b",
                r"\b(over the next \d+ years?)\b",
                r"\b(strategic|sustainable|permanent)\b"
            ],
            "examples": ["long term planning", "strategic decision", "sustainable approach"]
        },
        "ambiguous": {
            "patterns": [
                r"\b(when|timing|schedule|deadline|timeline)\b",
                r"\b(appropriate time|right time|best time)\b"
            ],
            "examples": ["when to implement", "appropriate timing"]
        }
    },
    
    # Stakeholder Entities - Focused on specific stakeholder types
    "stakeholders": {
        "employees": {
            "patterns": [
                r"\b(employees?|staff|team|workers?|personnel|workforce|colleagues?)\b",
                r"\b(employee satisfaction|staff morale|team dynamics)\b",
                r"\b(company|business|organization)\b"
            ],
            "examples": ["employee concerns", "team alignment", "staff satisfaction"]
        },
        "career_individual": {
            "patterns": [
                r"\b(job offer|job offers|career choice|career decision|career path)\b",
                r"\b(professional growth|career development|job opportunity)\b",
                r"\b(salary|benefits|compensation|work-life balance)\b",
                r"\b(promotion|advancement|career transition|job change)\b",
                r"\b(employment|work|professional|career move)\b"
            ],
            "examples": ["job offer decision", "career choice", "professional growth"]
        },
        "customers": {
            "patterns": [
                r"\b(customers?|clients?|users?|consumers?|buyers?|end users?)\b",
                r"\b(customer satisfaction|customer experience|customer needs)\b",
                r"\b(market|audience|target market)\b"
            ],
            "examples": ["customer needs", "client satisfaction", "market response"]
        },
        "investors": {
            "patterns": [
                r"\b(investors?|shareholders?|stakeholders?|owners?|partners?)\b",
                r"\b(return on investment|roi|profit|revenue|earnings)\b",
                r"\b(financial|monetary|economic)\b",
                r"\b(invest|investment)\b"
            ],
            "examples": ["investor expectations", "shareholder value", "financial returns"]
        },
        "regulators": {
            "patterns": [
                r"\b(regulators?|regulatory|compliance|legal|government|authorities?)\b",
                r"\b(regulations?|laws?|policies?|standards?|requirements?)\b",
                r"\b(compliance|legal|regulatory)\b"
            ],
            "examples": ["regulatory compliance", "legal requirements", "government standards"]
        },
        "suppliers": {
            "patterns": [
                r"\b(suppliers?|vendors?|partners?|contractors?|providers?)\b",
                r"\b(supply chain|procurement|sourcing)\b",
                r"\b(external|third party|outsourced)\b"
            ],
            "examples": ["supplier relationships", "vendor management", "supply chain"]
        }
    },
    
    # Criteria Entities - Focused on specific evaluation criteria
    "criteria": {
        "financial": {
            "patterns": [
                r"\b(financial|monetary|cost|budget|revenue|profit|expense)\b",
                r"\b(roi|return|investment|capital|funding|money)\b",
                r"\b(economic|fiscal|financial performance)\b"
            ],
            "examples": ["financial impact", "cost analysis", "budget constraints"]
        },
        "strategic": {
            "patterns": [
                r"\b(strategic|strategy|positioning|competitive|market position)\b",
                r"\b(competitive advantage|market share|brand|reputation)\b",
                r"\b(long term|future|growth|expansion)\b"
            ],
            "examples": ["strategic positioning", "competitive advantage", "market share"]
        },
        "operational": {
            "patterns": [
                r"\b(operational|operations|efficiency|productivity|performance)\b",
                r"\b(process|workflow|procedure|system|infrastructure)\b",
                r"\b(quality|delivery|service|execution)\b"
            ],
            "examples": ["operational efficiency", "process improvement", "quality standards"]
        },
        "risk": {
            "patterns": [
                r"\b(risk|threat|danger|vulnerability|exposure|uncertainty)\b",
                r"\b(risk assessment|risk management|mitigation|prevention)\b",
                r"\b(safety|security|protection|safeguard)\b"
            ],
            "examples": ["risk assessment", "threat analysis", "safety concerns"]
        },
        "career": {
            "patterns": [
                r"\b(salary|compensation|benefits|pay|earnings|income)\b",
                r"\b(career growth|professional development|advancement|promotion)\b",
                r"\b(work-life balance|quality of life|personal satisfaction)\b",
                r"\b(company culture|work environment|team dynamics)\b",
                r"\b(job security|stability|long-term prospects)\b",
                r"\b(skills development|learning opportunities|training)\b"
            ],
            "examples": ["salary comparison", "career growth", "work-life balance"]
        }
    },
    
    # Uncertainty/Complexity Entities - Focused on specific uncertainty indicators
    "uncertainty": {
        "high": {
            "patterns": [
                r"\b(high uncertainty|unpredictable|volatile|unstable|chaotic)\b",
                r"\b(unknown|unclear|ambiguous|vague|indefinite)\b",
                r"\b(rapid change|dynamic|turbulent|unstable)\b"
            ],
            "examples": ["high uncertainty", "unpredictable market", "volatile conditions"]
        },
        "medium": {
            "patterns": [
                r"\b(medium uncertainty|moderate|somewhat|partially)\b",
                r"\b(mixed|varied|diverse|complex)\b",
                r"\b(evolving|changing|developing)\b"
            ],
            "examples": ["medium uncertainty", "moderate risk", "evolving situation"]
        },
        "low": {
            "patterns": [
                r"\b(low uncertainty|predictable|stable|certain|clear)\b",
                r"\b(known|established|proven|reliable)\b",
                r"\b(consistent|steady|stable|reliable)\b"
            ],
            "examples": ["low uncertainty", "predictable outcomes", "stable conditions"]
        }
    },
    
    "complexity": {
        "high": {
            "patterns": [
                r"\b(high complexity|complex|complicated|intricate|sophisticated)\b",
                r"\b(multiple factors|many variables|interconnected|interdependent)\b",
                r"\b(technical|advanced|specialized|expert)\b"
            ],
            "examples": ["high complexity", "complicated decision", "multiple factors"]
        },
        "medium": {
            "patterns": [
                r"\b(medium complexity|moderate|somewhat complex|manageable)\b",
                r"\b(several factors|multiple considerations|various aspects)\b",
                r"\b(standard|typical|common|usual)\b"
            ],
            "examples": ["medium complexity", "several factors", "standard approach"]
        },
        "low": {
            "patterns": [
                r"\b(low complexity|simple|straightforward|basic|elementary)\b",
                r"\b(few factors|limited variables|minimal|basic)\b",
                r"\b(clear|obvious|direct|straightforward)\b"
            ],
            "examples": ["low complexity", "simple decision", "straightforward choice"]
        }
    }
}

# ============================================================================
# ENTITY PATTERNS FOR EXTRACTION (CLEANED)
# ============================================================================

ENTITY_PATTERNS = {
    # Decision indicators - Focused on specific decision-making terms
    "decision_indicators": [
        r"\b(decide|decision|choose|choice|select|option|alternative)\b",
        r"\b(evaluate|assess|analyze|examine|consider|weigh)\b",
        r"\b(compare|contrast|balance|trade-off|tradeoff)\b",
        r"\b(should|must|need to|have to|ought to)\b",
        r"\b(best|optimal|ideal|preferred|recommended)\b"
    ],
    
    # Context classifiers - Focused on specific context indicators
    "context_classifiers": [
        r"\b(business|corporate|organizational|company|firm)\b",
        r"\b(project|initiative|program|campaign|effort)\b",
        r"\b(problem|issue|challenge|opportunity|situation)\b",
        r"\b(goal|objective|target|aim|purpose)\b"
    ],
    
    # Action indicators - Focused on specific action terms
    "action_indicators": [
        r"\b(implement|execute|carry out|perform|conduct)\b",
        r"\b(develop|create|build|establish|set up)\b",
        r"\b(manage|handle|deal with|address|tackle)\b",
        r"\b(improve|enhance|optimize|maximize|minimize)\b"
    ]
}

# ============================================================================
# DECISION INDICATORS (CLEANED)
# ============================================================================

DECISION_INDICATORS = {
    "urgency": [
        "urgent", "immediate", "asap", "quick", "fast", "soon", "now",
        "critical", "pressing", "time-sensitive", "deadline"
    ],
    "importance": [
        "important", "critical", "essential", "vital", "crucial", "key",
        "significant", "major", "strategic", "high-priority"
    ],
    "scope": [
        "large", "small", "major", "minor", "comprehensive", "limited",
        "extensive", "narrow", "broad", "focused"
    ],
    "impact": [
        "high impact", "low impact", "significant", "minimal", "substantial",
        "negligible", "major", "minor", "extensive", "limited"
    ]
}

# ============================================================================
# CONTEXT CLASSIFIERS (CLEANED)
# ============================================================================

CONTEXT_CLASSIFIERS = {
    "business_context": [
        "business", "corporate", "organizational", "commercial", "enterprise",
        "company", "firm", "organization", "institution"
    ],
    "project_context": [
        "project", "initiative", "program", "campaign", "effort", "undertaking",
        "endeavor", "venture", "operation"
    ],
    "problem_context": [
        "problem", "issue", "challenge", "difficulty", "obstacle", "barrier",
        "hurdle", "complication", "trouble"
    ],
    "opportunity_context": [
        "opportunity", "chance", "possibility", "potential", "prospect",
        "advantage", "benefit", "upside", "positive"
    ]
}

# ============================================================================
# STOPLIST FILTERING FUNCTIONS
# ============================================================================

def is_stoplisted_term(term: str) -> bool:
    """Check if a term is in the stoplist"""
    return term.lower() in ENTITY_STOPLIST

def filter_stoplisted_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out stoplisted entities from the extracted entities"""
    filtered_entities = {
        "timeframe": {},
        "stakeholders": {},
        "criteria": {},
        "uncertainty": {},
        "complexity": {},
        "confidence": 0.0,
        "entity_neutral": False
    }
    
    for category, subcategories in entities.items():
        if category in ["confidence", "entity_neutral"]:
            filtered_entities[category] = entities[category]
            continue
            
        for subcategory, config in subcategories.items():
            # Check if the subcategory name is stoplisted
            if is_stoplisted_term(subcategory):
                continue
                
            # Check if examples contain stoplisted terms
            if "examples" in config:
                filtered_examples = []
                for example in config["examples"]:
                    example_words = re.findall(r'\b\w+\b', example.lower())
                    if not any(is_stoplisted_term(word) for word in example_words):
                        filtered_examples.append(example)
                
                if filtered_examples:  # Only keep if we have non-stoplisted examples
                    filtered_entities[category][subcategory] = {
                        "confidence": config["confidence"],
                        "examples": filtered_examples
                    }
            else:
                # Keep if no examples to filter
                filtered_entities[category][subcategory] = config
    
    return filtered_entities

# ============================================================================
# ENTITY EXTRACTION FUNCTIONS (UPDATED WITH STOPLIST)
# ============================================================================

@lru_cache(maxsize=200)  # Increased cache size for Phase 4.2 optimization
def extract_expanded_entities(query: str) -> Dict[str, Any]:
    """
    Extract expanded entities from a decision-making query with stoplist filtering.

    Args:
        query: The input query string

    Returns:
        Dictionary containing extracted entities with confidence scores (filtered)
    """
    query_lower = query.lower()

    # Enhanced entity-neutral detection for Phase 4.2
    entity_neutral_indicators = [
        "what is", "how do i", "what are", "how to", "what tools", "what methods",
        "what techniques", "what frameworks", "what approach", "what is the best",
        "how do you", "what should", "what would", "what could", "explain", "describe",
        "tell me about", "what does", "how does", "why does", "when does", "where does",
        "can you", "could you", "would you", "please", "help me", "guide me",
        "show me", "give me", "provide", "suggest", "recommend", "advise"
    ]
    
    # Quick check for entity-neutral queries to save processing time
    # BUT: Allow career-related queries even if they contain neutral indicators
    if any(indicator in query_lower for indicator in entity_neutral_indicators) and not any(word in query_lower for word in [
        "job offer", "job offers", "career", "choose", "select", "decision"
    ]):
        return {
            "timeframe": {}, "stakeholders": {}, "criteria": {},
            "uncertainty": {}, "complexity": {}, "confidence": 0.0,
            "entity_neutral": True
        }

    # Lazy loading: Only process entities if query has sufficient complexity
    # BUT: Allow job offer and career-related queries even if short
    if len(query.split()) < 5 and not any(word in query_lower for word in [
        "job offer", "job offers", "career", "choose", "select", "decision"
    ]):
        return {
            "timeframe": {}, "stakeholders": {}, "criteria": {},
            "uncertainty": {}, "complexity": {}, "confidence": 0.0,
            "entity_neutral": True
        }

    extracted_entities = {
        "timeframe": {},
        "stakeholders": {},
        "criteria": {},
        "uncertainty": {},
        "complexity": {},
        "confidence": 0.0,
        "entity_neutral": False
    }
    
    # Extract timeframe entities
    for timeframe_type, timeframe_data in EXPANDED_ENTITIES["timeframe"].items():
        confidence = calculate_entity_confidence(query_lower, timeframe_data["patterns"])
        if confidence > 0.0:
            extracted_entities["timeframe"][timeframe_type] = {
                "confidence": confidence,
                "examples": timeframe_data["examples"]
            }
    
    # Extract stakeholder entities
    for stakeholder_type, stakeholder_data in EXPANDED_ENTITIES["stakeholders"].items():
        confidence = calculate_entity_confidence(query_lower, stakeholder_data["patterns"])
        if confidence > 0.0:
            extracted_entities["stakeholders"][stakeholder_type] = {
                "confidence": confidence,
                "examples": stakeholder_data["examples"]
            }
            print(f"[DEBUG] Found stakeholder: {stakeholder_type} with confidence {confidence}")
    
    # Extract criteria entities
    for criteria_type, criteria_data in EXPANDED_ENTITIES["criteria"].items():
        confidence = calculate_entity_confidence(query_lower, criteria_data["patterns"])
        if confidence > 0.0:
            extracted_entities["criteria"][criteria_type] = {
                "confidence": confidence,
                "examples": criteria_data["examples"]
            }
            print(f"[DEBUG] Found criteria: {criteria_type} with confidence {confidence}")
    
    # Extract uncertainty entities
    for uncertainty_type, uncertainty_data in EXPANDED_ENTITIES["uncertainty"].items():
        confidence = calculate_entity_confidence(query_lower, uncertainty_data["patterns"])
        if confidence > 0.0:
            extracted_entities["uncertainty"][uncertainty_type] = {
                "confidence": confidence,
                "examples": uncertainty_data["examples"]
            }
    
    # Extract complexity entities
    for complexity_type, complexity_data in EXPANDED_ENTITIES["complexity"].items():
        confidence = calculate_entity_confidence(query_lower, complexity_data["patterns"])
        if confidence > 0.0:
            extracted_entities["complexity"][complexity_type] = {
                "confidence": confidence,
                "examples": complexity_data["examples"]
            }
    
    # Apply stoplist filtering
    filtered_entities = filter_stoplisted_entities(extracted_entities)
    
    # Calculate overall confidence
    total_entities = sum(len(entities) for entities in filtered_entities.values() if isinstance(entities, dict))
    if total_entities > 0:
        total_confidence = sum(
            entity["confidence"] 
            for entities in filtered_entities.values() 
            if isinstance(entities, dict)
            for entity in entities.values()
        )
        filtered_entities["confidence"] = total_confidence / total_entities
    
    return filtered_entities

def calculate_entity_confidence(query: str, patterns: List[str]) -> float:
    """
    Calculate confidence score for entity extraction based on pattern matches.
    
    Args:
        query: The query string to analyze
        patterns: List of regex patterns to match
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    if not patterns:
        return 0.0
    
    matches = 0
    total_patterns = len(patterns)
    
    # Use precompiled patterns if available, otherwise compile on-the-fly
    compiled_patterns = []
    for pattern in patterns:
        try:
            compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
        except re.error:
            # Fallback to string pattern if compilation fails
            compiled_patterns.append(pattern)
    
    for pattern in compiled_patterns:
        if isinstance(pattern, re.Pattern):
            if pattern.search(query):
                matches += 1
        else:
            # Fallback to string pattern
            if re.search(pattern, query, re.IGNORECASE):
                matches += 1
    
    # Calculate confidence as ratio of matched patterns
    confidence = matches / total_patterns if total_patterns > 0 else 0.0
    
    # Boost confidence for multiple matches
    if matches > 1:
        confidence = min(1.0, confidence * 1.2)
    
    return confidence

def get_entity_summary(entities: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of extracted entities.
    
    Args:
        entities: Dictionary of extracted entities
        
    Returns:
        String summary of entities
    """
    summary_parts = []
    
    # Add timeframe
    if entities.get("timeframe"):
        timeframe = max(entities["timeframe"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"timeframe: {timeframe[0]}")
    
    # Add stakeholders
    if entities.get("stakeholders"):
        stakeholders = [k for k, v in entities["stakeholders"].items() if v["confidence"] > 0.1]
        if stakeholders:
            summary_parts.append(f"stakeholders: {', '.join(stakeholders)}")
    
    # Add criteria
    if entities.get("criteria"):
        criteria = [k for k, v in entities["criteria"].items() if v["confidence"] > 0.1]
        if criteria:
            summary_parts.append(f"criteria: {', '.join(criteria)}")
    
    # Add uncertainty
    if entities.get("uncertainty"):
        uncertainty = max(entities["uncertainty"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"uncertainty: {uncertainty[0]}")
    
    # Add complexity
    if entities.get("complexity"):
        complexity = max(entities["complexity"].items(), key=lambda x: x[1]["confidence"])
        summary_parts.append(f"complexity: {complexity[0]}")
    
    # Return partial summary if any entities found, otherwise "general decision"
    if summary_parts:
        return "; ".join(summary_parts)
    else:
        return "general decision"

def validate_entity_extraction(query: str) -> Dict[str, Any]:
    """
    Validate entity extraction and provide debugging information.
    
    Args:
        query: The query to validate
        
    Returns:
        Dictionary with validation results
    """
    entities = extract_expanded_entities(query)
    
    validation_result = {
        "query": query,
        "entities_found": sum(len(entities.get(key, {})) for key in ["timeframe", "stakeholders", "criteria", "uncertainty", "complexity"]),
        "confidence": entities.get("confidence", 0.0),
        "entity_summary": get_entity_summary(entities),
        "detailed_entities": entities,
        "is_valid": entities.get("confidence", 0.0) > 0.1
    }
    
    return validation_result

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_entity_extraction():
    """Test entity extraction with sample queries"""
    test_queries = [
        "How do we handle short-term employee concerns with high uncertainty?",
        "What financial criteria matter for long-term investor satisfaction?",
        "How do we manage operational complexity for immediate customer needs?",
        "What strategic risks do regulators see in our approach?"
    ]
    
    print("🧪 Testing Clean Entity Extraction")
    print("=" * 50)
    
    for query in test_queries:
        result = validate_entity_extraction(query)
        print(f"\nQuery: {query}")
        print(f"Entities Found: {result['entities_found']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Summary: {result['entity_summary']}")
        print(f"Valid: {result['is_valid']}")

# Initialize precompiled patterns at module load time
_precompile_patterns()

if __name__ == "__main__":
    test_entity_extraction() 