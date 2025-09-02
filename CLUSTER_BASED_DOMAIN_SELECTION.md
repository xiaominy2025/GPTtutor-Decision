# Cluster-Based Domain Selection System

## Overview

The ThinkPal Decision Coach system now uses an improved cluster-based domain selection approach that replaces the previous threshold-based logic. This new system provides more intelligent and context-aware domain detection for semantic, keyword, and hybrid methods.

## Key Improvements

### 1. **Cluster-Based Logic**
- **Primary Cluster**: Strongly relevant domains with minimal score gaps
- **Secondary Cluster**: Modest domains that meet quality thresholds
- **Weak Domain Rejection**: Secondary clusters are rejected if they contain weak domains
- **Maximum Domain Cap**: Typically 3 domains, rarely 4 for exceptional cases

### 2. **Method-Specific Parameters**
Each detection method has optimized parameters based on its characteristics:

#### **Semantic Method** (Most Precise)
- **Primary Gap**: 0.08 (very tight clustering for normalized semantic scores 0.3-1.0)
- **Secondary Gap**: 0.06 (tight secondary cluster detection)
- **Weak Threshold**: 0.35 (high quality bar for normalized semantic scores)
- **Primary Min Score**: 0.45
- **Secondary Min Score**: 0.35

#### **Keyword Method** (Less Precise)
- **Primary Gap**: 0.20 (moderate clustering for normalized keyword scores 0.1-1.0)
- **Secondary Gap**: 0.15 (moderate secondary cluster detection)
- **Weak Threshold**: 0.25 (standard quality bar for keyword methods)
- **Primary Min Score**: 0.30
- **Secondary Min Score**: 0.25

#### **Hybrid Method** (Balanced Approach)
- **Primary Gap**: 0.12 (balanced clustering for hybrid combining both methods)
- **Secondary Gap**: 0.10 (balanced secondary detection)
- **Weak Threshold**: 0.30 (balanced quality requirements)
- **Primary Min Score**: 0.38
- **Secondary Min Score**: 0.30

## Core Functions

### 1. **`detect_domain_clusters_improved(domain_scores, method)`**
Detects clusters of domains based on score gaps.

**Parameters:**
- `domain_scores`: Dictionary of domain scores
- `method`: "semantic", "keyword", or "hybrid"

**Returns:**
- List of clusters, each containing (domain, score) tuples

**Logic:**
- Sorts domains by score (highest first)
- Creates primary cluster using method-specific primary gap threshold
- Creates secondary clusters using method-specific secondary gap threshold
- Continues clustering until all domains are assigned

### 2. **`select_domains_by_clusters_improved(domain_scores, method, max_domains)`**
Selects domains using cluster-based logic with quality filtering.

**Parameters:**
- `domain_scores`: Dictionary of domain scores
- `method`: "semantic", "keyword", or "hybrid"
- `max_domains`: Maximum number of domains to select (default 3)

**Returns:**
- Dictionary of selected domains with their scores

**Selection Logic:**
1. **Primary Cluster**: Always included if average score meets primary threshold
2. **Secondary Cluster**: Included if:
   - Average score meets secondary threshold
   - No weak domains (below secondary threshold)
   - Room available within max_domains limit
3. **Third Cluster**: Rarely included (only for 4-domain cases with very strong scores)

### 3. **`hybrid_domain_detection_improved(query)`**
Combines semantic and keyword methods using cluster-based selection with score normalization.

**Process:**
1. Get domain scores from both semantic and keyword methods
2. **Normalize scores within each method** to prevent keyword dominance:
   - **Semantic scores**: Already 0-1, normalize to max=1.0
   - **Keyword scores**: Can be 0-15+ (weighted), normalize to 0-1
3. Apply cluster-based selection to each normalized method independently
4. Combine normalized scores using `max(semantic, keyword)` for overlapping domains
5. Apply final cluster-based selection to combined scores
6. Cap at maximum 3 domains
7. **General domain fallback**: Only selected if no specific domains (behavioral, technical, strategic, negotiation) are picked

**Why Normalization is Critical:**
- **Keyword scores**: 3×strong + 2×modest + 1×weak can result in scores 0-15+
- **Semantic scores**: Cosine similarity typically 0-1
- **Without normalization**: Keyword scores would always dominate hybrid combination
- **With normalization**: Both methods contribute equally to final selection

**Parameter Adjustment After Normalization:**
- **Semantic**: Much tighter clustering (0.08/0.06 gaps) because normalized scores are higher (0.3-1.0)
- **Keyword**: Moderate clustering (0.20/0.15 gaps) because normalized scores are more spread (0.1-1.0)
- **Hybrid**: Balanced clustering (0.12/0.10 gaps) combining both normalized methods

**General Domain Handling:**
- **Removed before clustering**: General domain is filtered out to reduce noise in all methods
- **Fallback only**: General domain is only selected when no specific domains meet quality thresholds
- **Quality control**: Ensures behavioral, technical, strategic, and negotiation domains are prioritized

## Domain Selection Examples

### **Example 1: Single Strong Domain**
```
Scores: {"behavioral": 0.8, "technical": 0.2, "strategic": 0.1, "negotiation": 0.05}

Clusters:
- Primary: [behavioral(0.8)]
- Secondary: [technical(0.2), strategic(0.1), negotiation(0.05)]

Result: behavioral(0.8) only
Reason: Secondary cluster contains weak domains, rejected
```

### **Example 2: Two Balanced Domains**
```
Scores: {"behavioral": 0.7, "technical": 0.65, "strategic": 0.2, "negotiation": 0.1}

Clusters:
- Primary: [behavioral(0.7), technical(0.65)]
- Secondary: [strategic(0.2), negotiation(0.1)]

Result: behavioral(0.7), technical(0.65)
Reason: Primary cluster has two strong domains, secondary rejected due to weak scores
```

### **Example 3: Three Quality Domains**
```
Scores: {"behavioral": 0.8, "technical": 0.75, "strategic": 0.6, "negotiation": 0.3}

Clusters:
- Primary: [behavioral(0.8), technical(0.75)]
- Secondary: [strategic(0.6)]
- Third: [negotiation(0.3)]

Result: behavioral(0.8), technical(0.75), strategic(0.6)
Reason: Primary and secondary clusters both meet quality thresholds
```

### **Example 4: Hybrid Normalization Process**
```
Raw Scores:
- Keyword: behavioral(12), technical(9), strategic(3), negotiation(1)
- Semantic: behavioral(0.5), technical(0.4), strategic(0.3), negotiation(0.2)

Normalization:
- Keyword: behavioral(1.0), technical(0.75), strategic(0.25), negotiation(0.08)
- Semantic: behavioral(1.0), technical(0.8), strategic(0.6), negotiation(0.4)

Hybrid Combination (max):
- behavioral: max(1.0, 1.0) = 1.0
- technical: max(0.75, 0.8) = 0.8
- strategic: max(0.25, 0.6) = 0.6
- negotiation: max(0.08, 0.4) = 0.4

Final Result: behavioral(1.0), technical(0.8), strategic(0.6)
```

### **Example 5: General Domain Fallback**
```
Scores: {"behavioral": 0.15, "technical": 0.12, "strategic": 0.08, "negotiation": 0.05}

Clusters:
- Primary: [behavioral(0.15), technical(0.12), strategic(0.08), negotiation(0.05)]

Result: {} (no domains selected)
Reason: All scores below minimum thresholds (0.45 for semantic, 0.30 for keyword, 0.38 for hybrid)

Fallback: {'general': 1.0}
Reason: No specific domains meet quality requirements, general domain selected as fallback

## Integration with Existing System

### **Backward Compatibility**
- All existing function names are preserved
- New functions are added with `_improved` suffix
- Legacy functions are wrapped to call improved versions
- No breaking changes to existing code

### **Performance Impact**
- **Minimal overhead**: Cluster detection is lightweight
- **Cached results**: Domain detection results are cached
- **Efficient algorithms**: O(n log n) complexity for clustering
- **Early termination**: Stops when max_domains is reached

### **Error Handling**
- **Graceful fallbacks**: Falls back to previous methods if clustering fails
- **Exception safety**: Continues operation even with individual method failures
- **Logging**: Comprehensive error logging for debugging

## Configuration and Tuning

### **Adjusting Cluster Thresholds**
Modify the `cluster_params` dictionary in `detect_domain_clusters_improved`:

```python
cluster_params = {
    "semantic": {
        "primary_gap": 0.20,      # Adjust for tighter/looser primary clustering
        "secondary_gap": 0.15,    # Adjust for secondary cluster sensitivity
        "weak_threshold": 0.25    # Adjust quality bar for secondary inclusion
    },
    # ... other methods
}
```

### **Adjusting Selection Thresholds**
Modify the `selection_params` dictionary in `select_domains_by_clusters_improved`:

```python
selection_params = {
    "semantic": {
        "primary_min_score": 0.30,    # Adjust minimum score for primary inclusion
        "secondary_min_score": 0.25,  # Adjust minimum score for secondary inclusion
        "weak_rejection": True        # Enable/disable weak domain rejection
    },
    # ... other methods
}
```

## Testing and Validation

### **Test Script**
Run `test_cluster_domain_selection.py` to validate the system:

```bash
python test_cluster_domain_selection.py
```

### **Test Coverage**
- **Cluster Detection**: Tests various score distributions
- **Domain Selection**: Tests different quality thresholds
- **Real Queries**: Tests with actual user queries
- **Parameter Sensitivity**: Tests boundary conditions

### **Expected Behaviors**
1. **High-quality queries**: Should select 2-3 relevant domains
2. **Mixed-quality queries**: Should select primary domain + strong secondary
3. **Low-quality queries**: Should select only primary domain or fall back to general
4. **Edge cases**: Should handle boundary conditions gracefully

## Migration Guide

### **For Existing Code**
No changes required - all existing function calls continue to work.

### **For New Features**
Use the improved functions directly:

```python
# Old way (still works)
domains = detect_domain_semantic(query)

# New way (recommended)
domains = detect_domain_semantic_improved(query)

# Hybrid approach (best of both worlds)
domains = hybrid_domain_detection_improved(query)
```

### **For Custom Implementations**
Extend the cluster parameters for your specific use case:

```python
def custom_cluster_detection(domain_scores):
    # Use existing cluster logic with custom parameters
    return detect_domain_clusters_improved(domain_scores, "custom")
```

## Benefits of the New System

### **1. Improved Accuracy**
- **Context-aware clustering**: Considers domain relationships
- **Quality filtering**: Rejects weak domains in secondary clusters
- **Method optimization**: Parameters tuned for each detection method

### **2. Better Consistency**
- **Predictable behavior**: Clear rules for domain selection
- **Reduced noise**: Fewer irrelevant domains selected
- **Balanced selection**: Appropriate number of domains for each query

### **3. Enhanced Flexibility**
- **Configurable thresholds**: Easy to adjust for different use cases
- **Method-specific tuning**: Optimized parameters for each approach
- **Extensible design**: Easy to add new clustering methods

### **4. Performance Improvements**
- **Efficient algorithms**: Optimized clustering and selection
- **Caching support**: Results cached for repeated queries
- **Early termination**: Stops processing when limits reached

## Future Enhancements

### **Planned Features**
1. **Dynamic threshold adjustment**: Automatic parameter tuning based on query characteristics
2. **Multi-level clustering**: Hierarchical domain relationships
3. **Learning-based optimization**: Parameters that improve over time
4. **Domain-specific rules**: Custom logic for specialized domains

### **Research Areas**
1. **Optimal gap thresholds**: Data-driven parameter optimization
2. **Cluster quality metrics**: Quantitative measures of clustering effectiveness
3. **Hybrid method improvements**: Better combination strategies
4. **Real-time adaptation**: Dynamic parameter adjustment during operation

## Conclusion

The new cluster-based domain selection system represents a significant improvement over the previous threshold-based approach. It provides more intelligent, consistent, and accurate domain detection while maintaining backward compatibility and performance. The system is designed to be easily configurable and extensible for future enhancements.
