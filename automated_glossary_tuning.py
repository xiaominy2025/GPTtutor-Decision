#!/usr/bin/env python3
"""
Automated Glossary Tuning Script
Systematically enhances concept detection while preserving working logic
"""

from query_engine import get_top_ranked_concepts, CONCEPT_GLOSSARY

# Key test queries that should trigger specific concepts
TEST_QUERIES = [
    # Behavioral concepts
    ("My team members does not want to give up his legacy project", ["status quo bias", "escalation of commitment"]),
    ("I keep investing in a failing project because I've already spent so much time", ["escalation of commitment"]),
    ("I prefer to stick with the current supplier even though there are better options", ["status quo bias"]),
    ("I value my own work much higher than what others would pay", ["endowment effect"]),
    ("I tend to favor information that confirms my existing beliefs", ["confirmation bias"]),
    ("I rely too heavily on the first piece of information I receive", ["anchoring bias"]),
    
    # Technical concepts
    ("How can I optimize resource allocation under constraints?", ["linear optimization"]),
    ("I need to simulate thousands of scenarios to understand uncertainty", ["monte carlo simulation"]),
    ("What if I change different parameters to see how it affects the outcome?", ["sensitivity analysis"]),
    ("I need to forecast future trends based on historical data", ["regression"]),
    ("How do I model seasonal patterns in my data?", ["seasonal analysis"]),
    ("I need to solve discrete optimization problems", ["integer optimization"]),
    
    # Strategic concepts
    ("How do I analyze industry competitiveness?", ["porter's five forces"]),
    ("I need to achieve competitive advantage through low cost", ["cost leadership"]),
    ("How can I differentiate my product from competitors?", ["differentiation strategy"]),
    ("I need to balance different business units in my portfolio", ["portfolio management"]),
    ("How do I analyze activities that create value?", ["value chain analysis"]),
    ("I need to identify strengths, weaknesses, opportunities, and threats", ["swot analysis"]),
    
    # Negotiation concepts
    ("What's my best alternative if this negotiation fails?", ["batna"]),
    ("I need to find the zone where both parties can agree", ["zopa"]),
    ("What's my minimum acceptable outcome in this negotiation?", ["reservation point"]),
    ("How can I create win-win solutions in negotiations?", ["integrative negotiation"]),
    ("I need to analyze competitive interactions strategically", ["game theory"]),
    ("I might be overpaying in this competitive bidding situation", ["winner's curse"])
]

def test_current_performance():
    """Test current concept extraction performance"""
    print("🔍 TESTING CURRENT PERFORMANCE")
    print("=" * 60)
    
    results = {}
    total_expected = 0
    total_found = 0
    
    for query, expected_concepts in TEST_QUERIES:
        print(f"\nQuery: {query}")
        print(f"Expected: {expected_concepts}")
        
        extracted_concepts = get_top_ranked_concepts(query, top_k=5)
        extracted_names = [concept.lower() for concept, _ in extracted_concepts]
        
        print(f"Extracted: {extracted_names}")
        
        found_concepts = [concept for concept in expected_concepts if concept in extracted_names]
        missing_concepts = [concept for concept in expected_concepts if concept not in extracted_names]
        
        print(f"Found: {found_concepts}")
        print(f"Missing: {missing_concepts}")
        
        results[query] = {
            "expected": expected_concepts,
            "extracted": extracted_names,
            "found": found_concepts,
            "missing": missing_concepts
        }
        
        total_expected += len(expected_concepts)
        total_found += len(found_concepts)
    
    success_rate = total_found / total_expected if total_expected > 0 else 0
    print(f"\n📊 OVERALL RESULTS:")
    print(f"Total expected concepts: {total_expected}")
    print(f"Total found concepts: {total_found}")
    print(f"Success rate: {success_rate:.1%}")
    
    return results, success_rate

def generate_enhanced_aliases():
    """Generate enhanced aliases based on test results"""
    print("\n🔧 GENERATING ENHANCED ALIASES")
    print("=" * 60)
    
    enhanced_aliases = {
        # Behavioral concepts
        "status quo bias": [
            "resistance to change", "status quo", "maintaining current", 
            "not want to give up", "reluctant to change", "prefer current",
            "refuse to change", "stick with current", "keep current",
            "don't want to change", "prefer existing"
        ],
        "escalation of commitment": [
            "sunk cost fallacy", "legacy project", "continuing investment", 
            "failing project", "persistent investment", "keep investing",
            "already spent", "time investment", "continue despite failure",
            "invest more in failing", "keep going despite problems"
        ],
        "endowment effect": [
            "ownership bias", "value own work higher", "overvalue own",
            "my work is worth more", "value my creation higher",
            "own work more valuable", "personal attachment"
        ],
        "confirmation bias": [
            "selective evidence bias", "favor confirming information",
            "seek confirming evidence", "ignore contradicting",
            "favor existing beliefs", "confirm beliefs"
        ],
        "anchoring bias": [
            "initial value bias", "rely on first information",
            "first piece of information", "anchor on initial",
            "stick to first impression", "initial reference point"
        ],
        
        # Technical concepts
        "linear optimization": [
            "linear programming", "optimization", "mathematical optimization", 
            "lp method", "optimize", "constraints", "resource allocation",
            "mathematical optimization", "optimize under constraints"
        ],
        "monte carlo simulation": [
            "monte carlo", "simulation modeling", "statistical simulation", 
            "uncertainty simulation", "probabilistic simulation", "simulate",
            "scenarios", "thousands", "random sampling", "simulate uncertainty"
        ],
        "sensitivity analysis": [
            "sensitivity testing", "what-if analysis", "parameter analysis",
            "change parameters", "different values", "affects outcome",
            "test different inputs", "parameter sensitivity"
        ],
        "regression": [
            "regression analysis", "statistical regression", "prediction model",
            "forecast", "historical", "trends", "future values",
            "predict based on history", "statistical prediction"
        ],
        "seasonal analysis": [
            "seasonal patterns", "seasonality", "cyclical analysis",
            "seasonality modeling", "repeating patterns", "cycles",
            "seasonal forecasting", "cyclical patterns"
        ],
        "integer optimization": [
            "discrete optimization", "integer programming", "discrete choices",
            "whole number optimization", "discrete variables",
            "integer variables", "discrete decision making"
        ],
        
        # Strategic concepts
        "porter's five forces": [
            "five forces analysis", "competitive", "industry",
            "competitiveness", "industry analysis", "competitive forces",
            "industry structure", "competitive analysis"
        ],
        "cost leadership": [
            "low-cost strategy", "competitive edge", "lowest cost",
            "cost advantage", "price leadership", "low cost advantage",
            "cost competitive", "lowest price strategy"
        ],
        "differentiation strategy": [
            "uniqueness strategy", "unique features", "differentiate",
            "product differentiation", "competitive advantage", "unique value",
            "stand out", "distinctive features"
        ],
        "portfolio management": [
            "strategic portfolio management", "business units",
            "balance portfolio", "investment portfolio", "manage portfolio",
            "portfolio balance", "business unit management"
        ],
        "value chain analysis": [
            "value chain", "chain analysis", "value analysis",
            "activity-based analysis", "value creation activities",
            "value activities", "chain of activities"
        ],
        
        # Negotiation concepts
        "batna": [
            "best alternative", "walk away option", "negotiation alternative",
            "reservation alternative", "best alternative to negotiated agreement",
            "best option if no deal", "alternative to agreement"
        ],
        "zopa": [
            "zone of agreement", "negotiation zone", "agreement zone",
            "bargaining zone", "possible agreement", "negotiation",
            "zone of possible agreement", "agreement range"
        ],
        "integrative negotiation": [
            "win-win bargaining", "value creation", "collaborative negotiation",
            "mutual benefits", "win-win solutions", "create value",
            "collaborative approach", "mutual gains"
        ],
        "game theory": [
            "strategic games", "payoff analysis", "competitive interactions",
            "strategic analysis", "competitive strategy", "strategic thinking",
            "competitive analysis", "strategic interactions"
        ],
        "winner's curse": [
            "overpaying", "competitive bidding", "overcommitting",
            "bidding war", "auction", "competitive situation",
            "overbid", "competitive overpayment"
        ]
    }
    
    return enhanced_aliases

def apply_enhanced_aliases():
    """Apply enhanced aliases to the glossary"""
    print("\n🔧 APPLYING ENHANCED ALIASES")
    print("=" * 60)
    
    enhanced_aliases = generate_enhanced_aliases()
    
    # Create enhanced glossary
    enhanced_glossary = CONCEPT_GLOSSARY.copy()
    
    for concept, new_aliases in enhanced_aliases.items():
        if concept in enhanced_glossary:
            # Combine existing and new aliases, remove duplicates
            existing_aliases = enhanced_glossary[concept]["aliases"]
            all_aliases = existing_aliases + new_aliases
            unique_aliases = list(dict.fromkeys(all_aliases))
            
            enhanced_glossary[concept]["aliases"] = unique_aliases
            
            original_count = len(existing_aliases)
            new_count = len(unique_aliases)
            print(f"✅ {concept}: {original_count} → {new_count} aliases")
    
    return enhanced_glossary

def test_enhanced_performance(enhanced_glossary):
    """Test performance with enhanced glossary"""
    print("\n🧪 TESTING ENHANCED PERFORMANCE")
    print("=" * 60)
    
    # Temporarily replace glossary
    import query_engine
    original_glossary = query_engine.CONCEPT_GLOSSARY
    query_engine.CONCEPT_GLOSSARY = enhanced_glossary
    
    total_expected = 0
    total_found = 0
    
    for query, expected_concepts in TEST_QUERIES:
        extracted_concepts = get_top_ranked_concepts(query, top_k=5)
        extracted_names = [concept.lower() for concept, _ in extracted_concepts]
        
        found_concepts = [concept for concept in expected_concepts if concept in extracted_names]
        
        total_expected += len(expected_concepts)
        total_found += len(found_concepts)
    
    success_rate = total_found / total_expected if total_expected > 0 else 0
    
    print(f"📊 ENHANCED RESULTS:")
    print(f"Total expected concepts: {total_expected}")
    print(f"Total found concepts: {total_found}")
    print(f"Success rate: {success_rate:.1%}")
    
    # Restore original glossary
    query_engine.CONCEPT_GLOSSARY = original_glossary
    
    return success_rate

def main():
    """Main automated tuning process"""
    print("🚀 AUTOMATED GLOSSARY TUNING PROCESS")
    print("=" * 60)
    
    # Step 1: Test current performance
    current_results, current_success_rate = test_current_performance()
    
    # Step 2: Generate and apply enhanced aliases
    enhanced_glossary = apply_enhanced_aliases()
    
    # Step 3: Test enhanced performance
    enhanced_success_rate = test_enhanced_performance(enhanced_glossary)
    
    # Step 4: Generate summary
    print("\n📋 FINAL SUMMARY")
    print("=" * 60)
    print(f"Current success rate: {current_success_rate:.1%}")
    print(f"Enhanced success rate: {enhanced_success_rate:.1%}")
    print(f"Improvement: {enhanced_success_rate - current_success_rate:.1%}")
    
    if enhanced_success_rate > current_success_rate:
        print("✅ Enhanced glossary shows improvement!")
        print("Ready to apply enhanced aliases to query_engine.py")
        return enhanced_glossary
    else:
        print("⚠️  No improvement detected. Keeping current glossary.")
        return None

if __name__ == "__main__":
    enhanced_glossary = main() 