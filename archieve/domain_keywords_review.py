#!/usr/bin/env python3
"""
Extract and display all keywords for each domain from the query engine.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'Repeatability'))

def extract_keywords_from_file():
    """Extract keywords from the query_engine.py file."""
    
    keywords = {
        'behavioral': {'strong': [], 'modest': [], 'weak': []},
        'technical': {'strong': [], 'modest': [], 'weak': []},
        'strategic': {'strong': [], 'modest': [], 'weak': []},
        'negotiation': {'strong': [], 'modest': [], 'weak': []}
    }
    
    try:
        with open('Repeatability/query_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract behavioral keywords
        behav_start = content.find("behavioral_keywords = {")
        behav_end = content.find("}", behav_start) + 1
        behav_section = content[behav_start:behav_end]
        
        # Extract technical keywords
        tech_start = content.find("technical_keywords = {")
        tech_end = content.find("}", tech_start) + 1
        tech_section = content[tech_start:tech_end]
        
        # Extract strategic keywords
        strat_start = content.find("strategic_keywords = {")
        strat_end = content.find("}", strat_start) + 1
        strat_section = content[strat_start:strat_end]
        
        # Extract negotiation keywords
        neg_start = content.find("negotiation_keywords = {")
        neg_end = content.find("}", neg_start) + 1
        neg_section = content[neg_start:neg_end]
        
        # Parse behavioral keywords
        for weight in ['strong', 'modest', 'weak']:
            start = behav_section.find(f"'{weight}': [")
            if start != -1:
                start = behav_section.find('[', start)
                end = behav_section.find(']', start)
                if start != -1 and end != -1:
                    keywords_list = behav_section[start+1:end]
                    # Extract individual keywords
                    import re
                    matches = re.findall(r"'([^']+)'", keywords_list)
                    keywords['behavioral'][weight] = matches
        
        # Parse technical keywords
        for weight in ['strong', 'modest', 'weak']:
            start = tech_section.find(f"'{weight}': [")
            if start != -1:
                start = tech_section.find('[', start)
                end = tech_section.find(']', start)
                if start != -1 and end != -1:
                    keywords_list = tech_section[start+1:end]
                    matches = re.findall(r"'([^']+)'", keywords_list)
                    keywords['technical'][weight] = matches
        
        # Parse strategic keywords
        for weight in ['strong', 'modest', 'weak']:
            start = strat_section.find(f"'{weight}': [")
            if start != -1:
                start = strat_section.find('[', start)
                end = strat_section.find(']', start)
                if start != -1 and end != -1:
                    keywords_list = strat_section[start+1:end]
                    matches = re.findall(r"'([^']+)'", keywords_list)
                    keywords['strategic'][weight] = matches
        
        # Parse negotiation keywords
        for weight in ['strong', 'modest', 'weak']:
            start = neg_section.find(f"'{weight}': [")
            if start != -1:
                start = neg_section.find('[', start)
                end = neg_section.find(']', start)
                if start != -1 and end != -1:
                    keywords_list = neg_section[start+1:end]
                    matches = re.findall(r"'([^']+)'", keywords_list)
                    keywords['negotiation'][weight] = matches
                    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    return keywords

def display_keywords(keywords):
    """Display all keywords in a formatted way."""
    
    print("🔍 DOMAIN KEYWORDS REVIEW")
    print("=" * 80)
    print()
    
    for domain, weights in keywords.items():
        print(f"📋 {domain.upper()} DOMAIN")
        print("-" * 40)
        
        total_keywords = 0
        for weight, keyword_list in weights.items():
            print(f"\n🔸 {weight.upper()} keywords (weight = {3 if weight == 'strong' else 2 if weight == 'modest' else 1}):")
            print(f"   Count: {len(keyword_list)}")
            if keyword_list:
                # Display in columns for better readability
                for i in range(0, len(keyword_list), 4):
                    chunk = keyword_list[i:i+4]
                    print(f"   {', '.join(chunk)}")
            else:
                print("   (none)")
            total_keywords += len(keyword_list)
        
        print(f"\n📊 Total {domain} keywords: {total_keywords}")
        print("=" * 80)
        print()

def analyze_overlaps(keywords):
    """Analyze overlaps between domains."""
    
    print("🔍 KEYWORD OVERLAP ANALYSIS")
    print("=" * 80)
    print()
    
    # Create flat lists for each domain
    domain_lists = {}
    for domain, weights in keywords.items():
        all_keywords = []
        for weight, keyword_list in weights.items():
            all_keywords.extend(keyword_list)
        domain_lists[domain] = set(all_keywords)
    
    # Check overlaps
    domains = list(domain_lists.keys())
    for i, domain1 in enumerate(domains):
        for domain2 in domains[i+1:]:
            overlap = domain_lists[domain1] & domain_lists[domain2]
            if overlap:
                print(f"🔄 {domain1.upper()} ↔ {domain2.upper()} overlap ({len(overlap)} keywords):")
                print(f"   {', '.join(sorted(overlap))}")
                print()

def main():
    """Main function."""
    
    keywords = extract_keywords_from_file()
    if keywords:
        display_keywords(keywords)
        analyze_overlaps(keywords)
    else:
        print("❌ Failed to extract keywords from file")

if __name__ == "__main__":
    main()
