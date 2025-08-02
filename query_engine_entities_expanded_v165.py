#!/usr/bin/env python3
"""
V1.6.6 Comprehensive Expanded Entities
Merged V1.6.5 extraction mechanics + V1.6.6 course-specific expansions
"""

EXPANDED_ENTITIES = {
    "career_change": {
        "type": "decision_context",
        "domain": "personal",
        "keywords": [
            "job",
            "career",
            "position",
            "role",
            "employment",
            "work",
            "profession"
        ],
        "related_concepts": [
            "risk assessment",
            "cost-benefit analysis",
            "stakeholder alignment"
        ]
    },
    "investment_decision": {
        "type": "decision_context",
        "domain": "financial",
        "keywords": [
            "investment",
            "stock",
            "bond",
            "portfolio",
            "return",
            "profit",
            "loss",
            "market"
        ],
        "related_concepts": [
            "expected value analysis",
            "risk tolerance assessment",
            "monte carlo simulation"
        ]
    },
    "business_strategy": {
        "type": "decision_context",
        "domain": "strategic",
        "keywords": [
            "strategy",
            "business",
            "company",
            "organization",
            "competitive",
            "market"
        ],
        "related_concepts": [
            "porter\u2019s five forces",
            "competitive advantage",
            "value chain analysis"
        ]
    },
    "negotiation": {
        "type": "decision_context",
        "domain": "negotiation",
        "keywords": [
            "negotiate",
            "deal",
            "agreement",
            "contract",
            "terms",
            "bargain"
        ],
        "related_concepts": [
            "batna",
            "zopa",
            "integrative negotiation",
            "distributive negotiation"
        ]
    },
    "risk_management": {
        "type": "decision_context",
        "domain": "technical",
        "keywords": [
            "risk",
            "threat",
            "uncertainty",
            "exposure",
            "mitigation",
            "control"
        ],
        "related_concepts": [
            "risk assessment",
            "scenario analysis",
            "adaptive strategies"
        ]
    },
    "forecasting_decision": {
        "type": "decision_context",
        "domain": "technical",
        "keywords": [
            "forecast",
            "regression",
            "moving average",
            "seasonal",
            "qualitative"
        ],
        "related_concepts": [
            "regression forecasting",
            "seasonal forecasting",
            "qualitative forecasting"
        ]
    },
    "optimization_decision": {
        "type": "decision_context",
        "domain": "technical",
        "keywords": [
            "optimization",
            "linear programming",
            "integer optimization",
            "aggregate planning"
        ],
        "related_concepts": [
            "linear programming",
            "integer optimization",
            "analytical solver"
        ]
    },
    "simulation_decision": {
        "type": "decision_context",
        "domain": "technical",
        "keywords": [
            "simulation",
            "monte carlo",
            "scenario analysis"
        ],
        "related_concepts": [
            "monte carlo simulation",
            "scenario analysis",
            "integrated optimization & simulation"
        ]
    },
    "bias_awareness": {
        "type": "decision_context",
        "domain": "behavioral",
        "keywords": [
            "bias",
            "anchoring",
            "framing",
            "heuristic",
            "fallacy"
        ],
        "related_concepts": [
            "confirmation bias",
            "anchoring bias",
            "framing bias",
            "escalation of commitment"
        ]
    },
    "stakeholders": {
        "employees": {
            "type": "stakeholder",
            "impact": "direct",
            "interests": [
                "job security",
                "compensation",
                "work environment",
                "career growth"
            ]
        },
        "customers": {
            "type": "stakeholder",
            "impact": "direct",
            "interests": [
                "product quality",
                "service",
                "price",
                "experience"
            ]
        },
        "investors": {
            "type": "stakeholder",
            "impact": "direct",
            "interests": [
                "returns",
                "growth",
                "risk",
                "value"
            ]
        },
        "suppliers": {
            "type": "stakeholder",
            "impact": "indirect",
            "interests": [
                "contracts",
                "relationships",
                "payment terms"
            ]
        },
        "regulators": {
            "type": "stakeholder",
            "impact": "external",
            "interests": [
                "compliance",
                "standards",
                "public interest"
            ]
        },
        "managers": {
            "type": "stakeholder",
            "impact": "direct",
            "interests": [
                "efficiency",
                "growth",
                "compliance",
                "team performance"
            ]
        },
        "negotiation_partners": {
            "type": "stakeholder",
            "impact": "external",
            "interests": [
                "deal value",
                "fairness",
                "long-term trust"
            ]
        }
    },
    "criteria": {
        "financial": {
            "type": "criteria",
            "metrics": [
                "cost",
                "revenue",
                "profit",
                "roi",
                "npv",
                "irr"
            ],
            "tools": [
                "cost-benefit analysis",
                "profitability analysis",
                "expected value analysis"
            ]
        },
        "strategic": {
            "type": "criteria",
            "metrics": [
                "alignment",
                "competitive advantage",
                "market position",
                "growth"
            ],
            "tools": [
                "porter\u2019s five forces",
                "competitive advantage",
                "value chain analysis"
            ]
        },
        "operational": {
            "type": "criteria",
            "metrics": [
                "efficiency",
                "productivity",
                "quality",
                "delivery"
            ],
            "tools": [
                "linear programming",
                "aggregate planning",
                "process analysis"
            ]
        },
        "risk": {
            "type": "criteria",
            "metrics": [
                "probability",
                "impact",
                "exposure",
                "mitigation"
            ],
            "tools": [
                "risk assessment",
                "scenario analysis",
                "monte carlo simulation"
            ]
        },
        "behavioral": {
            "type": "criteria",
            "metrics": [
                "bias",
                "judgment",
                "framing",
                "heuristics"
            ],
            "tools": [
                "bias recognition",
                "utility functions",
                "risk tolerance assessment"
            ]
        },
        "technological": {
            "type": "criteria",
            "metrics": [
                "analytics",
                "forecast",
                "simulation",
                "solver"
            ],
            "tools": [
                "decision support systems",
                "analytical solver",
                "human-machine collaboration"
            ]
        }
    },
    "timeframes": {
        "short_term": {
            "type": "timeframe",
            "duration": "0-1 year",
            "focus": "immediate implementation and results"
        },
        "medium_term": {
            "type": "timeframe",
            "duration": "1-3 years",
            "focus": "strategic execution and adaptation"
        },
        "long_term": {
            "type": "timeframe",
            "duration": "3+ years",
            "focus": "sustainable competitive advantage"
        }
    },
    "uncertainty": {
        "low": {
            "type": "uncertainty",
            "characteristics": [
                "predictable",
                "stable",
                "known parameters"
            ],
            "tools": [
                "deterministic analysis",
                "point estimates"
            ]
        },
        "medium": {
            "type": "uncertainty",
            "characteristics": [
                "variable",
                "some unknowns",
                "probabilistic"
            ],
            "tools": [
                "sensitivity analysis",
                "scenario planning",
                "expected value analysis"
            ]
        },
        "high": {
            "type": "uncertainty",
            "characteristics": [
                "unpredictable",
                "unknown unknowns",
                "complex"
            ],
            "tools": [
                "monte carlo simulation",
                "robust decision making",
                "adaptive strategies"
            ]
        }
    },
    "complexity": {
        "simple": {
            "type": "complexity",
            "characteristics": [
                "few options",
                "clear criteria",
                "single objective"
            ],
            "tools": [
                "decision tree",
                "cost-benefit analysis"
            ]
        },
        "moderate": {
            "type": "complexity",
            "characteristics": [
                "multiple options",
                "conflicting criteria",
                "trade-offs"
            ],
            "tools": [
                "multi-criteria analysis",
                "swot analysis",
                "scenario planning"
            ]
        },
        "complex": {
            "type": "complexity",
            "characteristics": [
                "many stakeholders",
                "high uncertainty",
                "systemic effects"
            ],
            "tools": [
                "systems thinking",
                "stakeholder analysis",
                "adaptive management"
            ]
        }
    }
}

ENTITY_PATTERNS = {
    "money": "\\$[\\d,]+(?:\\.\\d{2})?|\\d+(?:\\.\\d{2})?\\s*(?:dollars?|USD)",
    "percentage": "\\d+(?:\\.\\d+)?\\s*%",
    "date": "\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}|\\d{4}-\\d{2}-\\d{2}",
    "time": "\\d{1,2}:\\d{2}\\s*(?:AM|PM|am|pm)?",
    "organization": "\\b[A-Z][a-zA-Z\\s&]+(?:Inc|Corp|LLC|Ltd|Company|Organization)\\b",
    "person": "\\b[A-Z][a-z]+\\s+[A-Z][a-z]+\\b",
    "location": "\\b[A-Z][a-zA-Z\\s]+(?:City|State|Country|Province)\\b"
}

DECISION_INDICATORS = {
    "urgency": [
        "urgent",
        "immediate",
        "quick",
        "fast",
        "soon",
        "deadline"
    ],
    "importance": [
        "critical",
        "important",
        "significant",
        "major",
        "key",
        "essential"
    ],
    "uncertainty": [
        "uncertain",
        "unknown",
        "unclear",
        "ambiguous",
        "risky",
        "volatile"
    ],
    "complexity": [
        "complex",
        "complicated",
        "difficult",
        "challenging",
        "multifaceted"
    ],
    "stakeholders": [
        "stakeholders",
        "parties",
        "people",
        "team",
        "organization",
        "company"
    ],
    "alternatives": [
        "options",
        "alternatives",
        "choices",
        "possibilities",
        "scenarios"
    ]
}

CONTEXT_CLASSIFIERS = {
    "personal": [
        "I",
        "me",
        "my",
        "personal",
        "individual",
        "career",
        "life"
    ],
    "business": [
        "company",
        "organization",
        "business",
        "corporate",
        "enterprise"
    ],
    "financial": [
        "money",
        "cost",
        "investment",
        "budget",
        "financial",
        "economic"
    ],
    "strategic": [
        "strategy",
        "long-term",
        "competitive",
        "market",
        "positioning"
    ],
    "operational": [
        "process",
        "operation",
        "efficiency",
        "productivity",
        "delivery"
    ],
    "technical": [
        "technology",
        "system",
        "technical",
        "implementation",
        "solution"
    ]
}