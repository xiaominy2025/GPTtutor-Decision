#!/usr/bin/env python3
"""
Apply Enhanced Aliases to Glossary
Directly applies systematically enhanced aliases to improve concept detection
"""

# Enhanced aliases based on systematic analysis of query patterns
ENHANCED_ALIASES = {
    # Behavioral concepts - enhanced for better detection
    "status quo bias": [
        "resistance to change", "status quo", "maintaining current", 
        "not want to give up", "reluctant to change", "prefer current",
        "refuse to change", "stick with current", "keep current",
        "don't want to change", "prefer existing", "stick to current"
    ],
    "escalation of commitment": [
        "sunk cost fallacy", "legacy project", "continuing investment", 
        "failing project", "persistent investment", "keep investing",
        "already spent", "time investment", "continue despite failure",
        "invest more in failing", "keep going despite problems", "legacy"
    ],
    "endowment effect": [
        "ownership bias", "value own work higher", "overvalue own",
        "my work is worth more", "value my creation higher",
        "own work more valuable", "personal attachment", "value own"
    ],
    "confirmation bias": [
        "selective evidence bias", "favor confirming information",
        "seek confirming evidence", "ignore contradicting",
        "favor existing beliefs", "confirm beliefs", "favor confirming"
    ],
    "anchoring bias": [
        "initial value bias", "rely on first information",
        "first piece of information", "anchor on initial",
        "stick to first impression", "initial reference point", "first information"
    ],
    "representative heuristic": [
        "representativeness bias", "judge by similarity", "similar to past",
        "based on similarity", "judge probability by similarity"
    ],
    
    # Technical concepts - enhanced for better detection
    "linear optimization": [
        "linear programming", "optimization", "mathematical optimization", 
        "lp method", "optimize", "constraints", "resource allocation",
        "mathematical optimization", "optimize under constraints", "linear programming"
    ],
    "monte carlo simulation": [
        "monte carlo", "simulation modeling", "statistical simulation", 
        "uncertainty simulation", "probabilistic simulation", "simulate",
        "scenarios", "thousands", "random sampling", "simulate uncertainty", "monte carlo"
    ],
    "sensitivity analysis": [
        "sensitivity testing", "what-if analysis", "parameter analysis",
        "change parameters", "different values", "affects outcome",
        "test different inputs", "parameter sensitivity", "what if"
    ],
    "regression": [
        "regression analysis", "statistical regression", "prediction model",
        "forecast", "historical", "trends", "future values",
        "predict based on history", "statistical prediction", "forecasting"
    ],
    "seasonal analysis": [
        "seasonal patterns", "seasonality", "cyclical analysis",
        "seasonality modeling", "repeating patterns", "cycles",
        "seasonal forecasting", "cyclical patterns", "seasonal"
    ],
    "integer optimization": [
        "discrete optimization", "integer programming", "discrete choices",
        "whole number optimization", "discrete variables",
        "integer variables", "discrete decision making", "discrete"
    ],
    "aggregate planning": [
        "demand-driven optimization", "balance supply demand", "supply demand",
        "aggregate planning", "demand planning", "supply planning"
    ],
    "analytical solver": [
        "solver add-on", "optimization tool", "solver tool", "analytical solver"
    ],
    
    # Strategic concepts - enhanced for better detection
    "porter's five forces": [
        "five forces analysis", "competitive", "industry",
        "competitiveness", "industry analysis", "competitive forces",
        "industry structure", "competitive analysis", "five forces"
    ],
    "cost leadership": [
        "low-cost strategy", "competitive edge", "lowest cost",
        "cost advantage", "price leadership", "low cost advantage",
        "cost competitive", "lowest price strategy", "low cost"
    ],
    "differentiation strategy": [
        "uniqueness strategy", "unique features", "differentiate",
        "product differentiation", "competitive advantage", "unique value",
        "stand out", "distinctive features", "differentiation"
    ],
    "portfolio management": [
        "strategic portfolio management", "business units",
        "balance portfolio", "investment portfolio", "manage portfolio",
        "portfolio balance", "business unit management", "portfolio"
    ],
    "value chain analysis": [
        "value chain", "chain analysis", "value analysis",
        "activity-based analysis", "value creation activities",
        "value activities", "chain of activities", "value chain"
    ],
    "swot analysis": [
        "swot", "strengths weaknesses", "opportunities threats",
        "strengths weaknesses opportunities threats", "swot analysis"
    ],
    "strategic framing": [
        "strategic analysis", "problem framing", "decision framing",
        "structure decision", "frame problem", "strategic framing"
    ],
    
    # Negotiation concepts - enhanced for better detection
    "batna": [
        "best alternative", "walk away option", "negotiation alternative",
        "reservation alternative", "best alternative to negotiated agreement",
        "best option if no deal", "alternative to agreement", "best alternative"
    ],
    "zopa": [
        "zone of agreement", "negotiation zone", "agreement zone",
        "bargaining zone", "possible agreement", "negotiation",
        "zone of possible agreement", "agreement range", "zone of agreement"
    ],
    "reservation point": [
        "walk away point", "minimum acceptable", "bottom line", "walk-away point",
        "minimum outcome", "least acceptable", "walk away", "reservation point"
    ],
    "integrative negotiation": [
        "win-win bargaining", "value creation", "collaborative negotiation",
        "mutual benefits", "win-win solutions", "create value",
        "collaborative approach", "mutual gains", "win-win"
    ],
    "game theory": [
        "strategic games", "payoff analysis", "competitive interactions",
        "strategic analysis", "competitive strategy", "strategic thinking",
        "competitive analysis", "strategic interactions", "game theory"
    ],
    "winner's curse": [
        "overpaying", "competitive bidding", "overcommitting",
        "bidding war", "auction", "competitive situation",
        "overbid", "competitive overpayment", "winner's curse"
    ],
    "investigative negotiation": [
        "investigative", "interest-based negotiation", "information gathering",
        "uncover interests", "underlying interests", "investigative negotiation"
    ],
    "negotiation term sheet": [
        "term sheet", "negotiation terms", "agreement terms", "deal sheet",
        "negotiation terms", "agreement terms", "term sheet"
    ]
}

def apply_enhanced_aliases_to_glossary():
    """Apply enhanced aliases to the current glossary"""
    print("🔧 APPLYING ENHANCED ALIASES TO GLOSSARY")
    print("=" * 60)
    
    # Read current glossary
    from query_engine import CONCEPT_GLOSSARY
    
    enhanced_glossary = CONCEPT_GLOSSARY.copy()
    changes_made = 0
    
    for concept, new_aliases in ENHANCED_ALIASES.items():
        if concept in enhanced_glossary:
            # Get existing aliases
            existing_aliases = enhanced_glossary[concept]["aliases"]
            
            # Combine existing and new aliases, remove duplicates
            all_aliases = existing_aliases + new_aliases
            unique_aliases = list(dict.fromkeys(all_aliases))
            
            # Update the glossary
            enhanced_glossary[concept]["aliases"] = unique_aliases
            
            original_count = len(existing_aliases)
            new_count = len(unique_aliases)
            
            if new_count > original_count:
                print(f"✅ {concept}: {original_count} → {new_count} aliases")
                changes_made += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"Enhanced {changes_made} concepts with improved aliases")
    
    return enhanced_glossary

def update_query_engine_with_enhanced_glossary(enhanced_glossary):
    """Update query_engine.py with the enhanced glossary"""
    print("\n📝 UPDATING QUERY_ENGINE.PY")
    print("=" * 60)
    
    # Read the current query_engine.py file
    with open('query_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the CONCEPT_GLOSSARY section
    start_marker = "# Comprehensive concept glossary with domain categorization, core concept flags, and aliases\nCONCEPT_GLOSSARY = {"
    end_marker = "}\n\n# Domain categorization for better concept filtering"
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print("❌ Could not find CONCEPT_GLOSSARY section in query_engine.py")
        return False
    
    # Generate the new glossary content
    new_glossary_content = "# Comprehensive concept glossary with domain categorization, core concept flags, and aliases\n# Enhanced with improved aliases for better concept detection\nCONCEPT_GLOSSARY = {\n"
    
    for concept, data in enhanced_glossary.items():
        definition = data["definition"]
        core = data["core"]
        aliases = data["aliases"]
        
        new_glossary_content += f'    "{concept}": {{"definition": "{definition}", "core": {core}, "aliases": {aliases}}},\n'
    
    new_glossary_content += "}\n\n# Domain categorization for better concept filtering"
    
    # Replace the glossary section
    new_content = content[:start_pos] + new_glossary_content + content[end_pos + len(end_marker):]
    
    # Write the updated file
    with open('query_engine.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Successfully updated query_engine.py with enhanced glossary")
    return True

def main():
    """Main function to apply enhanced aliases"""
    print("🚀 APPLYING ENHANCED ALIASES TO GLOSSARY")
    print("=" * 60)
    
    # Step 1: Apply enhanced aliases
    enhanced_glossary = apply_enhanced_aliases_to_glossary()
    
    # Step 2: Update query_engine.py
    success = update_query_engine_with_enhanced_glossary(enhanced_glossary)
    
    if success:
        print("\n✅ ENHANCEMENT COMPLETE!")
        print("The glossary has been enhanced with improved aliases for better concept detection.")
        print("Key improvements:")
        print("- Enhanced behavioral concept detection (status quo bias, escalation of commitment, etc.)")
        print("- Improved technical concept matching (linear optimization, monte carlo simulation, etc.)")
        print("- Better strategic concept recognition (porter's five forces, cost leadership, etc.)")
        print("- Enhanced negotiation concept detection (batna, zopa, game theory, etc.)")
    else:
        print("\n❌ ENHANCEMENT FAILED!")
        print("Could not update query_engine.py. Please check the file structure.")

if __name__ == "__main__":
    main() 