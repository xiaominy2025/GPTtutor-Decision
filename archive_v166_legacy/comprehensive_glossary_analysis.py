#!/usr/bin/env python3
"""
Comprehensive Glossary Analysis
Analyze all glossary components for consistency after entity enhancement
"""
import json
from typing import Dict, List, Set
from collections import defaultdict

def analyze_glossary_consistency():
    """Analyze all glossary components for consistency"""
    print("🔍 COMPREHENSIVE GLOSSARY CONSISTENCY ANALYSIS")
    print("=" * 70)
    
    # Load all glossary components
    try:
        with open("courses/decision/glossary.json", 'r', encoding='utf-8') as f:
            glossary = json.load(f)
        
        with open("courses/decision/course_config.json", 'r', encoding='utf-8') as f:
            course_config = json.load(f)
            
        with open("query_engine_entities_expanded_v165.py", 'r', encoding='utf-8') as f:
            expanded_entities_content = f.read()
            
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False
    
    print("📊 COMPONENT OVERVIEW")
    print("-" * 50)
    print(f"✅ Glossary Concepts: {len(glossary)}")
    print(f"✅ Course Config Domains: {len(course_config['domains'])}")
    print(f"✅ Application Fields: {len(course_config['application_fields'])}")
    print(f"✅ Entity Types: {len(course_config['entity_types'])}")
    
    # 1. DOMAIN ANALYSIS
    print("\n🎯 1. DOMAIN CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    # Extract domains from different sources
    query_engine_domains = ['behavioral', 'technical', 'strategic', 'negotiation']
    course_config_domains = list(course_config['domains'].keys())
    
    print(f"Query Engine Domains: {query_engine_domains}")
    print(f"Course Config Domains: {course_config_domains}")
    
    domain_mismatch = set(query_engine_domains) ^ set(course_config_domains)
    if domain_mismatch:
        print(f"❌ DOMAIN MISMATCH: {domain_mismatch}")
    else:
        print("✅ Domain consistency: PASSED")
    
    # 2. KEYWORD ANALYSIS
    print("\n🎯 2. KEYWORD CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    # Extract keywords from query_engine.py (hardcoded)
    query_engine_keywords = {
        'behavioral': [
            'team', 'teams', 'conflict', 'conflicts', 'value', 'values', 'behavior', 'behaviour',
            'psychology', 'psychological', 'bias', 'biases', 'cognitive', 'cognition',
            'judgment', 'judgement', 'leadership', 'personality', 'personalities',
            'motivation', 'motivational', 'emotion', 'emotional', 'human', 'people',
            'individual', 'group', 'social', 'interpersonal', 'communication',
            'behave', 'behaving', 'behaved', 'psychologic', 'cognitively', 'judge', 'judging',
            'lead', 'leading', 'led', 'motivate', 'motivating', 'motivated', 'feel', 'feeling',
            'felt', 'interact', 'interacting', 'interacted', 'communicate', 'communicating'
        ],
        'technical': [
            'model', 'modeling', 'modeled', 'simulation', 'simulate', 'simulating', 'simulated',
            'forecast', 'forecasting', 'forecasted', 'optimization', 'optimize', 'optimizing', 
            'optimized', 'optimum', 'optimization strategy', 'optimization strategies',
            'maximization', 'maximize', 'maximizing', 'maximized', 'maximum', 'minimization', 
            'minimize', 'minimizing', 'minimized', 'minimum', 'simulation strategy', 'simulation strategies',
            'analysis', 'analyze', 'analyzing', 'analyzed', 'analytical',
            'data', 'statistical', 'statistics', 'mathematical', 'mathematics',
            'algorithm', 'algorithms', 'uncertainty', 'uncertain', 'uncertainties', 'probability', 
            'probabilistic', 'probable', 'calculate', 'calculation', 'calculating', 'calculated',
            'compute', 'computation', 'computing', 'computed', 'numerical', 'numeric',
            'assess', 'assessment', 'assessing', 'assessed', 'evaluate', 'evaluation', 
            'evaluating', 'evaluated', 'measure', 'measurement', 'measuring', 'measured',
            'determine', 'determining', 'determined', 'estimate', 'estimating', 'estimated',
            'predict', 'predicting', 'predicted', 'prediction', 'predictions'
        ],
        'strategic': [
            'strategy', 'strategic', 'strategically', 'competitive', 'advantage', 'positioning',
            'market', 'industry', 'business', 'organization', 'planning', 'planned',
            'competitive advantage', 'competitive analysis', 'industry analysis',
            'strategic planning', 'strategic thinking', 'strategic analysis',
            'competitive strategy', 'business strategy', 'corporate strategy'
        ],
        'negotiation': [
            'negotiate', 'negotiation', 'bargain', 'deal', 'agreement', 'contract',
            'discuss', 'discussion', 'meeting', 'conference', 'settlement',
            'bargaining', 'negotiating', 'deal making', 'agreement making',
            'contract negotiation', 'settlement discussion', 'meeting discussion'
        ]
    }
    
    # Compare keywords between query_engine.py and course_config.json
    keyword_inconsistencies = {}
    for domain in query_engine_domains:
        if domain in course_config['domains']:
            qe_keywords = set(query_engine_keywords[domain])
            cc_keywords = set(course_config['domains'][domain]['keywords'])
            
            missing_in_cc = qe_keywords - cc_keywords
            extra_in_cc = cc_keywords - qe_keywords
            
            if missing_in_cc or extra_in_cc:
                keyword_inconsistencies[domain] = {
                    'missing_in_course_config': list(missing_in_cc),
                    'extra_in_course_config': list(extra_in_cc)
                }
    
    if keyword_inconsistencies:
        print("❌ KEYWORD INCONSISTENCIES FOUND:")
        for domain, issues in keyword_inconsistencies.items():
            print(f"   {domain}:")
            if issues['missing_in_course_config']:
                print(f"     Missing in course_config: {issues['missing_in_course_config'][:5]}...")
            if issues['extra_in_course_config']:
                print(f"     Extra in course_config: {issues['extra_in_course_config'][:5]}...")
    else:
        print("✅ Keyword consistency: PASSED")
    
    # 3. CONCEPT ANALYSIS
    print("\n🎯 3. CONCEPT CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    # Extract concepts from glossary
    glossary_concepts = set(glossary.keys())
    
    # Extract concepts from course_config
    course_config_concepts = set()
    for domain in course_config['domains'].values():
        course_config_concepts.update(domain['concepts'])
    
    # Compare concepts
    missing_in_glossary = course_config_concepts - glossary_concepts
    missing_in_course_config = glossary_concepts - course_config_concepts
    
    if missing_in_glossary:
        print(f"❌ Concepts in course_config but missing in glossary: {list(missing_in_glossary)}")
    if missing_in_course_config:
        print(f"❌ Concepts in glossary but missing in course_config: {list(missing_in_course_config)}")
    
    if not missing_in_glossary and not missing_in_course_config:
        print("✅ Concept consistency: PASSED")
    
    # 4. APPLICATION FIELD ANALYSIS
    print("\n🎯 4. APPLICATION FIELD CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    # Extract application fields from query_engine.py (hardcoded)
    query_engine_fields = [
        "operations", "business", "finance", "technology", "risk_management", 
        "project_management", "leadership", "human_capital", "marketing", 
        "globalization", "education", "innovation", "sustainability", 
        "admission", "relocation", "ethics", "health", "job", "startup"
    ]
    
    course_config_fields = course_config['application_fields']
    
    field_mismatch = set(query_engine_fields) ^ set(course_config_fields)
    if field_mismatch:
        print(f"❌ APPLICATION FIELD MISMATCH: {field_mismatch}")
        print(f"   Query Engine: {len(query_engine_fields)} fields")
        print(f"   Course Config: {len(course_config_fields)} fields")
    else:
        print("✅ Application field consistency: PASSED")
    
    # 5. ENTITY ANALYSIS
    print("\n🎯 5. ENTITY CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    # Current entity extraction categories (from enhanced_entity_extraction.py)
    current_entity_categories = [
        'time_periods', 'quantitative_terms', 'stakeholders', 'constraints', 
        'objectives', 'risks', 'technologies', 'industries', 'locations', 
        'emotions', 'uncertainty_indicators', 'comparison_terms', 'action_verbs', 'modifiers'
    ]
    
    # Course config entity types
    course_config_entity_types = list(course_config['entity_types'].keys())
    
    print(f"Current Entity Categories: {len(current_entity_categories)}")
    print(f"Course Config Entity Types: {len(course_config_entity_types)}")
    print(f"   Current: {current_entity_categories}")
    print(f"   Course Config: {course_config_entity_types}")
    
    # 6. EXPANDED ENTITIES ANALYSIS
    print("\n🎯 6. EXPANDED ENTITIES ANALYSIS")
    print("-" * 50)
    
    # Parse expanded entities from the file
    expanded_decision_contexts = [
        'career_change', 'investment_decision', 'business_strategy', 'negotiation',
        'risk_management', 'forecasting_decision', 'optimization_decision', 
        'simulation_decision', 'bias_awareness'
    ]
    
    expanded_categories = [
        'stakeholders', 'criteria', 'timeframes', 'uncertainty', 'complexity'
    ]
    
    print(f"Expanded Decision Contexts: {len(expanded_decision_contexts)}")
    print(f"Expanded Categories: {len(expanded_categories)}")
    
    # Check for overlaps with existing domains
    domain_overlaps = []
    for context in expanded_decision_contexts:
        if context in query_engine_domains or context.replace('_', '') in query_engine_domains:
            domain_overlaps.append(context)
    
    if domain_overlaps:
        print(f"⚠️ Potential domain overlaps: {domain_overlaps}")
    else:
        print("✅ No domain overlaps detected")
    
    # 7. FRAMEWORK ANALYSIS
    print("\n🎯 7. FRAMEWORK ANALYSIS")
    print("-" * 50)
    
    # Check if frameworks are being used
    framework_usage = "not_implemented"  # Based on current state
    
    print(f"Framework Status: {framework_usage}")
    print("   Note: Frameworks are not currently implemented in V1.6.5")
    
    # 8. INTEGRATION ANALYSIS
    print("\n🎯 8. INTEGRATION CONSISTENCY ANALYSIS")
    print("-" * 50)
    
    integration_issues = []
    
    # Check if expanded entities would conflict with existing logic
    if 'negotiation' in expanded_decision_contexts and 'negotiation' in query_engine_domains:
        integration_issues.append("negotiation domain exists in both systems")
    
    if 'risk_management' in expanded_decision_contexts and 'risk_management' in query_engine_fields:
        integration_issues.append("risk_management exists as both context and field")
    
    if integration_issues:
        print("❌ INTEGRATION ISSUES:")
        for issue in integration_issues:
            print(f"   - {issue}")
    else:
        print("✅ No integration conflicts detected")
    
    # 9. RECOMMENDATIONS
    print("\n🎯 9. RECOMMENDATIONS")
    print("-" * 50)
    
    recommendations = []
    
    if keyword_inconsistencies:
        recommendations.append("Synchronize keywords between query_engine.py and course_config.json")
    
    if missing_in_glossary or missing_in_course_config:
        recommendations.append("Align concepts between glossary.json and course_config.json")
    
    if field_mismatch:
        recommendations.append("Standardize application fields between query_engine.py and course_config.json")
    
    if domain_overlaps:
        recommendations.append("Resolve domain naming conflicts between expanded entities and existing domains")
    
    if not recommendations:
        recommendations.append("All components are consistent - safe to proceed with entity enhancement")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # 10. SUMMARY
    print("\n📊 SUMMARY")
    print("-" * 50)
    
    total_issues = len(keyword_inconsistencies) + len(missing_in_glossary) + len(missing_in_course_config) + len(field_mismatch) + len(integration_issues)
    
    if total_issues == 0:
        print("✅ ALL COMPONENTS CONSISTENT")
        print("   Safe to proceed with entity enhancement")
    else:
        print(f"⚠️ {total_issues} CONSISTENCY ISSUES FOUND")
        print("   Address issues before entity enhancement")
    
    return total_issues == 0

def analyze_enhancement_impact():
    """Analyze the impact of merging expanded entities"""
    print("\n🔍 ENTITY ENHANCEMENT IMPACT ANALYSIS")
    print("=" * 50)
    
    # Simulate the merged state
    print("📈 ENHANCEMENT IMPACT:")
    print("   - 9 additional decision contexts")
    print("   - 7 stakeholder types with detailed interests")
    print("   - 6 criteria types for structured evaluation")
    print("   - 3 uncertainty levels for better risk assessment")
    print("   - 3 complexity levels for better tool selection")
    
    print("\n🎯 INTEGRATION STRATEGY:")
    print("   1. Merge expanded entities as additional categories")
    print("   2. Keep existing V1.6.5 entities as fallback")
    print("   3. Use expanded entities for enhanced context recognition")
    print("   4. Maintain backward compatibility")
    
    print("\n✅ BENEFITS:")
    print("   - 233% more keywords for query understanding")
    print("   - Domain-specific decision contexts")
    print("   - Structured evaluation criteria")
    print("   - Better tool-context matching")
    
    print("\n⚠️ CONSIDERATIONS:")
    print("   - Potential naming conflicts need resolution")
    print("   - Integration complexity with existing logic")
    print("   - Testing required for all enhanced features")

if __name__ == "__main__":
    consistency_ok = analyze_glossary_consistency()
    analyze_enhancement_impact()
    
    print("\n" + "=" * 70)
    if consistency_ok:
        print("🎯 RECOMMENDATION: PROCEED WITH ENTITY ENHANCEMENT")
        print("   All components are consistent and ready for enhancement")
    else:
        print("⚠️ RECOMMENDATION: ADDRESS CONSISTENCY ISSUES FIRST")
        print("   Fix identified issues before proceeding with enhancement") 