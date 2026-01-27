#!/usr/bin/env python3
"""
Test script to verify and fix the framework selection logic for linear optimization queries.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import generate_course_domain_strategic_lens, detect_course_concept_domains, extract_application_field

def test_linear_optimization_framework_selection():
    """Test that linear optimization queries only select relevant frameworks."""
    
    print("🔍 Testing Linear Optimization Framework Selection")
    print("=" * 60)
    
    # Test query that should only match linear optimization
    test_query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    
    print(f"Query: {test_query}")
    
    try:
        # Get domain and application field
        domains = detect_course_concept_domains(test_query)
        application_field = extract_application_field(test_query)
        
        print(f"Detected domains: {domains}")
        print(f"Application field: {application_field}")
        
        # Generate strategic lens
        course_domain = max(domains.items(), key=lambda x: x[1])[0] if domains else 'general'
        strategic_lens = generate_course_domain_strategic_lens(test_query, course_domain, application_field)
        
        print(f"\nGenerated Strategic Lens:")
        print("-" * 50)
        print(strategic_lens)
        print("-" * 50)
        
        # Check for unwanted frameworks
        unwanted_frameworks = [
            "Monte Carlo simulation",
            "Monte Carlo",
            "simulation"
        ]
        
        found_unwanted = []
        for framework in unwanted_frameworks:
            if framework.lower() in strategic_lens.lower():
                found_unwanted.append(framework)
        
        if found_unwanted:
            print(f"❌ PROBLEM: Found unwanted frameworks: {found_unwanted}")
            return False
        else:
            print("✅ No unwanted frameworks found")
        
        # Check for wanted frameworks
        wanted_frameworks = [
            "Linear optimization",
            "Linear optimization modeling",
            "optimization"
        ]
        
        found_wanted = []
        for framework in wanted_frameworks:
            if framework.lower() in strategic_lens.lower():
                found_wanted.append(framework)
        
        if found_wanted:
            print(f"✅ Found relevant frameworks: {found_wanted}")
            return True
        else:
            print(f"❌ PROBLEM: No relevant frameworks found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_framework_keyword_matching():
    """Test the keyword matching logic for framework selection."""
    
    print(f"\n🔧 Testing Framework Keyword Matching")
    print("=" * 50)
    
    # Test the keyword mappings
    test_keywords = {
        "linear": ["linear", "optimization", "programming", "linear programming"],
        "monte carlo": ["monte carlo", "simulation", "probabilistic", "random", "stochastic"]
    }
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    query_lower = query.lower()
    
    print(f"Query: {query}")
    print(f"Query (lowercase): {query_lower}")
    
    # Check which keywords are found
    found_keywords = {}
    for category, keywords in test_keywords.items():
        found = []
        for keyword in keywords:
            if keyword in query_lower:
                found.append(keyword)
        found_keywords[category] = found
    
    print(f"\nFound keywords by category:")
    for category, keywords in found_keywords.items():
        print(f"  {category}: {keywords}")
    
    # Determine which frameworks should be selected
    if found_keywords["linear"] and not found_keywords["monte carlo"]:
        print("✅ Should select Linear optimization frameworks only")
        return True
    elif found_keywords["monte carlo"] and not found_keywords["linear"]:
        print("✅ Should select Monte Carlo frameworks only")
        return True
    else:
        print("❌ Mixed or no keyword matches found")
        return False

def analyze_framework_selection_logic():
    """Analyze the current framework selection logic."""
    
    print(f"\n🔍 Analyzing Framework Selection Logic")
    print("=" * 50)
    
    # The issue is likely in the scoring algorithm
    print("Current scoring algorithm:")
    print("1. Score each framework based on keyword matches")
    print("2. Weight by keyword length (longer keywords get higher scores)")
    print("3. Bonus for exact matches")
    print("4. Bonus for framework name mentions")
    print("5. Additional bonus for multiple keyword matches")
    print("6. Select top 2 frameworks with highest scores")
    
    print("\nPotential issues:")
    print("1. Monte Carlo might be getting selected due to domain fallback")
    print("2. Scoring might not be strict enough for keyword matching")
    print("3. Fallback logic might be adding irrelevant frameworks")
    
    # Check the technical domain frameworks
    technical_frameworks = [
        "Monte Carlo simulation",
        "Linear optimization modeling", 
        "Sensitivity analysis",
        "Decision tree analysis",
        "Expected value calculations"
    ]
    
    print(f"\nTechnical domain frameworks:")
    for i, framework in enumerate(technical_frameworks, 1):
        print(f"  {i}. {framework}")
    
    print("\nThe issue: Linear optimization should be prioritized over Monte Carlo for this query")

if __name__ == "__main__":
    print("🚀 Starting Linear Optimization Framework Selection Analysis")
    print("=" * 70)
    
    # Run tests
    test1_result = test_linear_optimization_framework_selection()
    test2_result = test_framework_keyword_matching()
    analyze_framework_selection_logic()
    
    print(f"\n✅ Analysis Complete")
    print("=" * 70)
    
    if test1_result and test2_result:
        print("✅ Framework selection working correctly")
    else:
        print("❌ Framework selection needs fixing") 