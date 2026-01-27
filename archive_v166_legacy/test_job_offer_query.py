#!/usr/bin/env python3
"""
Test script to investigate job offer query response quality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 INVESTIGATING JOB OFFER QUERY RESPONSE")
print("=" * 60)

try:
    from query_engine import process_query, detect_course_concept_domains, extract_application_fields, extract_enhanced_entities
    print("✅ Import successful")
    
    # Test job offer queries
    test_queries = [
        "Should I accept this job offer?",
        "How do I evaluate a job offer?",
        "What should I consider when deciding on a job offer?",
        "I received a job offer, how should I think about it strategically?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 40)
        
        # Extract components for debugging
        entities = extract_enhanced_entities(query)
        domains = detect_course_concept_domains(query)
        fields = extract_application_fields(query)
        
        print(f"Detected entities: {entities}")
        print(f"Detected domains: {domains}")
        print(f"Detected fields: {fields}")
        
        # Generate full answer
        answer = process_query(query)
        
        print(f"\nGenerated Answer:")
        print(f"'{answer}'")
        
        # Analyze relevance
        job_keywords = ["job", "offer", "career", "employment", "position", "role", "salary", "benefits", "company"]
        answer_lower = answer.lower()
        has_job_relevance = any(keyword in answer_lower for keyword in job_keywords)
        
        if has_job_relevance:
            print("✅ ANSWER RELEVANCE: Contains job-related content")
        else:
            print("⚠️  ANSWER RELEVANCE: Missing job-related content")
        
        # Check for strategic thinking elements
        strategic_keywords = ["strategic", "analysis", "evaluate", "consider", "decision", "framework"]
        has_strategic_content = any(keyword in answer_lower for keyword in strategic_keywords)
        
        if has_strategic_content:
            print("✅ STRATEGIC CONTENT: Contains strategic thinking elements")
        else:
            print("⚠️  STRATEGIC CONTENT: Missing strategic thinking elements")
        
        print("-" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 