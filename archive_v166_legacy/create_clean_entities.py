#!/usr/bin/env python3
"""
Create Clean Entities JSON
Generates a permanent clean_entities.json file with only approved entities after stoplist filtering.
This replaces runtime stoplist filtering for production use.
"""

import json
import re
from typing import Dict, List, Any, Set
from difflib import SequenceMatcher

def load_stoplist() -> Set[str]:
    """Load the entity stoplist"""
    try:
        with open("entity_stoplist.json", "r", encoding="utf-8") as f:
            stoplist_data = json.load(f)
        return set(stoplist_data.get("all_stoplist_terms", []))
    except Exception as e:
        print(f"❌ Error loading stoplist: {e}")
        return set()

def extract_entities_from_clean_module() -> Dict[str, Any]:
    """Extract entities from the cleaned expanded_entities_clean.py module"""
    try:
        from expanded_entities_clean import EXPANDED_ENTITIES
        return EXPANDED_ENTITIES
    except ImportError as e:
        print(f"❌ Error importing cleaned entities: {e}")
        return {}

def extract_entity_terms(entities: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all entity terms with their categories and relevance scores"""
    clean_entities = []
    stoplist = load_stoplist()
    
    # Category mapping for better organization
    category_mapping = {
        "timeframe": "Timeframe",
        "stakeholders": "Stakeholder", 
        "criteria": "Criteria",
        "uncertainty": "Uncertainty",
        "complexity": "Complexity"
    }
    
    for category, subcategories in entities.items():
        category_name = category_mapping.get(category, "Uncategorized")
        
        for subcategory, config in subcategories.items():
            # Skip if subcategory is in stoplist
            if subcategory.lower() in stoplist:
                continue
                
            # Extract examples and patterns
            examples = config.get("examples", [])
            patterns = config.get("patterns", [])
            
            # Process examples
            for example in examples:
                # Check if example contains stoplisted terms
                example_words = re.findall(r'\b\w+\b', example.lower())
                if not any(word in stoplist for word in example_words):
                    clean_entities.append({
                        "entity": example,
                        "category": category_name,
                        "relevance": 0.85  # Default relevance for examples
                    })
            
            # Process patterns (extract key terms from regex patterns)
            for pattern in patterns:
                # Extract meaningful terms from regex patterns
                pattern_terms = re.findall(r'\b\w+\b', pattern.lower())
                for term in pattern_terms:
                    if term not in stoplist and len(term) > 2:  # Skip short terms
                        clean_entities.append({
                            "entity": term,
                            "category": category_name,
                            "relevance": 0.80  # Default relevance for pattern terms
                        })
    
    return clean_entities

def add_specific_entities() -> List[Dict[str, Any]]:
    """Add specific entities that are commonly used in decision-making contexts"""
    specific_entities = [
        # Timeframe entities
        {"entity": "immediate", "category": "Timeframe", "relevance": 0.90},
        {"entity": "urgent", "category": "Timeframe", "relevance": 0.92},
        {"entity": "short-term", "category": "Timeframe", "relevance": 0.88},
        {"entity": "medium-term", "category": "Timeframe", "relevance": 0.85},
        {"entity": "long-term", "category": "Timeframe", "relevance": 0.87},
        {"entity": "quarterly", "category": "Timeframe", "relevance": 0.83},
        {"entity": "annual", "category": "Timeframe", "relevance": 0.85},
        {"entity": "Q1", "category": "Timeframe", "relevance": 0.80},
        {"entity": "Q2", "category": "Timeframe", "relevance": 0.80},
        {"entity": "Q3", "category": "Timeframe", "relevance": 0.80},
        {"entity": "Q4", "category": "Timeframe", "relevance": 0.80},
        {"entity": "2025", "category": "Timeframe", "relevance": 0.85},
        {"entity": "2026", "category": "Timeframe", "relevance": 0.85},
        
        # Stakeholder entities
        {"entity": "employees", "category": "Stakeholder", "relevance": 0.90},
        {"entity": "customers", "category": "Stakeholder", "relevance": 0.92},
        {"entity": "investors", "category": "Stakeholder", "relevance": 0.88},
        {"entity": "suppliers", "category": "Stakeholder", "relevance": 0.85},
        {"entity": "regulators", "category": "Stakeholder", "relevance": 0.87},
        {"entity": "shareholders", "category": "Stakeholder", "relevance": 0.89},
        {"entity": "management", "category": "Stakeholder", "relevance": 0.86},
        {"entity": "team", "category": "Stakeholder", "relevance": 0.84},
        {"entity": "staff", "category": "Stakeholder", "relevance": 0.83},
        {"entity": "clients", "category": "Stakeholder", "relevance": 0.91},
        {"entity": "partners", "category": "Stakeholder", "relevance": 0.85},
        {"entity": "vendors", "category": "Stakeholder", "relevance": 0.84},
        
        # Financial criteria
        {"entity": "financial", "category": "Criteria", "relevance": 0.90},
        {"entity": "cost", "category": "Criteria", "relevance": 0.92},
        {"entity": "budget", "category": "Criteria", "relevance": 0.88},
        {"entity": "revenue", "category": "Criteria", "relevance": 0.89},
        {"entity": "profit", "category": "Criteria", "relevance": 0.91},
        {"entity": "ROI", "category": "Criteria", "relevance": 0.93},
        {"entity": "investment", "category": "Criteria", "relevance": 0.87},
        {"entity": "capital", "category": "Criteria", "relevance": 0.86},
        {"entity": "funding", "category": "Criteria", "relevance": 0.85},
        
        # Operational criteria
        {"entity": "operational", "category": "Criteria", "relevance": 0.88},
        {"entity": "efficiency", "category": "Criteria", "relevance": 0.90},
        {"entity": "productivity", "category": "Criteria", "relevance": 0.89},
        {"entity": "performance", "category": "Criteria", "relevance": 0.87},
        {"entity": "quality", "category": "Criteria", "relevance": 0.91},
        {"entity": "delivery", "category": "Criteria", "relevance": 0.84},
        
        # Risk criteria
        {"entity": "risk", "category": "Criteria", "relevance": 0.92},
        {"entity": "threat", "category": "Criteria", "relevance": 0.89},
        {"entity": "danger", "category": "Criteria", "relevance": 0.88},
        {"entity": "vulnerability", "category": "Criteria", "relevance": 0.86},
        {"entity": "exposure", "category": "Criteria", "relevance": 0.85},
        {"entity": "safety", "category": "Criteria", "relevance": 0.90},
        {"entity": "security", "category": "Criteria", "relevance": 0.91},
        
        # Career criteria
        {"entity": "salary", "category": "Criteria", "relevance": 0.88},
        {"entity": "compensation", "category": "Criteria", "relevance": 0.87},
        {"entity": "benefits", "category": "Criteria", "relevance": 0.86},
        {"entity": "career", "category": "Criteria", "relevance": 0.89},
        {"entity": "promotion", "category": "Criteria", "relevance": 0.85},
        {"entity": "advancement", "category": "Criteria", "relevance": 0.84},
        
        # Uncertainty levels
        {"entity": "high uncertainty", "category": "Uncertainty", "relevance": 0.92},
        {"entity": "unpredictable", "category": "Uncertainty", "relevance": 0.90},
        {"entity": "volatile", "category": "Uncertainty", "relevance": 0.89},
        {"entity": "medium uncertainty", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "moderate", "category": "Uncertainty", "relevance": 0.83},
        {"entity": "low uncertainty", "category": "Uncertainty", "relevance": 0.87},
        {"entity": "predictable", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "stable", "category": "Uncertainty", "relevance": 0.88},
        
        # Complexity levels
        {"entity": "high complexity", "category": "Complexity", "relevance": 0.91},
        {"entity": "complex", "category": "Complexity", "relevance": 0.89},
        {"entity": "complicated", "category": "Complexity", "relevance": 0.88},
        {"entity": "medium complexity", "category": "Complexity", "relevance": 0.84},
        {"entity": "manageable", "category": "Complexity", "relevance": 0.83},
        {"entity": "low complexity", "category": "Complexity", "relevance": 0.86},
        {"entity": "simple", "category": "Complexity", "relevance": 0.85},
        {"entity": "straightforward", "category": "Complexity", "relevance": 0.84},
        
        # Strategic terms (specific ones)
        {"entity": "competitive advantage", "category": "Criteria", "relevance": 0.93},
        {"entity": "market share", "category": "Criteria", "relevance": 0.90},
        {"entity": "brand", "category": "Criteria", "relevance": 0.87},
        {"entity": "reputation", "category": "Criteria", "relevance": 0.89},
        {"entity": "positioning", "category": "Criteria", "relevance": 0.86},
        
        # Specific time indicators
        {"entity": "ASAP", "category": "Timeframe", "relevance": 0.94},
        {"entity": "urgently", "category": "Timeframe", "relevance": 0.91},
        {"entity": "immediately", "category": "Timeframe", "relevance": 0.92},
        {"entity": "soon", "category": "Timeframe", "relevance": 0.85},
        {"entity": "now", "category": "Timeframe", "relevance": 0.88},
        {"entity": "today", "category": "Timeframe", "relevance": 0.86},
        {"entity": "this week", "category": "Timeframe", "relevance": 0.84},
        {"entity": "this month", "category": "Timeframe", "relevance": 0.83},
        {"entity": "next quarter", "category": "Timeframe", "relevance": 0.85},
        {"entity": "coming months", "category": "Timeframe", "relevance": 0.82},
        {"entity": "future", "category": "Timeframe", "relevance": 0.87},
        {"entity": "years", "category": "Timeframe", "relevance": 0.86},
        {"entity": "annual", "category": "Timeframe", "relevance": 0.85},
        {"entity": "yearly", "category": "Timeframe", "relevance": 0.84},
        
        # Specific stakeholder types
        {"entity": "workforce", "category": "Stakeholder", "relevance": 0.88},
        {"entity": "personnel", "category": "Stakeholder", "relevance": 0.85},
        {"entity": "colleagues", "category": "Stakeholder", "relevance": 0.84},
        {"entity": "users", "category": "Stakeholder", "relevance": 0.86},
        {"entity": "consumers", "category": "Stakeholder", "relevance": 0.89},
        {"entity": "buyers", "category": "Stakeholder", "relevance": 0.87},
        {"entity": "end users", "category": "Stakeholder", "relevance": 0.85},
        {"entity": "owners", "category": "Stakeholder", "relevance": 0.88},
        {"entity": "contractors", "category": "Stakeholder", "relevance": 0.83},
        {"entity": "providers", "category": "Stakeholder", "relevance": 0.84},
        {"entity": "authorities", "category": "Stakeholder", "relevance": 0.86},
        
        # Specific financial terms
        {"entity": "monetary", "category": "Criteria", "relevance": 0.88},
        {"entity": "expense", "category": "Criteria", "relevance": 0.89},
        {"entity": "earnings", "category": "Criteria", "relevance": 0.90},
        {"entity": "return", "category": "Criteria", "relevance": 0.87},
        {"entity": "money", "category": "Criteria", "relevance": 0.85},
        {"entity": "economic", "category": "Criteria", "relevance": 0.86},
        {"entity": "fiscal", "category": "Criteria", "relevance": 0.84},
        
        # Specific operational terms
        {"entity": "operations", "category": "Criteria", "relevance": 0.87},
        {"entity": "process", "category": "Criteria", "relevance": 0.86},
        {"entity": "workflow", "category": "Criteria", "relevance": 0.85},
        {"entity": "procedure", "category": "Criteria", "relevance": 0.84},
        {"entity": "system", "category": "Criteria", "relevance": 0.88},
        {"entity": "infrastructure", "category": "Criteria", "relevance": 0.86},
        {"entity": "service", "category": "Criteria", "relevance": 0.87},
        {"entity": "execution", "category": "Criteria", "relevance": 0.85},
        
        # Specific risk terms
        {"entity": "assessment", "category": "Criteria", "relevance": 0.88},
        {"entity": "management", "category": "Criteria", "relevance": 0.87},
        {"entity": "mitigation", "category": "Criteria", "relevance": 0.86},
        {"entity": "prevention", "category": "Criteria", "relevance": 0.85},
        {"entity": "protection", "category": "Criteria", "relevance": 0.89},
        {"entity": "safeguard", "category": "Criteria", "relevance": 0.84},
        
        # Specific career terms
        {"entity": "pay", "category": "Criteria", "relevance": 0.86},
        {"entity": "income", "category": "Criteria", "relevance": 0.87},
        {"entity": "growth", "category": "Criteria", "relevance": 0.88},
        {"entity": "development", "category": "Criteria", "relevance": 0.87},
        {"entity": "transition", "category": "Criteria", "relevance": 0.85},
        {"entity": "balance", "category": "Criteria", "relevance": 0.86},
        {"entity": "satisfaction", "category": "Criteria", "relevance": 0.85},
        {"entity": "culture", "category": "Criteria", "relevance": 0.84},
        {"entity": "environment", "category": "Criteria", "relevance": 0.85},
        {"entity": "dynamics", "category": "Criteria", "relevance": 0.83},
        {"entity": "security", "category": "Criteria", "relevance": 0.88},
        {"entity": "stability", "category": "Criteria", "relevance": 0.86},
        {"entity": "prospects", "category": "Criteria", "relevance": 0.85},
        {"entity": "opportunities", "category": "Criteria", "relevance": 0.87},
        {"entity": "training", "category": "Criteria", "relevance": 0.84},
        
        # Specific uncertainty terms
        {"entity": "unknown", "category": "Uncertainty", "relevance": 0.89},
        {"entity": "unclear", "category": "Uncertainty", "relevance": 0.87},
        {"entity": "ambiguous", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "vague", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "indefinite", "category": "Uncertainty", "relevance": 0.84},
        {"entity": "change", "category": "Uncertainty", "relevance": 0.88},
        {"entity": "dynamic", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "turbulent", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "unstable", "category": "Uncertainty", "relevance": 0.87},
        {"entity": "chaotic", "category": "Uncertainty", "relevance": 0.88},
        {"entity": "mixed", "category": "Uncertainty", "relevance": 0.83},
        {"entity": "varied", "category": "Uncertainty", "relevance": 0.84},
        {"entity": "diverse", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "evolving", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "changing", "category": "Uncertainty", "relevance": 0.87},
        {"entity": "developing", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "known", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "established", "category": "Uncertainty", "relevance": 0.87},
        {"entity": "proven", "category": "Uncertainty", "relevance": 0.88},
        {"entity": "reliable", "category": "Uncertainty", "relevance": 0.89},
        {"entity": "consistent", "category": "Uncertainty", "relevance": 0.86},
        {"entity": "steady", "category": "Uncertainty", "relevance": 0.85},
        {"entity": "clear", "category": "Uncertainty", "relevance": 0.87},
        
        # Specific complexity terms
        {"entity": "intricate", "category": "Complexity", "relevance": 0.88},
        {"entity": "sophisticated", "category": "Complexity", "relevance": 0.87},
        {"entity": "factors", "category": "Complexity", "relevance": 0.86},
        {"entity": "variables", "category": "Complexity", "relevance": 0.85},
        {"entity": "interconnected", "category": "Complexity", "relevance": 0.87},
        {"entity": "interdependent", "category": "Complexity", "relevance": 0.86},
        {"entity": "technical", "category": "Complexity", "relevance": 0.88},
        {"entity": "advanced", "category": "Complexity", "relevance": 0.87},
        {"entity": "specialized", "category": "Complexity", "relevance": 0.86},
        {"entity": "expert", "category": "Complexity", "relevance": 0.89},
        {"entity": "moderate", "category": "Complexity", "relevance": 0.84},
        {"entity": "manageable", "category": "Complexity", "relevance": 0.85},
        {"entity": "considerations", "category": "Complexity", "relevance": 0.86},
        {"entity": "aspects", "category": "Complexity", "relevance": 0.85},
        {"entity": "standard", "category": "Complexity", "relevance": 0.84},
        {"entity": "typical", "category": "Complexity", "relevance": 0.83},
        {"entity": "common", "category": "Complexity", "relevance": 0.84},
        {"entity": "usual", "category": "Complexity", "relevance": 0.83},
        {"entity": "elementary", "category": "Complexity", "relevance": 0.82},
        {"entity": "limited", "category": "Complexity", "relevance": 0.84},
        {"entity": "minimal", "category": "Complexity", "relevance": 0.83},
        {"entity": "basic", "category": "Complexity", "relevance": 0.82},
        {"entity": "obvious", "category": "Complexity", "relevance": 0.85},
        {"entity": "direct", "category": "Complexity", "relevance": 0.84}
    ]
    
    return specific_entities

def remove_duplicates_and_validate(entities: List[Dict[str, Any]], stoplist: Set[str]) -> List[Dict[str, Any]]:
    """Remove duplicates and validate that no entities are in the stoplist"""
    seen_entities = set()
    clean_entities = []
    
    for entity in entities:
        entity_text = entity["entity"].lower()
        
        # Skip if entity is in stoplist
        if entity_text in stoplist:
            continue
            
        # Skip if we've seen this entity before
        if entity_text in seen_entities:
            continue
            
        # Skip if entity is too short or generic
        if len(entity_text) < 3:
            continue
            
        seen_entities.add(entity_text)
        clean_entities.append(entity)
    
    return clean_entities

def main():
    """Main function to create clean_entities.json"""
    print("🧹 Creating Clean Entities JSON")
    print("=" * 50)
    
    # Load stoplist
    print("📥 Loading stoplist...")
    stoplist = load_stoplist()
    print(f"✅ Loaded {len(stoplist)} stoplist terms")
    
    # Extract entities from clean module
    print("📥 Extracting entities from clean module...")
    entities = extract_entities_from_clean_module()
    if not entities:
        print("❌ Failed to extract entities")
        return
    
    # Extract entity terms
    print("🔍 Extracting entity terms...")
    extracted_entities = extract_entity_terms(entities)
    print(f"✅ Extracted {len(extracted_entities)} entities from module")
    
    # Add specific entities
    print("➕ Adding specific entities...")
    specific_entities = add_specific_entities()
    print(f"✅ Added {len(specific_entities)} specific entities")
    
    # Combine all entities
    all_entities = extracted_entities + specific_entities
    
    # Remove duplicates and validate
    print("🧹 Removing duplicates and validating...")
    clean_entities = remove_duplicates_and_validate(all_entities, stoplist)
    print(f"✅ Final clean entities: {len(clean_entities)}")
    
    # Sort by relevance (descending)
    clean_entities.sort(key=lambda x: x["relevance"], reverse=True)
    
    # Save to file
    print("💾 Saving clean_entities.json...")
    with open("clean_entities.json", "w", encoding="utf-8") as f:
        json.dump(clean_entities, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n📋 Clean Entities Summary")
    print("=" * 50)
    print(f"✅ Total clean entities: {len(clean_entities)}")
    
    # Show some examples
    print(f"\n🔍 Sample entities:")
    for i, entity in enumerate(clean_entities[:10]):
        print(f"  {i+1}. {entity['entity']} ({entity['category']}) - {entity['relevance']:.2f}")
    
    # Category breakdown
    categories = {}
    for entity in clean_entities:
        cat = entity["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n📊 Category breakdown:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")
    
    print(f"\n📁 Saved to: clean_entities.json")

if __name__ == "__main__":
    main() 