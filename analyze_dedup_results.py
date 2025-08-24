import json
import re

def analyze_query_results():
    """Analyze the query results to check deduplication feature"""
    
    with open('query_test_results.json', 'r') as f:
        results = json.load(f)
    
    print("=== DEDUPLICATION FEATURE ANALYSIS ===\n")
    
    for i in range(1, 4):
        query_key = f"query_{i}"
        if query_key in results:
            data = results[query_key]
            response = json.loads(data['response'])
            
            print(f"Query {i}: {data['question']}")
            print(f"Status: {data['status_code']}")
            print(f"Content Length: {data['content_length']}")
            
            # Extract concepts from the answer text
            answer = response['data']['answer']
            concepts_section = re.search(r'\*\*Concepts/Tools\*\*\s*\n\n(.*?)(?=\n\n|$)', answer, re.DOTALL)
            
            if concepts_section:
                concepts_text = concepts_section.group(1).strip()
                print(f"Concepts Section Found: {len(concepts_text)} characters")
                print("Concepts in answer:")
                print(concepts_text)
            else:
                print("No Concepts/Tools section found in answer")
            
            # Check conceptsToolsPractice array
            concepts_array = response['data'].get('conceptsToolsPractice', [])
            print(f"Concepts Array Length: {len(concepts_array)}")
            
            if concepts_array:
                print("Concepts in array:")
                for j, concept in enumerate(concepts_array):
                    print(f"  {j+1}. {concept.get('term', 'N/A')}: {concept.get('definition', 'N/A')}")
                
                # Check for duplicates in the array
                terms = [concept.get('term', '').lower() for concept in concepts_array]
                unique_terms = list(set(terms))
                if len(terms) != len(unique_terms):
                    print(f"⚠️  DUPLICATES FOUND: {len(terms)} total, {len(unique_terms)} unique")
                else:
                    print("✅ No duplicates in concepts array")
            else:
                print("⚠️  No concepts in array (extraction may have failed)")
            
            print("-" * 80)
            print()

if __name__ == "__main__":
    analyze_query_results()
