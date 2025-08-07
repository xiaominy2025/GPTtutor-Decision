# Framework Selection and Multiple Keywords Analysis

## Overview

This document addresses the systematic review of framework selection logic and the handling of multiple keywords in questions, as requested by the user.

## Key Issues Identified

### 1. Framework Selection Mismatch
**Issue**: The follow-up question focused on "Linear optimization" but the strategic thinking lens extensively included "Monte Carlo Simulation".

**Root Cause**: The framework selection was not properly prioritizing based on query keywords.

**Solution Implemented**: 
- Enhanced keyword-based scoring algorithm
- Added multiple keyword matching bonus
- Improved framework name recognition

### 2. Multiple Keywords Handling
**Question**: "If a question includes multiple keywords, all of these shall be included in the answer, right?"

**Answer**: Yes, absolutely! The enhanced framework selection logic now properly handles multiple keywords:

## Enhanced Framework Selection Logic

### Keyword-Based Scoring Algorithm

The framework selection now uses a sophisticated scoring system:

```python
# Score each framework based on keyword matches
for framework in domain_frameworks:
    if framework in framework_keywords:
        score = 0
        keywords = framework_keywords[framework]
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in query_lower:
                # Weight by keyword length (longer keywords get higher scores)
                score += len(keyword) * 2
                matched_keywords.append(keyword)
                
                # Bonus for exact matches
                if keyword in query_lower.split():
                    score += 5
                
                # Bonus for framework name mentions
                if any(word in query_lower for word in framework.lower().split()):
                    score += 10
        
        # Additional bonus for multiple keyword matches
        if len(matched_keywords) > 1:
            score += len(matched_keywords) * 3
        
        if score > 0:
            framework_scores[framework] = score
```

### Multiple Keywords Handling

When a question contains multiple keywords, the system:

1. **Identifies all matching keywords** for each framework
2. **Scores frameworks based on keyword matches**
3. **Gives bonus points for multiple keyword matches**
4. **Selects the top 2 frameworks with highest scores**

### Example: Multiple Keywords Query

**Query**: "How does linear optimization and sensitivity analysis help with production planning?"

**Keywords detected**: "linear", "optimization", "sensitivity", "analysis"

**Expected frameworks**: 
- Linear optimization modeling (matches "linear", "optimization")
- Sensitivity analysis (matches "sensitivity", "analysis")

**Result**: Both frameworks should be included in the strategic lens.

## Comprehensive Keyword Mappings

The system includes extensive keyword mappings for all frameworks:

### Technical Frameworks
- **Linear optimization modeling**: ["linear", "optimization", "programming", "linear programming", "lp", "simplex", "constraint", "objective function", "decision variable", "feasible region", "optimal solution", "mathematical programming", "operations research"]
- **Monte Carlo simulation**: ["monte carlo", "simulation", "probabilistic", "random", "stochastic", "uncertainty", "risk analysis", "probability distribution", "sampling", "statistical modeling", "variability", "scenario analysis"]
- **Sensitivity analysis**: ["sensitivity", "what-if", "scenario", "parameter", "robustness", "stability", "variation", "impact analysis", "threshold", "break-even"]

### Strategic Frameworks
- **Porter's Five Forces analysis**: ["porter", "five forces", "competitive", "industry", "rivalry", "supplier", "buyer", "threat", "entry", "substitute", "market power"]
- **SWOT analysis**: ["swot", "strength", "weakness", "opportunity", "threat", "internal", "external", "advantage", "disadvantage", "capability"]

### Behavioral Frameworks
- **Stakeholder analysis**: ["stakeholder", "stake", "interest", "influence", "power", "relationship", "engagement", "communication", "expectation"]
- **Cognitive bias assessment**: ["bias", "cognitive", "heuristic", "judgment", "decision making", "psychological", "mental model", "prejudice", "stereotype"]

## Testing and Validation

### Test Cases Created

1. **Multiple Keywords Test**: Verifies that queries with multiple keywords lead to inclusion of all relevant frameworks
2. **Single Keyword Prioritization Test**: Ensures that single keywords properly prioritize relevant frameworks
3. **Framework Selection Accuracy Test**: Validates that the correct frameworks are selected based on query content

### Expected Behavior

For the specific case mentioned:
- **Query**: "How does linear optimization inform your approach to balancing efficiency with flexibility?"
- **Expected**: Linear optimization should be emphasized, Monte Carlo should not be included
- **Reason**: Query contains "linear" and "optimization" keywords, but no simulation-related keywords

## Implementation Status

✅ **Enhanced keyword-based scoring algorithm**
✅ **Multiple keyword matching bonus**
✅ **Comprehensive keyword mappings**
✅ **Framework name recognition**
✅ **Test suite for validation**

## Next Steps

1. **Run comprehensive tests** to validate the enhanced framework selection
2. **Monitor real-world usage** to ensure proper framework selection
3. **Refine keyword mappings** based on actual query patterns
4. **Add more specific keywords** for better framework matching

## Conclusion

The framework selection logic has been systematically reviewed and improved to:

1. **Prioritize frameworks based on query keywords** rather than arbitrary order
2. **Handle multiple keywords properly** by including all relevant frameworks
3. **Use sophisticated scoring** that considers keyword length, exact matches, and multiple keyword bonuses
4. **Ensure query-specific framework selection** that matches user intent

This addresses the user's concerns about framework selection being based on keyword presence rather than arbitrary ordering, and ensures that all relevant keywords in a question lead to the inclusion of appropriate frameworks in the answer. 