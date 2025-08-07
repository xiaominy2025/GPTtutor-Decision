# Concept Selection Logic Analysis & Domain-Driven Solution

## 🔍 **Current System Problems**

### **Problem 1: No Domain-Driven Selection**
Current logic: Semantic similarity → Domain multipliers → Top K selection
**Missing**: Primary domain enforcement and domain-balanced selection

### **Problem 2: Technical Concepts Override Behavioral**
Example: "budget salary" query
- ✅ Domain detected: behavioral (1.000)
- ❌ Concepts selected: seasonal forecasting, aggregate planning (technical)
- ❌ Expected: mental accounting, framing bias (behavioral)

### **Problem 3: Weak Domain Enforcement**
Domain multipliers (0.6-1.5) are insufficient to override semantic similarity

## 🎯 **Proposed Domain-Driven Solution**

### **Single Domain Logic (3 concepts)**
```
If primary_domain_score > 0.8:
    Select 3 concepts from primary domain only
    Rank by: semantic_similarity + domain_boost
```

### **Multi-Domain Logic (2+1+1)**
```
If multiple domains detected:
    Select 2 concepts from primary domain
    Select 1 concept from each secondary domain (score > 0.3)
    Rank within each domain by: semantic_similarity + domain_boost
```

### **Domain Enforcement Rules**
1. **Primary domain concepts** get +0.5 boost
2. **Secondary domain concepts** get +0.3 boost  
3. **Non-domain concepts** get -0.5 penalty
4. **Minimum domain representation**: At least 50% from primary domain

## 🔧 **Implementation Strategy**

### **Step 1: Domain Classification**
```python
def classify_concepts_by_domain(concepts, query_domains):
    primary_domain = max(query_domains, key=query_domains.get)
    domain_concepts = {
        'primary': [],
        'secondary': [],
        'other': []
    }
    # Classify each concept by domain
    return domain_concepts
```

### **Step 2: Domain-Balanced Selection**
```python
def select_domain_balanced_concepts(domain_concepts, top_k=3):
    if len(query_domains) == 1:
        # Single domain: 3 from primary
        return select_top_from_domain(domain_concepts['primary'], 3)
    else:
        # Multi-domain: 2 from primary + 1 from each secondary
        selected = select_top_from_domain(domain_concepts['primary'], 2)
        for secondary_domain in secondary_domains:
            selected.extend(select_top_from_domain(domain_concepts['secondary'], 1))
        return selected
```

### **Step 3: Enhanced Domain Boosting**
```python
def apply_domain_boosting(concept_name, concept_domain, query_domains):
    primary_domain = max(query_domains, key=query_domains.get)
    
    if concept_domain == primary_domain:
        return 0.5  # Strong primary domain boost
    elif concept_domain in query_domains:
        return 0.3  # Secondary domain boost
    else:
        return -0.5  # Strong penalty for non-domain concepts
```

## 📊 **Expected Results**

### **Behavioral Domain Query: "How to deal with unfair critiques?"**
**Current**: seasonal forecasting, aggregate planning (technical)
**Proposed**: framing bias, confirmation bias, anchoring bias (behavioral)

### **Money-Related Query: "How to budget salary?"**  
**Current**: seasonal forecasting, aggregate planning (technical)
**Proposed**: mental accounting, framing bias, confirmation bias (behavioral)

## 🚀 **Implementation Priority**

1. **High Priority**: Implement domain-driven selection logic
2. **Medium Priority**: Add domain classification function
3. **Low Priority**: Fine-tune domain boosting values

This will ensure that behavioral domain queries get behavioral concepts, not technical ones! 