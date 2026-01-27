#!/usr/bin/env python3
"""
Debug script to see exactly what keywords are being detected for each domain
"""

import sys
import os
from query_engine import detect_course_concept_domains

def debug_domain_keywords():
    """Debug domain keyword detection"""
    
    test_query = "How shall I deal with unfair critiques from my manager?"
    query_lower = test_query.lower()
    
    print("🔍 Debugging Domain Keyword Detection")
    print("=" * 50)
    print(f"Query: {test_query}")
    print(f"Query (lower): {query_lower}")
    
    # Check behavioral keywords
    behavioral_keywords = [
        'team', 'teams', 'conflict', 'conflicts', 'value', 'values', 'behavior', 'behaviour',
        'psychology', 'psychological', 'bias', 'biases', 'cognitive', 'cognition',
        'judgment', 'judgement', 'leadership', 'personality', 'personalities',
        'motivation', 'motivational', 'emotion', 'emotional', 'human', 'people',
        'individual', 'group', 'social', 'interpersonal', 'communication',
        'behave', 'behaving', 'behaved', 'psychologic', 'cognitively', 'judge', 'judging',
        'lead', 'leading', 'led', 'motivate', 'motivating', 'motivated', 'feel', 'feeling',
        'felt', 'interact', 'interacting', 'interacted', 'communicate', 'communicating',
        'manager', 'managers', 'boss', 'supervisor', 'supervisors', 'colleague', 'colleagues',
        'workplace', 'office', 'professional', 'professionally', 'work', 'working',
        'critique', 'critiques', 'criticism', 'criticisms', 'feedback', 'unfair', 'fair',
        'approach', 'approaching', 'situation', 'circumstance', 'circumstances',
        'relationship', 'relationships', 'interpersonal', 'communication', 'communicate',
        'response', 'respond', 'responding', 'react', 'reacting', 'reaction', 'reactions',
        'budget', 'budgeting', 'budgeted', 'salary', 'salaries', 'expense', 'expenses', 'spending', 'spend', 'spent',
        'money', 'financial', 'finance', 'cost', 'costs', 'price', 'prices', 'payment', 'payments',
        'income', 'revenue', 'profit', 'loss', 'saving', 'savings', 'save', 'saved',
        'investment', 'invest', 'investing', 'invested', 'wealth', 'wealthy', 'asset', 'assets',
        'debt', 'credit', 'loan', 'loans', 'mortgage', 'rent', 'rental', 'utility', 'utilities',
        'grocery', 'groceries', 'entertainment', 'transportation', 'healthcare', 'insurance'
    ]
    
    # Check negotiation keywords
    negotiation_keywords = [
        'negotiate', 'negotiation', 'negotiating', 'negotiated', 'negotiator', 'negotiators',
        'agreement', 'agree', 'agreeing', 'agreed', 'disagree', 'disagreeing', 'disagreed',
        'bargain', 'bargaining', 'bargained', 'bargaining strategy', 'bargaining strategies', 
        'negotiation strategy', 'negotiation strategies', 'contract', 'contracts', 'contracting', 'contracted', 
        'settlement', 'settle', 'settling', 'settled', 'compromise', 'compromising', 'compromised',
        'proposal', 'proposals', 'propose', 'proposing', 'proposed',
        'counteroffer', 'counteroffers', 'counter-offer', 'counter-offers',
        'terms', 'term', 'condition', 'conditions', 'concession', 'concessions',
        'deadlock', 'impasse', 'deadlocked', 'win-win', 'win win', 'zero-sum', 'zero sum',
        'package', 'packages', 'offer', 'offers', 'offering', 'offered', 'deal', 'deals',
        'salary', 'salaries', 'compensation', 'benefits', 'bonus', 'bonuses', 'raise', 'raises'
    ]
    
    print("\n📋 Behavioral Keywords Found:")
    behavioral_found = []
    for keyword in behavioral_keywords:
        if keyword in query_lower:
            behavioral_found.append(keyword)
            print(f"  ✅ {keyword}")
    
    print(f"\n📊 Behavioral Score: {len(behavioral_found)}")
    
    print("\n📋 Negotiation Keywords Found:")
    negotiation_found = []
    for keyword in negotiation_keywords:
        if keyword in query_lower:
            negotiation_found.append(keyword)
            print(f"  ✅ {keyword}")
    
    print(f"\n📊 Negotiation Score: {len(negotiation_found)}")
    
    # Check final domain detection
    domains = detect_course_concept_domains(test_query)
    print(f"\n🎯 Final Domain Detection:")
    for domain, score in domains.items():
        print(f"  {domain}: {score:.3f}")
    
    detected_domain = max(domains, key=domains.get) if domains else 'general'
    print(f"\n🏆 Detected Domain: {detected_domain}")

if __name__ == "__main__":
    debug_domain_keywords() 