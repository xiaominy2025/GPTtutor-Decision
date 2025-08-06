# Course Development Guide - V1.6.5.1

## 🎯 Overview

This guide provides comprehensive instructions for developing and maintaining ThinkPal Decision Coach courses, with specific focus on the V1.6.5.1 production-ready implementation.

## 📋 Core Components

### 1. Query Engine Architecture
- **File**: `query_engine.py`
- **Purpose**: Main processing engine for decision-making queries
- **Features**: Entity enrichment, concept extraction, answer generation

### 2. Entity Management
- **File**: `clean_entities_static.py`
- **Purpose**: Static entity extraction using curated entities
- **Features**: No runtime filtering, pre-approved entities only

### 3. Course Configuration
- **Directory**: `courses/`
- **Files**: `course_config.json`, `glossary.json`, `prompts.json`
- **Purpose**: Course-specific settings and content

## 🔧 Clean Entities Workflow

### Overview
The Clean Entities Workflow ensures high-quality entity enrichment by using a static, curated list of entities rather than runtime filtering.

### Implementation Details

#### 1. Static Entity File
- **File**: `clean_entities.json`
- **Content**: 239 curated entities with relevance scores
- **Format**: JSON array of entity objects
- **Categories**: Timeframe, Stakeholders, Criteria, Uncertainty, Complexity

#### 2. Entity Relevance Threshold
- **Threshold**: 0.7 (70% confidence required)
- **Purpose**: Ensure only high-quality entities are used
- **Fallback**: Domain + application field concepts when threshold not met

#### 3. Fallback Logic
Use domain + application field concepts when:
- No strong entities found (confidence < 0.7)
- Query is entity-neutral (general questions)
- Entity extraction fails

#### 4. Quality Enforcement
- **No Padding**: Output never pads with generic filler
- **Quality Focus**: Prefer quality content over entity quantity
- **Graceful Degradation**: Always provide meaningful content

### Usage Example
```python
from clean_entities_static import extract_expanded_entities

# Extract entities with relevance threshold
entities = extract_expanded_entities("How do we handle short-term employee concerns?")
if entities['confidence'] >= 0.7:
    # Use entities for enrichment
    pass
else:
    # Use domain + application field concepts
    pass
```

## 📝 Answer Structure Requirements

### Strategic Thinking Lens
- **Word Count**: 100-140 words
- **Format**: 2 well-developed paragraphs
- **Content**: Strategic analysis, trade-offs, domain insights
- **Quality**: No artificial padding, prefer quality over length

### Story in Action
- **Word Count**: 60-80 words
- **Format**: 3-4 sentence concrete example
- **Content**: Sequential flow with specific details
- **Alignment**: Must mirror Strategic Thinking Lens concepts

### Follow-up Prompts
- **Count**: 2-4 reflective questions
- **Purpose**: Invite deeper thinking
- **Content**: No repetition of previous sections

### Concepts/Tools
- **Count**: 2-4 unique concepts (max 5)
- **Format**: "Concept Name: Definition"
- **Prioritization**: Domain concepts first, then application field
- **Deduplication**: Enforced to prevent repetition

## 🧪 Testing Requirements

### Entity Extraction Testing
- **Queries**: 12 representative queries across domains
- **Domains**: Strategic, Operational, Financial, Risk, Neutral
- **Validation**: Average confidence > 0.7 when entities present
- **Output**: entities_found, confidence, entity_summary, is_valid

### Quality Validation
- **Word Count**: Strategic Lens 100-140 words
- **Concepts**: 2-4 unique concepts, max 5 total
- **Deduplication**: No repeated concepts
- **Relevance**: Concepts match query domain

## 🚀 Production Deployment

### V1.6.5.1 Requirements
1. **Static Entities**: Use clean_entities.json only
2. **Relevance Threshold**: 0.7 minimum confidence
3. **Fallback Logic**: Domain + application field concepts
4. **Word Count**: Strategic Lens 100-140 words
5. **Concepts/Tools**: Capped at 4-5 total

### Validation Checklist
- [ ] clean_entities.json exists with 239 entities
- [ ] query_engine.py imports from clean_entities_static.py
- [ ] No references to runtime stoplist filtering
- [ ] Entity relevance threshold = 0.7 enforced
- [ ] Graceful fallback to domain + application fields
- [ ] Strategic Thinking Lens 100-140 words
- [ ] Concepts/Tools capped at 4-5 total
- [ ] Deduplication enforced
- [ ] Test suite passes with 12 representative queries

## 📚 File Structure

```
GPTTutor-Decision/
├── query_engine.py              # Main processing engine
├── clean_entities_static.py     # Static entity extraction
├── clean_entities.json          # Curated entity list
├── courses/                     # Course configurations
│   ├── decision/
│   │   ├── course_config.json
│   │   ├── glossary.json
│   │   └── prompts.json
│   └── marketing/
│       ├── glossary.json
│       └── prompts.json
└── tests/                       # Test suites
    ├── validate_phase1.py
    └── concept_extraction/
```

## 🔄 Maintenance

### Adding New Entities
1. Edit `clean_entities.json`
2. Add entity with relevance score
3. Test with `test_entity_extraction()`
4. Validate confidence > 0.7

### Updating Course Content
1. Modify course configuration files
2. Update glossary.json for new concepts
3. Test concept extraction
4. Validate answer quality

### Quality Assurance
1. Run comprehensive test suite
2. Validate word counts
3. Check concept relevance
4. Ensure no generic filler

## ✅ Success Criteria

### V1.6.5.1 Production Ready
- [ ] All loose ends from B1651 Implementation Summary closed
- [ ] Clean entities integration complete
- [ ] Entity enrichment validation passed
- [ ] Word count enforcement working
- [ ] Answer structure consistent
- [ ] Concepts/Tools section optimized
- [ ] Testing expanded to 12 queries
- [ ] Documentation updated
- [ ] Final confirmation: "✅ V1.6.5.1 production-ready" 