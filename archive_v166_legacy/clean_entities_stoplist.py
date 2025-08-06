#!/usr/bin/env python3
"""
Clean Entities Stoplist Generator
Analyzes current entities against domain and field lists to create a stoplist
for generic terms that should be excluded from entity enrichment.
"""

import json
import re
from typing import Dict, List, Set, Any
from difflib import SequenceMatcher

# Load current entities from expanded_entities.py
def load_current_entities() -> Dict[str, Any]:
    """Load current entities from expanded_entities.py"""
    try:
        from expanded_entities import EXPANDED_ENTITIES
        return EXPANDED_ENTITIES
    except ImportError:
        print("❌ Error: Could not import EXPANDED_ENTITIES from expanded_entities.py")
        return {}

def load_domain_field_lists() -> Dict[str, List[str]]:
    """Load domain and field lists from course configuration"""
    try:
        with open("courses/decision/course_config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        domain_keywords = []
        for domain_name, domain_config in config.get("domains", {}).items():
            domain_keywords.extend(domain_config.get("keywords", []))
        
        application_fields = config.get("application_fields", [])
        
        return {
            "domain_keywords": domain_keywords,
            "application_fields": application_fields
        }
    except Exception as e:
        print(f"❌ Error loading course config: {e}")
        return {"domain_keywords": [], "application_fields": []}

def extract_entity_terms(entities: Dict[str, Any]) -> Set[str]:
    """Extract all entity terms from the expanded entities"""
    terms = set()
    
    for category, subcategories in entities.items():
        for subcategory, config in subcategories.items():
            # Add examples
            if "examples" in config:
                for example in config["examples"]:
                    # Split examples into individual terms
                    example_terms = re.findall(r'\b\w+\b', example.lower())
                    terms.update(example_terms)
            
            # Add patterns (extract words from regex patterns)
            if "patterns" in config:
                for pattern in config["patterns"]:
                    # Extract word boundaries from regex patterns
                    pattern_words = re.findall(r'\b\w+\b', pattern.lower())
                    terms.update(pattern_words)
    
    return terms

def find_similar_terms(terms: Set[str], reference_list: List[str], similarity_threshold: float = 0.8) -> List[tuple]:
    """Find terms that are similar to reference list items"""
    similar_terms = []
    
    for term in terms:
        for ref_term in reference_list:
            similarity = SequenceMatcher(None, term.lower(), ref_term.lower()).ratio()
            if similarity >= similarity_threshold:
                similar_terms.append((term, ref_term, similarity))
    
    return similar_terms

def create_stoplist(entities: Dict[str, Any], domain_lists: Dict[str, List[str]]) -> Dict[str, Any]:
    """Create a comprehensive stoplist for generic entities"""
    
    # Extract all entity terms
    entity_terms = extract_entity_terms(entities)
    print(f"📊 Found {len(entity_terms)} unique entity terms")
    
    # Define base generic terms
    base_generic_terms = [
        "decision", "management", "planning", "budget", "business", "leadership", "organization",
        "strategy", "analysis", "assessment", "evaluation", "consideration", "approach",
        "process", "system", "method", "technique", "framework", "model", "tool",
        "factor", "element", "aspect", "component", "dimension", "perspective",
        "context", "situation", "scenario", "circumstance", "condition", "environment",
        "objective", "goal", "target", "aim", "purpose", "intention", "outcome",
        "result", "consequence", "impact", "effect", "influence", "benefit", "advantage",
        "risk", "threat", "challenge", "problem", "issue", "concern", "matter",
        "option", "choice", "alternative", "possibility", "opportunity", "potential",
        "time", "period", "duration", "timeline", "schedule", "deadline", "timing",
        "level", "degree", "extent", "scope", "range", "scale", "magnitude",
        "type", "category", "classification", "group", "class", "kind", "sort"
    ]
    
    # Find similar terms to domain keywords
    domain_similar = find_similar_terms(entity_terms, domain_lists["domain_keywords"])
    
    # Find similar terms to application fields
    field_similar = find_similar_terms(entity_terms, domain_lists["application_fields"])
    
    # Combine all stoplist terms
    stoplist_terms = set(base_generic_terms)
    
    # Add domain-similar terms
    for term, ref_term, similarity in domain_similar:
        stoplist_terms.add(term)
    
    # Add field-similar terms
    for term, ref_term, similarity in field_similar:
        stoplist_terms.add(term)
    
    # Create stoplist structure
    stoplist = {
        "version": "1.0",
        "description": "Generic terms to exclude from entity enrichment",
        "base_generic_terms": base_generic_terms,
        "domain_similar_terms": [term for term, _, _ in domain_similar],
        "field_similar_terms": [term for term, _, _ in field_similar],
        "all_stoplist_terms": sorted(list(stoplist_terms)),
        "similarity_matches": {
            "domain_matches": [{"term": term, "reference": ref, "similarity": sim} 
                              for term, ref, sim in domain_similar],
            "field_matches": [{"term": term, "reference": ref, "similarity": sim} 
                             for term, ref, sim in field_similar]
        }
    }
    
    return stoplist

def analyze_entity_coverage(entities: Dict[str, Any], stoplist: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how many entities would be filtered by the stoplist"""
    
    entity_terms = extract_entity_terms(entities)
    stoplist_terms = set(stoplist["all_stoplist_terms"])
    
    # Count entities that would be filtered
    filtered_terms = entity_terms.intersection(stoplist_terms)
    remaining_terms = entity_terms - stoplist_terms
    
    analysis = {
        "total_entity_terms": len(entity_terms),
        "filtered_terms": len(filtered_terms),
        "remaining_terms": len(remaining_terms),
        "filter_percentage": (len(filtered_terms) / len(entity_terms)) * 100 if entity_terms else 0,
        "filtered_terms_list": sorted(list(filtered_terms)),
        "remaining_terms_list": sorted(list(remaining_terms))
    }
    
    return analysis

def main():
    """Main function to generate the stoplist"""
    print("🧹 Cleaning Entities - Stoplist Generation")
    print("=" * 50)
    
    # Load current entities
    print("📥 Loading current entities...")
    entities = load_current_entities()
    if not entities:
        print("❌ Failed to load entities")
        return
    
    # Load domain and field lists
    print("📥 Loading domain and field lists...")
    domain_lists = load_domain_field_lists()
    
    # Create stoplist
    print("🔍 Creating stoplist...")
    stoplist = create_stoplist(entities, domain_lists)
    
    # Analyze coverage
    print("📊 Analyzing entity coverage...")
    analysis = analyze_entity_coverage(entities, stoplist)
    
    # Save stoplist
    print("💾 Saving stoplist...")
    with open("entity_stoplist.json", "w", encoding="utf-8") as f:
        json.dump(stoplist, f, indent=2, ensure_ascii=False)
    
    # Save analysis
    with open("entity_analysis.json", "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n📋 Stoplist Generation Summary")
    print("=" * 50)
    print(f"✅ Total entity terms: {analysis['total_entity_terms']}")
    print(f"🚫 Terms to filter: {analysis['filtered_terms']} ({analysis['filter_percentage']:.1f}%)")
    print(f"✅ Remaining terms: {analysis['remaining_terms']}")
    print(f"📁 Stoplist saved to: entity_stoplist.json")
    print(f"📊 Analysis saved to: entity_analysis.json")
    
    # Show some examples
    print(f"\n🔍 Sample filtered terms: {', '.join(analysis['filtered_terms_list'][:10])}")
    print(f"✅ Sample remaining terms: {', '.join(analysis['remaining_terms_list'][:10])}")

if __name__ == "__main__":
    main() 