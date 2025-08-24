import json
import re

def analyze_story_merge_results():
    """Analyze the query results to check Story in Action merging feature"""
    
    with open('query_test_results.json', 'r') as f:
        results = json.load(f)
    
    print("=== STORY IN ACTION MERGING FEATURE ANALYSIS ===\n")
    
    for i in range(1, 4):
        query_key = f"query_{i}"
        if query_key in results:
            data = results[query_key]
            response = json.loads(data['response'])
            
            print(f"Query {i}: {data['question']}")
            print(f"Status: {data['status_code']}")
            print(f"Content Length: {data['content_length']}")
            
            # Extract Strategic Thinking Lens section
            answer = response['data']['answer']
            lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n\n(.*?)(?=\n\n\*\*|\Z)', answer, re.DOTALL)
            
            if lens_match:
                lens_content = lens_match.group(1).strip()
                print(f"Strategic Thinking Lens Length: {len(lens_content)} characters")
                
                # Check for story indicators
                story_indicators = [
                    "For instance,",
                    "For example,",
                    "Consider this scenario:",
                    "Picture",
                    "Imagine",
                    "Envision",
                    "Take the case of",
                    "Suppose"
                ]
                
                found_indicators = []
                for indicator in story_indicators:
                    if indicator.lower() in lens_content.lower():
                        found_indicators.append(indicator)
                
                if found_indicators:
                    print(f"✅ Story indicators found: {', '.join(found_indicators)}")
                    print("✅ Story in Action merging is working!")
                else:
                    print("⚠️ No clear story indicators found")
                
                # Check for natural flow
                if "For instance," in lens_content or "For example," in lens_content:
                    print("✅ Natural story integration detected")
                
                # Check for italics formatting
                if "*" in lens_content:
                    print("✅ Italics formatting preserved")
                
                # Show a preview of the lens content
                preview = lens_content[:200] + "..." if len(lens_content) > 200 else lens_content
                print(f"Lens Preview: {preview}")
                
            else:
                print("❌ No Strategic Thinking Lens section found")
            
            # Check concepts array
            concepts_array = response['data'].get('conceptsToolsPractice', [])
            print(f"Concepts Array Length: {len(concepts_array)}")
            
            print("-" * 80)
            print()

if __name__ == "__main__":
    analyze_story_merge_results()
