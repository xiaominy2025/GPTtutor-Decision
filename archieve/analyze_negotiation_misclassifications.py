#!/usr/bin/env python3
"""
Analyze which queries incorrectly identified negotiation when it shouldn't have been.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'Repeatability'))

from query_engine import hybrid_domain_detection, detect_domain_semantic, detect_course_concept_domains

def analyze_negotiation_misclassifications():
    """Analyze negotiation misclassifications."""
    
    # 20 test queries with expected domains
    test_queries = [
        # Query 1: (T + S) - NO NEGOTIATION
        ("A demand forecasting model shows high error variance across product categories. How should this influence strategic capacity planning?", 
         ['technical', 'strategic']),
        
        # Query 2: (H + S) - NO NEGOTIATION
        ("Managers consistently overweight short-term gains when evaluating long-term investment decisions. What cognitive bias explains this behavior?", 
         ['behavioral', 'strategic']),
        
        # Query 3: (N + S) - SHOULD HAVE NEGOTIATION
        ("During merger talks, one firm prioritizes speed, while the other values thorough due diligence. How should they structure the negotiation?", 
         ['negotiation', 'strategic']),
        
        # Query 4: (T + H) - NO NEGOTIATION
        ("A machine-learning hiring model favors candidates with certain resume patterns. How should we address potential bias in the algorithm?", 
         ['technical', 'behavioral']),
        
        # Query 5: (H + S) - NO NEGOTIATION
        ("A company refuses to shut down a failing project due to emotional attachment and sunk cost fallacy. What decision-making framework should they apply?", 
         ['behavioral', 'strategic']),
        
        # Query 6: (N + H) - SHOULD HAVE NEGOTIATION
        ("In labor negotiations, workers distrust management's data on company performance. How can trust be rebuilt while maintaining bargaining positions?", 
         ['negotiation', 'behavioral']),
        
        # Query 7: (T + N) - SHOULD HAVE NEGOTIATION
        ("A predictive model for supplier pricing shows high uncertainty. How should this affect contract negotiation strategies?", 
         ['technical', 'negotiation']),
        
        # Query 8: (S + T) - NO NEGOTIATION
        ("A company must decide between expanding capacity now or waiting for clearer market signals. What analytical framework should guide this strategic choice?", 
         ['strategic', 'technical']),
        
        # Query 9: (H + N) - SHOULD HAVE NEGOTIATION
        ("Team members resist changing their approach despite evidence that the current method is inefficient. How should a leader handle this resistance?", 
         ['behavioral', 'negotiation']),
        
        # Query 10: (S + N + H) - SHOULD HAVE NEGOTIATION
        ("In a joint venture negotiation, partners disagree on control rights and profit sharing. How should they balance individual interests with collective success?", 
         ['strategic', 'negotiation', 'behavioral']),
        
        # Query 11: (T + S + H) - NO NEGOTIATION
        ("A data-driven performance evaluation system creates competition among employees but reduces collaboration. How should management address this trade-off?", 
         ['technical', 'strategic', 'behavioral']),
        
        # Query 12: (T + S) - NO NEGOTIATION
        ("A simulation model suggests two different investment strategies have similar expected returns but different risk profiles. How should executives choose?", 
         ['technical', 'strategic']),
        
        # Query 13: (H + S) - NO NEGOTIATION
        ("Executives consistently ignore external advice when making strategic decisions, preferring to rely on internal expertise. What psychological factors drive this?", 
         ['behavioral', 'strategic']),
        
        # Query 14: (N + T + S) - SHOULD HAVE NEGOTIATION
        ("During contract negotiations, one party presents complex technical data that the other party struggles to interpret. How should this information asymmetry be managed?", 
         ['negotiation', 'technical', 'strategic']),
        
        # Query 15: (N + S) - SHOULD HAVE NEGOTIATION
        ("Two firms are negotiating a partnership but disagree on how to value each party's contributions. What framework should guide this valuation discussion?", 
         ['negotiation', 'strategic']),
        
        # Query 16: (H + T) - NO NEGOTIATION
        ("A team is overconfident about their forecasting model's accuracy despite poor historical performance. How should this cognitive bias be addressed?", 
         ['behavioral', 'technical']),
        
        # Query 17: (S + T + H) - NO NEGOTIATION
        ("A company must choose between investing in new technology or improving existing processes. How should they evaluate this strategic trade-off?", 
         ['strategic', 'technical', 'behavioral']),
        
        # Query 18: (N + H) - SHOULD HAVE NEGOTIATION
        ("In salary negotiations, an employee feels undervalued but fears appearing too aggressive. How should they approach this emotional challenge?", 
         ['negotiation', 'behavioral']),
        
        # Query 19: (N + T + S) - SHOULD HAVE NEGOTIATION
        ("During merger negotiations, both parties have different risk tolerance levels and technical capabilities. How should these differences be reconciled?", 
         ['negotiation', 'technical', 'strategic']),
        
        # Query 20: (N + S + H + T) - SHOULD HAVE NEGOTIATION
        ("A complex negotiation involves multiple stakeholders with conflicting interests, technical constraints, and behavioral biases. How should this be structured?", 
         ['negotiation', 'strategic', 'behavioral', 'technical'])
    ]
    
    print("🔍 ANALYZING NEGOTIATION MISCLASSIFICATIONS")
    print("=" * 50)
    print()
    
    false_positives = []  # Queries that identified negotiation when they shouldn't
    false_negatives = []  # Queries that should have identified negotiation but didn't
    true_positives = []   # Queries that correctly identified negotiation
    true_negatives = []   # Queries that correctly didn't identify negotiation
    
    for i, (query, expected) in enumerate(test_queries, 1):
        should_have_negotiation = 'negotiation' in expected
        hybrid_result = hybrid_domain_detection(query)
        hybrid_domains = list(hybrid_result.keys())
        identified_negotiation = 'negotiation' in hybrid_domains
        
        if should_have_negotiation and identified_negotiation:
            true_positives.append(i)
        elif should_have_negotiation and not identified_negotiation:
            false_negatives.append(i)
        elif not should_have_negotiation and identified_negotiation:
            false_positives.append(i)
        else:
            true_negatives.append(i)
    
    print("❌ FALSE POSITIVES (Negotiation identified when it shouldn't be):")
    print("-" * 60)
    if false_positives:
        for query_num in false_positives:
            query, expected = test_queries[query_num - 1]
            hybrid_result = hybrid_domain_detection(query)
            hybrid_domains = list(hybrid_result.keys())
            print(f"Query {query_num}: Expected {expected}, Got {hybrid_domains}")
            print(f"   Query: {query[:100]}...")
            print()
    else:
        print("✅ No false positives found!")
    print()
    
    print("❌ FALSE NEGATIVES (Negotiation should be identified but wasn't):")
    print("-" * 60)
    if false_negatives:
        for query_num in false_negatives:
            query, expected = test_queries[query_num - 1]
            hybrid_result = hybrid_domain_detection(query)
            hybrid_domains = list(hybrid_result.keys())
            print(f"Query {query_num}: Expected {expected}, Got {hybrid_domains}")
            print(f"   Query: {query[:100]}...")
            print()
    else:
        print("✅ No false negatives found!")
    print()
    
    print("✅ TRUE POSITIVES (Negotiation correctly identified):")
    print("-" * 60)
    if true_positives:
        for query_num in true_positives:
            query, expected = test_queries[query_num - 1]
            hybrid_result = hybrid_domain_detection(query)
            hybrid_domains = list(hybrid_result.keys())
            print(f"Query {query_num}: Expected {expected}, Got {hybrid_domains}")
            print(f"   Query: {query[:100]}...")
            print()
    else:
        print("❌ No true positives found!")
    print()
    
    print("📊 NEGOTIATION CLASSIFICATION SUMMARY:")
    print("-" * 40)
    print(f"False Positives: {len(false_positives)}")
    print(f"False Negatives: {len(false_negatives)}")
    print(f"True Positives:  {len(true_positives)}")
    print(f"True Negatives:  {len(true_negatives)}")
    print()
    
    if false_positives:
        precision = len(true_positives) / (len(true_positives) + len(false_positives)) * 100
        print(f"Precision: {precision:.1f}%")
    if false_negatives:
        recall = len(true_positives) / (len(true_positives) + len(false_negatives)) * 100
        print(f"Recall: {recall:.1f}%")

if __name__ == "__main__":
    analyze_negotiation_misclassifications()
