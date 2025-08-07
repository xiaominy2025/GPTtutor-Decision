# Multi-Course Architecture Analysis & Solution Plan

## 🚨 **CRITICAL ISSUE IDENTIFIED**

V1.6.5 is **NOT** truly multi-course ready. It's a **single-course system with a thin multi-course wrapper** that creates dangerous inconsistencies.

## 🔍 **Current Architecture Problems**

### **1. Hardcoded Course-Specific Logic**
The `query_engine.py` contains **hardcoded decision course logic**:

```python
# HARDCODED DOMAINS (Decision Course Only)
course_concept_domains = {
    'behavioral': 0,      # Decision course specific
    'technical': 0,       # Decision course specific  
    'strategic': 0,       # Decision course specific
    'negotiation': 0      # Decision course specific
}

# HARDCODED KEYWORDS (Decision Course Only)
behavioral_keywords = [
    'team', 'conflict', 'psychology', 'bias', 'leadership'  # Decision-specific
]
technical_keywords = [
    'model', 'simulation', 'optimization', 'analysis'  # Decision-specific
]
```

### **2. Incomplete Course Configuration**
The `course_config` parameter only handles:
- ✅ `glossary` (concepts)
- ❌ **Missing**: Domain definitions
- ❌ **Missing**: Keyword mappings  
- ❌ **Missing**: Application fields
- ❌ **Missing**: Entity extraction rules
- ❌ **Missing**: Answer generation templates

### **3. Black Box Problem**
You're right - the system is a **black box** because:
- Domain detection logic is hardcoded in `query_engine.py`
- Application field extraction is hardcoded
- Entity extraction rules are hardcoded
- Answer generation templates are hardcoded
- **No course-specific customization possible**

## 📊 **Systematic Analysis**

### **Current Course-Specific Components (All Hardcoded):**

1. **Domain Detection** (`detect_course_concept_domains`)
   - Hardcoded domains: `behavioral`, `technical`, `strategic`, `negotiation`
   - Hardcoded keywords for each domain
   - **Problem**: Marketing course would need different domains/keywords

2. **Application Field Extraction** (`extract_application_field`)
   - Hardcoded application fields list
   - **Problem**: Marketing course has different application fields

3. **Entity Extraction** (`extract_enhanced_entities`)
   - Hardcoded entity types and extraction rules
   - **Problem**: Marketing course needs different entity types

4. **Answer Generation Templates**
   - Hardcoded section templates
   - **Problem**: Marketing course might need different answer structure

5. **Concept Selection Logic**
   - Hardcoded concept ranking and selection
   - **Problem**: Marketing course has different concept priorities

## 🎯 **Solution: True Multi-Course Architecture**

### **Phase 1: Course Configuration Schema**

Create comprehensive course configuration files:

```json
// courses/marketing/course_config.json
{
  "course_id": "marketing",
  "name": "Marketing Strategy",
  "domains": {
    "consumer_behavior": {
      "keywords": ["customer", "consumer", "buyer", "purchase", "brand"],
      "concepts": ["consumer psychology", "brand loyalty", "purchase decision"]
    },
    "market_analysis": {
      "keywords": ["market", "competition", "industry", "segment"],
      "concepts": ["market research", "competitive analysis", "segmentation"]
    },
    "campaign_strategy": {
      "keywords": ["campaign", "advertising", "promotion", "message"],
      "concepts": ["campaign planning", "advertising strategy", "message design"]
    }
  },
  "application_fields": [
    "digital_marketing", "traditional_marketing", "b2b_marketing", 
    "b2c_marketing", "social_media", "content_marketing"
  ],
  "entity_types": {
    "brands": ["brand names", "company names"],
    "campaigns": ["campaign names", "advertising campaigns"],
    "channels": ["marketing channels", "distribution channels"]
  },
  "answer_templates": {
    "strategic_lens": "Marketing-focused strategic thinking...",
    "story_in_action": "Marketing scenario with customer focus...",
    "follow_up_prompts": "Marketing-specific reflection questions..."
  }
}
```

### **Phase 2: Modular Query Engine**

Refactor `query_engine.py` to be course-agnostic:

```python
def detect_course_concept_domains(query: str, course_config: dict) -> dict:
    """Course-agnostic domain detection"""
    domains = {}
    for domain_name, domain_config in course_config['domains'].items():
        score = 0
        for keyword in domain_config['keywords']:
            if keyword in query.lower():
                score += 1
        domains[domain_name] = score
    return domains

def extract_application_field(query: str, course_config: dict) -> str:
    """Course-agnostic application field extraction"""
    # Use course_config['application_fields'] instead of hardcoded list
    pass

def extract_enhanced_entities(query: str, course_config: dict) -> dict:
    """Course-agnostic entity extraction"""
    # Use course_config['entity_types'] instead of hardcoded rules
    pass
```

### **Phase 3: Course-Specific Answer Generation**

```python
def generate_course_specific_answer(query: str, course_config: dict) -> str:
    """Use course-specific templates and logic"""
    templates = course_config['answer_templates']
    # Generate answer using course-specific templates
    pass
```

## 📋 **Implementation Plan**

### **Step 1: Create Course Configuration Schema**
- [ ] Define comprehensive course configuration JSON schema
- [ ] Create example configurations for `decision` and `marketing` courses
- [ ] Document all course-specific components

### **Step 2: Refactor Query Engine**
- [ ] Make `detect_course_concept_domains` course-agnostic
- [ ] Make `extract_application_field` course-agnostic  
- [ ] Make `extract_enhanced_entities` course-agnostic
- [ ] Make answer generation course-agnostic

### **Step 3: Update API Server**
- [ ] Enhance `load_course_config()` to load all course components
- [ ] Pass complete course configuration to query engine
- [ ] Add validation for course configuration completeness

### **Step 4: Create Course Migration Tools**
- [ ] Extract current decision course logic into configuration
- [ ] Create tools to validate course configuration completeness
- [ ] Create course configuration testing framework

### **Step 5: Testing & Validation**
- [ ] Test with multiple course configurations
- [ ] Validate that all course-specific logic is externalized
- [ ] Ensure no hardcoded course logic remains

## 🎯 **Benefits of True Multi-Course Architecture**

1. **Consistency**: All courses use same engine with different configs
2. **Maintainability**: Course logic is externalized and version-controlled
3. **Scalability**: Easy to add new courses without code changes
4. **Reliability**: No more black box - all logic is explicit
5. **Flexibility**: Each course can have completely different domains, fields, entities

## 🚨 **Immediate Action Required**

The current system is **dangerous** because:
- It pretends to be multi-course but isn't
- Course-specific logic is scattered and hardcoded
- Adding new courses requires code changes
- No systematic way to ensure course completeness

**Recommendation**: Pause any new course development until this architecture is properly implemented. 