# Multi-Course Implementation Plan

## 🚨 **URGENT: V1.6.5 Multi-Course Readiness**

The current system is **dangerously inconsistent** - it pretends to be multi-course but contains hardcoded decision course logic throughout. This creates the exact type of issues we just experienced with the glossary mismatch.

## 📋 **Phase 1: Immediate Course Configuration Extraction**

### **Step 1.1: Extract Current Decision Course Logic**

Create `courses/decision/course_config.json`:

```json
{
  "course_id": "decision",
  "name": "Decision Making",
  "version": "1.6.5",
  "domains": {
    "behavioral": {
      "keywords": [
        "team", "teams", "conflict", "conflicts", "value", "values", "behavior", "behaviour",
        "psychology", "psychological", "bias", "biases", "cognitive", "cognition",
        "judgment", "judgement", "leadership", "personality", "personalities",
        "motivation", "motivational", "emotion", "emotional", "human", "people",
        "individual", "group", "social", "interpersonal", "communication"
      ],
      "concepts": [
        "escalation of commitment", "prospect theory", "confirmation bias", 
        "anchoring bias", "framing bias", "representative heuristic", 
        "endowment effect", "status quo bias", "mental accounting"
      ]
    },
    "technical": {
      "keywords": [
        "model", "modeling", "simulation", "forecast", "optimization", "analysis",
        "data", "statistical", "mathematical", "algorithm", "uncertainty", 
        "probability", "calculate", "compute", "assess", "evaluate", "measure"
      ],
      "concepts": [
        "monte carlo simulation", "sensitivity analysis", "linear optimization",
        "expected value", "scenario analysis", "regression", "moving average"
      ]
    },
    "strategic": {
      "keywords": [
        "strategy", "strategic", "competitive", "advantage", "positioning",
        "market", "industry", "business", "organization", "planning"
      ],
      "concepts": [
        "porter's five forces", "cost leadership", "differentiation strategy",
        "portfolio management", "competitive advantage analysis"
      ]
    },
    "negotiation": {
      "keywords": [
        "negotiate", "negotiation", "bargain", "deal", "agreement", "contract",
        "discuss", "discussion", "meeting", "conference", "settlement"
      ],
      "concepts": [
        "batna", "reservation point", "zopa", "integrative negotiation",
        "game theory", "winner's curse"
      ]
    }
  },
  "application_fields": [
    "business_strategy", "project_management", "risk_management", 
    "financial_analysis", "operations_management", "human_resources",
    "change_management", "stakeholder_management", "performance_management"
  ],
  "entity_types": {
    "organizations": ["company names", "department names", "team names"],
    "projects": ["project names", "initiative names", "campaign names"],
    "decisions": ["decision points", "choice options", "alternatives"],
    "stakeholders": ["person names", "role names", "position titles"]
  },
  "answer_templates": {
    "strategic_lens": "In this scenario, addressing {context} involves understanding {primary_domain} principles. {domain_explanation} By leveraging {key_concepts}, you can {approach}. However, it's essential to {consideration}.",
    "story_in_action": "For instance, {character} faced a similar situation where {scenario}. By applying {concept}, they {action} which led to {outcome}.",
    "follow_up_prompts": [
      "How might you {action} based on {concept}?",
      "What {consideration} should you keep in mind when {situation}?",
      "How could you {approach} using {method}?"
    ]
  }
}
```

### **Step 1.2: Create Course Configuration Loader**

Create `course_config_loader.py`:

```python
#!/usr/bin/env python3
"""
Course Configuration Loader
"""
import json
import os
from typing import Dict, Any

def load_course_config(course_id: str) -> Dict[str, Any]:
    """Load complete course configuration"""
    course_path = os.path.join("courses", course_id)
    config_path = os.path.join(course_path, "course_config.json")
    
    if not os.path.exists(config_path):
        raise ValueError(f"Course configuration not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required fields
    required_fields = ["course_id", "name", "domains", "application_fields", "entity_types"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in course config")
    
    return config

def validate_course_config(config: Dict[str, Any]) -> bool:
    """Validate course configuration completeness"""
    # Add validation logic
    return True
```

## 📋 **Phase 2: Refactor Query Engine**

### **Step 2.1: Make Domain Detection Course-Agnostic**

Replace hardcoded `detect_course_concept_domains`:

```python
def detect_course_concept_domains(query: str, course_config: dict) -> dict:
    """
    Course-agnostic domain detection using course configuration
    """
    query_lower = query.lower()
    domains = {}
    
    # Initialize all domains from course config
    for domain_name in course_config['domains']:
        domains[domain_name] = 0
    
    # Score each domain based on keywords
    for domain_name, domain_config in course_config['domains'].items():
        score = 0
        for keyword in domain_config['keywords']:
            if keyword in query_lower:
                score += 1
        domains[domain_name] = score
    
    return domains
```

### **Step 2.2: Make Application Field Extraction Course-Agnostic**

```python
def extract_application_field(query: str, course_config: dict) -> str:
    """
    Course-agnostic application field extraction
    """
    query_lower = query.lower()
    application_fields = course_config['application_fields']
    
    # Simple keyword matching for now
    for field in application_fields:
        if field.replace('_', ' ') in query_lower:
            return field
    
    return application_fields[0]  # Default to first field
```

### **Step 2.3: Update process_query Function**

```python
def process_query(query: str, course_config: dict = None) -> str:
    """
    Main query processing function - now course-agnostic
    """
    if course_config is None:
        # Load default course config
        course_config = load_course_config("decision")
    
    # Use course-agnostic functions
    domains = detect_course_concept_domains(query, course_config)
    application_field = extract_application_field(query, course_config)
    
    # Rest of the function remains the same but uses course_config
    # ...
```

## 📋 **Phase 3: Update API Server**

### **Step 3.1: Enhance load_course_config Function**

```python
def load_course_config(course_id: str) -> dict:
    """
    Load complete course configuration including all components
    """
    try:
        # Load main course config
        config = load_course_config_from_file(course_id)
        
        # Load additional components
        config['glossary'] = load_course_glossary(course_id)
        config['prompt_template'] = load_course_prompt_template(course_id)
        config['sections_config'] = load_course_sections_config(course_id)
        
        return config
    except Exception as e:
        print(f"❌ Failed to load course config for '{course_id}': {e}")
        # Fall back to decision course
        return load_course_config("decision")
```

## 📋 **Phase 4: Testing & Validation**

### **Step 4.1: Create Course Configuration Test**

```python
def test_course_configuration():
    """Test that all course configurations are complete"""
    courses = ["decision", "marketing"]  # Add more as needed
    
    for course_id in courses:
        try:
            config = load_course_config(course_id)
            print(f"✅ Course '{course_id}' configuration loaded successfully")
            
            # Validate completeness
            validate_course_config(config)
            print(f"✅ Course '{course_id}' configuration validated")
            
        except Exception as e:
            print(f"❌ Course '{course_id}' configuration failed: {e}")
```

### **Step 4.2: Create Multi-Course Test**

```python
def test_multi_course_consistency():
    """Test that same query produces appropriate results for different courses"""
    test_query = "How should I approach this decision?"
    
    for course_id in ["decision", "marketing"]:
        config = load_course_config(course_id)
        domains = detect_course_concept_domains(test_query, config)
        print(f"Course '{course_id}' domains: {domains}")
```

## 🎯 **Implementation Priority**

### **HIGH PRIORITY (This Week)**
1. ✅ Extract decision course configuration (DONE - glossary alignment)
2. 🔄 Create course configuration schema
3. 🔄 Refactor domain detection to be course-agnostic
4. 🔄 Update API server to load complete course config

### **MEDIUM PRIORITY (Next Week)**
1. 🔄 Refactor application field extraction
2. 🔄 Refactor entity extraction
3. 🔄 Create course configuration validation
4. 🔄 Add comprehensive testing

### **LOW PRIORITY (Future)**
1. 🔄 Create additional course configurations (marketing, etc.)
2. 🔄 Add course-specific answer templates
3. 🔄 Create course migration tools

## 🚨 **Immediate Action Required**

1. **STOP** any new course development until this architecture is implemented
2. **IMPLEMENT** Phase 1 (Course Configuration Extraction) immediately
3. **TEST** thoroughly before adding any new courses
4. **DOCUMENT** all course-specific components

This will ensure V1.6.5 is truly multi-course ready and prevent the type of inconsistencies we just experienced. 