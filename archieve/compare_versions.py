import requests
import json

print("=" * 80)
print("COMPARING LOCAL vs DEPLOYED VERSIONS")
print("=" * 80)

# Test questions
test_questions = [
    "Under tariff uncertainty, how do I plan my production?",
    "I have two job offers, how to choose?", 
    "How to convey bad news to my boss?"
]

# Lambda function URL
lambda_url = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query"

print(f"\n🔍 TESTING DEPLOYED VERSION:")
print(f"URL: {lambda_url}")

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*60}")
    print(f"QUESTION {i}: {question}")
    print(f"{'='*60}")
    
    # Test deployed version
    payload = {
        "query": question,
        "course_id": "decision",
        "user_id": "default"
    }
    
    try:
        response = requests.post(lambda_url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        answer = data.get('data', {}).get('answer', 'No answer found')
        concepts = data.get('data', {}).get('conceptsToolsPractice', [])
        
        print(f"\n📊 DEPLOYED VERSION RESPONSE:")
        print(f"   Answer length: {len(answer)} characters")
        print(f"   Concepts extracted: {len(concepts)}")
        
        if concepts:
            print(f"\n   EXTRACTED CONCEPTS:")
            for concept in concepts:
                term = concept.get('term', 'Unknown')
                print(f"   • {term}")
        else:
            print(f"\n   ❌ NO CONCEPTS EXTRACTED")
        
        # Check for specific concept mentions
        answer_lower = answer.lower()
        specific_concepts = [
            'scenario analysis', 'monte carlo', 'decision tree', 'sensitivity analysis',
            'linear optimization', 'utility functions', 'expected value', 'framing bias',
            'confirmation bias', 'anchoring bias', 'stakeholder alignment'
        ]
        
        found_concepts = []
        for concept in specific_concepts:
            if concept in answer_lower:
                found_concepts.append(concept)
        
        if found_concepts:
            print(f"\n   ✅ SPECIFIC CONCEPTS MENTIONED:")
            for concept in found_concepts:
                print(f"   • {concept}")
        else:
            print(f"\n   ❌ NO SPECIFIC CONCEPTS MENTIONED")
            
    except Exception as e:
        print(f"   ❌ Error testing deployed version: {e}")

print(f"\n{'='*80}")
print("DEPLOYED VERSION TEST COMPLETE")
print(f"{'='*80}")

print(f"\n🔍 TESTING LOCAL VERSION:")
print(f"Note: Local version may have dependency issues")

# Try to test local version if possible
try:
    import sys
    sys.path.append('Repeatability')
    from query_engine import get_top_ranked_concepts, CONCEPT_GLOSSARY
    
    print(f"✅ Successfully imported local query_engine")
    print(f"📚 CONCEPT_GLOSSARY contains {len(CONCEPT_GLOSSARY)} concepts")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"QUESTION {i}: {question}")
        print(f"{'='*60}")
        
        try:
            concepts = get_top_ranked_concepts(question, top_k=3)
            
            print(f"\n📊 LOCAL VERSION RESPONSE:")
            print(f"   Concepts found: {len(concepts)}")
            
            if concepts:
                print(f"\n   EXTRACTED CONCEPTS:")
                for j, (concept_name, definition) in enumerate(concepts, 1):
                    print(f"   {j}. {concept_name}")
                    print(f"      Definition: {definition[:100]}...")
            else:
                print(f"\n   ❌ NO CONCEPTS EXTRACTED")
                
        except Exception as e:
            print(f"   ❌ Error during local concept extraction: {e}")
            
except ImportError as e:
    print(f"❌ Cannot import local query_engine: {e}")
    print(f"This is expected due to dependency issues")

print(f"\n{'='*80}")
print("COMPARISON COMPLETE")
print(f"{'='*80}")
