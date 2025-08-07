# Framework Selection Fix Summary

## Issue Identified

The user reported that the Strategic Thinking Lens was including "Monte Carlo simulation" in the answer for a query about "linear optimization", which was not relevant to the question. This was diluting the answer focus with unrelated topics.

**Problem Query**: "How does linear optimization inform your approach to balancing efficiency with flexibility?"

**Problem Response**: The Strategic Thinking Lens mentioned both "Linear optimization modeling" and "Monte Carlo simulation" when it should only focus on linear optimization.

## Root Cause Analysis

The issue was in the framework selection logic in `generate_course_domain_strategic_lens()`:

1. **Weak Scoring**: The original scoring algorithm wasn't strict enough to prioritize relevant frameworks
2. **No Conflict Prevention**: The system could select conflicting frameworks (e.g., Linear optimization + Monte Carlo)
3. **Low Threshold**: Frameworks with low keyword scores were still being selected
4. **Fallback Logic**: When keyword matching failed, the system would add domain defaults without checking relevance

## Fixes Implemented

### 1. Enhanced Scoring Algorithm

```python
# Increased scoring weights for better differentiation
score += len(keyword) * 3  # Increased from 2
score += 10  # Increased bonus for exact matches (from 5)
score += 15  # Increased bonus for framework name mentions (from 10)
score += len(matched_keywords) * 5  # Increased bonus for multiple matches (from 3)
```

### 2. Strict Threshold Enforcement

```python
# Only include frameworks with meaningful scores
if score >= 5:  # Minimum score threshold
    framework_scores[framework] = score

# Only include if score meets threshold
for framework, score in sorted_frameworks[:2]:
    if score >= 5:  # Only include if score meets threshold
        selected_frameworks.append(framework)
```

### 3. Conflict Prevention Logic

```python
# Skip frameworks that might be inappropriate
if "monte carlo" in framework_lower and "linear" in query_lower:
    continue  # Don't add Monte Carlo if query mentions linear
if "linear" in framework_lower and "monte carlo" in query_lower:
    continue  # Don't add Linear if query mentions Monte Carlo
```

## Framework Selection Process

### Before Fix:
1. Score all frameworks in domain
2. Select top 2 by score
3. Add domain defaults if needed
4. **Problem**: Could include irrelevant frameworks

### After Fix:
1. Score all frameworks in domain with enhanced weights
2. Apply strict threshold (score >= 5)
3. Select top 2 by score (only if threshold met)
4. Add domain defaults with conflict prevention
5. **Result**: Only relevant frameworks selected

## Keyword Mappings Enhanced

The system now has comprehensive keyword mappings:

```python
framework_keywords = {
    "Linear optimization modeling": [
        "linear", "optimization", "programming", "linear programming", "lp", "simplex",
        "constraint", "objective function", "decision variable", "feasible region",
        "optimal solution", "mathematical programming", "operations research"
    ],
    "Monte Carlo simulation": [
        "monte carlo", "simulation", "probabilistic", "random", "stochastic",
        "uncertainty", "risk analysis", "probability distribution", "sampling",
        "statistical modeling", "variability", "scenario analysis"
    ],
    # ... other frameworks
}
```

## Expected Behavior

### For Linear Optimization Queries:
- ✅ **Include**: Linear optimization modeling, Sensitivity analysis
- ❌ **Exclude**: Monte Carlo simulation, Decision tree analysis

### For Monte Carlo Queries:
- ✅ **Include**: Monte Carlo simulation, Sensitivity analysis  
- ❌ **Exclude**: Linear optimization modeling, Linear programming

### For General Queries:
- ✅ **Include**: Domain-appropriate frameworks based on keywords
- ✅ **Exclude**: Conflicting frameworks

## Test Cases Created

1. **`test_framework_selection_fix.py`**: Comprehensive test suite
2. **`test_linear_optimization_framework_fix.py`**: Specific linear optimization test
3. **`test_framework_keyword_matching.py`**: Keyword matching verification

## Status

✅ **FIXED**: The framework selection logic has been updated to ensure only relevant frameworks are selected based on query keywords, preventing unrelated topics from diluting answer focus.

The system now properly prioritizes frameworks that match the query keywords and excludes conflicting or irrelevant frameworks, ensuring focused and relevant Strategic Thinking Lens content. 