# Course Config Rebuild Analysis for V1.7

## 🎯 **Source of Truth: query_engine.py**

The `query_engine.py` is the **fine-tuned, stable version** that delivers **satisfying query processing performance**. Therefore, `course_config.json` should be rebuilt to match the query engine exactly.

## 📊 **Domain Comparison**

### ✅ **Domain Structure: PERFECT MATCH**
Both files use identical domain names:
- `behavioral`
- `technical` 
- `strategic`
- `negotiation`

## 🔍 **Keyword Analysis - What Needs Updating**

### **1. Behavioral Domain**

**Current course_config.json keywords (50+):**
```json
"behavioral": {
  "keywords": [
    "team", "teams", "conflict", "conflicts", "value", "values", "behavior", "behaviour",
    "psychology", "psychological", "bias", "biases", "cognitive", "cognition",
    "judgment", "judgement", "leadership", "personality", "personalities",
    "motivation", "motivational", "emotion", "emotional", "human", "people",
    "individual", "group", "social", "interpersonal", "communication",
    "behave", "behaving", "behaved", "psychologic", "cognitively", "judge", "judging",
    "lead", "leading", "led", "motivate", "motivating", "motivated", "feel", "feeling",
    "felt", "interact", "interacting", "interacted", "communicate", "communicating",
    "reluctant", "reluctance", "convince", "convincing", "persuade", "persuasion",
    "legacy", "legacy project", "give up", "giving up", "think differently"
  ]
}
```

**query_engine.py keywords (80+):**
```python
behavioral_keywords = [
    'team', 'teams', 'conflict', 'conflicts', 'value', 'values', 'behavior', 'behaviour',
    'psychology', 'psychological', 'bias', 'biases', 'cognitive', 'cognition',
    'judgment', 'judgement', 'leadership', 'personality', 'personalities',
    'motivation', 'motivational', 'emotion', 'emotional', 'human', 'people',
    'individual', 'group', 'social', 'interpersonal', 'communication',
    'behave', 'behaving', 'behaved', 'psychologic', 'cognitively', 'judge', 'judging',
    'lead', 'leading', 'led', 'motivate', 'motivating', 'motivated', 'feel', 'feeling',
    'felt', 'interact', 'interacting', 'interacted', 'communicate', 'communicating',
    # Manager and workplace relationship keywords
    'manager', 'managers', 'boss', 'supervisor', 'supervisors', 'colleague', 'colleagues',
    'workplace', 'office', 'professional', 'professionally', 'work', 'working',
    'critique', 'critiques', 'criticism', 'criticisms', 'feedback', 'unfair', 'fair',
    'approach', 'approaching', 'situation', 'circumstance', 'circumstances',
    'relationship', 'relationships', 'interpersonal', 'communication', 'communicate',
    'response', 'respond', 'responding', 'react', 'reacting', 'reaction', 'reactions',
    # Money and financial behavior keywords
    'budget', 'budgeting', 'budgeted', 'salary', 'salaries', 'expense', 'expenses', 'spending', 'spend', 'spent',
    'money', 'financial', 'finance', 'cost', 'costs', 'price', 'prices', 'payment', 'payments',
    'income', 'revenue', 'profit', 'loss', 'saving', 'savings', 'save', 'saved',
    'investment', 'invest', 'investing', 'invested', 'wealth', 'wealthy', 'asset', 'assets',
    'debt', 'credit', 'loan', 'loans', 'mortgage', 'rent', 'rental', 'utility', 'utilities',
    'grocery', 'groceries', 'entertainment', 'transportation', 'healthcare', 'insurance'
]
```

**Missing in course_config.json:**
- Workplace relationship keywords (manager, boss, supervisor, colleague, workplace, office, etc.)
- Financial behavior keywords (budget, salary, expense, money, financial, etc.)
- Professional interaction keywords (critique, feedback, unfair, fair, etc.)

### **2. Technical Domain**

**Current course_config.json keywords (40+):**
```json
"technical": {
  "keywords": [
    "model", "modeling", "modeled", "simulation", "simulate", "simulating", "simulated",
    "forecast", "forecasting", "forecasted", "optimization", "optimize", "optimizing", 
    "optimized", "optimum", "optimization strategy", "optimization strategies",
    "maximization", "maximize", "maximizing", "maximized", "maximum", "minimization", 
    "minimize", "minimizing", "minimized", "minimum", "simulation strategy", "simulation strategies",
    "analysis", "analyze", "analyzing", "analyzed", "analytical",
    "data", "statistical", "statistics", "mathematical", "mathematics",
    "algorithm", "algorithms", "uncertainty", "uncertain", "uncertainties", "probability", 
    "probabilistic", "probable", "calculate", "calculation", "calculating", "calculated",
    "compute", "computation", "computing", "computed", "numerical", "numeric",
    "assess", "assessment", "assessing", "assessed", "evaluate", "evaluation", 
    "evaluating", "evaluated", "measure", "measurement", "measuring", "measured",
    "determine", "determining", "determined", "estimate", "estimating", "estimated",
    "predict", "predicting", "predicted", "prediction", "predictions"
  ]
}
```

**query_engine.py keywords (50+):**
```python
technical_keywords = [
    'simulation', 'simulate', 'simulating', 'simulated',
    'forecast', 'forecasting', 'forecasted', 
    'optimization', 'optimize', 'optimizing', 'optimized',
    'maximization', 'maximize', 'maximizing', 'maximized',
    'minimization', 'minimize', 'minimizing', 'minimized',
    'algorithm', 'algorithms', 'mathematical', 'mathematics',
    'calculate', 'calculation', 'calculating', 'calculated',
    'compute', 'computation', 'computing', 'computed',
    'production', 'demand', 'storage', 'capacity', 'inventory',
    'operations', 'operational', 'manufacturing', 'logistics',
    'data', 'statistical', 'statistics', 'numerical', 'numeric',
    'uncertainty', 'uncertain', 'uncertainties', 'probability', 
    'probabilistic', 'probable', 'scenario', 'scenarios',
    'model', 'modeling', 'modeled', 'models',
    'visualize', 'visualizing', 'visualized', 'visualization',
    'map', 'mapping', 'mapped', 'diagram', 'diagrams',
    'chart', 'charts', 'graph', 'graphs', 'tree', 'trees',
    'flow', 'flows', 'flowchart', 'flowcharts'
]
```

**Missing in course_config.json:**
- Operations keywords (production, demand, storage, capacity, inventory, operations, manufacturing, logistics)
- Visualization keywords (visualize, visualization, map, mapping, diagram, chart, graph, tree, flow, flowchart)

### **3. Strategic Domain**

**Current course_config.json keywords (20+):**
```json
"strategic": {
  "keywords": [
    "strategy", "strategic", "strategically", "competitive", "advantage", "positioning",
    "market", "industry", "business", "organization", "planning", "planned",
    "competitive advantage", "competitive analysis", "industry analysis",
    "strategic planning", "strategic thinking", "strategic analysis",
    "competitive strategy", "business strategy", "corporate strategy"
  ]
}
```

**query_engine.py keywords (80+):**
```python
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
    # Investment and financial keywords (business/strategic context only)
    'portfolio', 'portfolios', 'fund', 'funds', 'funding', 'funded',
    'return', 'returns', 'revenue', 'revenues', 'profit', 'profits', 'profitable',
    'capital', 'equity', 'stock', 'stocks', 'bond', 'bonds', 'mutual fund', 'mutual funds', 'etf', 'etfs', 'dividend', 'dividends',
    # Education and academic keywords
    'college', 'colleges', 'university', 'universities', 'school', 'schools', 'academic',
    'academics', 'education', 'educational', 'learning', 'learn', 'learned', 'studying',
    'study', 'studies', 'course', 'courses', 'program', 'programs', 'degree', 'degrees',
    'major', 'majors', 'minor', 'minors', 'curriculum', 'curricula', 'tuition', 'scholarship',
    'scholarships', 'admission', 'admissions', 'enroll', 'enrollment', 'enrolled',
    'graduate', 'graduation', 'undergraduate', 'graduate school', 'graduate schools',
    'skill', 'skills', 'development', 'training', 'certification'
]
```

**Missing in course_config.json:**
- Extensive business and marketing keywords (markets, marketing, competition, competitor, etc.)
- Investment and financial keywords (portfolio, fund, capital, equity, stock, bond, etc.)
- Education and academic keywords (college, university, school, academic, education, etc.)
- Decision-making keywords (choice, choose, decide, compare, evaluate, option, alternative, etc.)

### **4. Negotiation Domain**

**Current course_config.json keywords (15+):**
```json
"negotiation": {
  "keywords": [
    "negotiate", "negotiation", "bargain", "deal", "agreement", "contract",
    "discuss", "discussion", "meeting", "conference", "settlement",
    "bargaining", "negotiating", "deal making", "agreement making",
    "contract negotiation", "settlement discussion", "meeting discussion"
  ]
}
```

**query_engine.py keywords (30+):**
```python
negotiation_keywords = [
    'negotiate', 'negotiation', 'negotiating', 'negotiated', 'negotiator', 'negotiators',
    'agreement', 'agree', 'agreeing', 'agreed', 'disagree', 'disagreeing', 'disagreed',
    'bargain', 'bargaining', 'bargained', 'bargaining strategy', 'bargaining strategies', 
    'negotiation strategy', 'negotiation strategies', 'contract', 'contracts', 'contracting', 'contracted', 
    'settlement', 'settle', 'settling', 'settled', 'compromise', 'compromising', 'compromised',
    'proposal', 'proposals', 'propose', 'proposing', 'proposed',
    'counteroffer', 'counteroffers', 'counter-offer', 'counter-offers',
    'terms', 'term', 'condition', 'conditions', 'concession', 'concessions',
    'deadlock', 'impasse', 'deadlocked', 'win-win', 'win win', 'zero-sum', 'zero sum',
    # Add missing negotiation keywords
    'package', 'packages', 'offer', 'offers', 'offering', 'offered', 'deal', 'deals'
]
```

**Missing in course_config.json:**
- Agreement/disagreement keywords (agree, disagree, agreed, disagreed)
- Strategy keywords (bargaining strategy, negotiation strategy, strategies)
- Process keywords (compromise, proposal, counteroffer, terms, conditions, concession)
- Outcome keywords (deadlock, impasse, win-win, zero-sum)
- Additional keywords (package, offer, deal)

## 🎯 **Application Fields - Major Mismatch**

### **Current course_config.json (12 fields):**
```json
"application_fields": [
  "business_strategy", "project_management", "risk_management", 
  "financial_analysis", "operations_management", "human_resources",
  "change_management", "stakeholder_management", "performance_management",
  "supply_chain_management", "quality_management", "innovation_management"
]
```

### **query_engine.py (13 fields):**
```python
# 1. Business & Markets
# 2. Operations Management  
# 3. Financial Decision-Making
# 4. Technology Management
# 5. Risk, Crisis & Resilience
# 6. People, Talent & Career
# 7. Policy & Regulatory
# 8. Product Development & Innovation
# 9. Sustainability & Environment
# 10. Education & Learning
# 11. Healthcare & Medical
# 12. Military & Defense Decisions
# 13. General Decision-Making
```

**Complete mismatch!** The application fields are completely different between the two files.

## 💡 **Recommendation for V1.7**

### **Rebuild course_config.json to match query_engine.py exactly:**

1. **Update all domain keywords** to match query_engine.py exactly
2. **Replace application_fields** with the 13 fields from query_engine.py
3. **Keep the existing structure** (domains, concepts, entity_types, answer_templates)
4. **Extract concepts** from CONCEPT_GLOSSARY in query_engine.py
5. **Update entity_types** if needed based on query_engine.py usage

### **Benefits of rebuilding:**
- ✅ **100% consistency** with the source of truth
- ✅ **Better performance** - matches the fine-tuned keywords
- ✅ **Future-proof** - ready for V1.7 centralized architecture
- ✅ **Reduced maintenance** - single source of truth

### **Implementation approach:**
1. Extract all keywords from query_engine.py functions
2. Extract all concepts from CONCEPT_GLOSSARY
3. Extract application fields from extract_application_field function
4. Rebuild course_config.json with exact matches
5. Test to ensure performance is maintained

This will ensure that V1.7 uses the **exact same logic** that's currently delivering satisfying performance.

