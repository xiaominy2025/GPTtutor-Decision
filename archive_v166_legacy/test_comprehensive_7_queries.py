#!/usr/bin/env python3
"""
Comprehensive 7 queries test for manual review
"""

import sys
import os
from query_engine import process_query, load_data_lazily

def test_comprehensive_7_queries():
    """Test 7 diverse queries and document answers for manual review"""
    
    print("🧪 Comprehensive 7 Queries Test for Manual Review")
    print("=" * 70)
    
    # 7 diverse test queries covering different domains and application fields
    test_queries = [
        "How should I deal with unfair critiques from my manager?",
        "Should I invest in stocks or bonds for my retirement?",
        "How do I negotiate a better salary package?",
        "What's the best way to optimize my production process?",
        "How can I market my new product effectively?",
        "Should I start my own business or stay employed?",
        "What tools can help me make better decisions?"
    ]
    
    try:
        print("📊 Testing 7 diverse queries for manual review...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 QUERY {i}/7: {query}")
            print("=" * 60)
            
            try:
                result = process_query(query)
                
                # Extract sections for analysis
                sections = {}
                current_section = None
                current_content = []
                
                for line in result.split('\n'):
                    if line.strip().startswith('##'):
                        if current_section:
                            sections[current_section] = '\n'.join(current_content).strip()
                        current_section = line.strip('#').strip()
                        current_content = []
                    elif current_section:
                        current_content.append(line)
                
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Document the results
                print(f"📝 QUERY: {query}")
                print(f"🎯 STRATEGIC THINKING LENS:")
                if 'Strategic Thinking Lens' in sections:
                    lens_content = sections['Strategic Thinking Lens']
                    print(lens_content[:500] + "..." if len(lens_content) > 500 else lens_content)
                else:
                    print("❌ No Strategic Thinking Lens found")
                
                print(f"\n🔧 CONCEPTS/TOOLS:")
                if 'Concepts/Tools' in sections:
                    concepts_content = sections['Concepts/Tools']
                    print(concepts_content[:300] + "..." if len(concepts_content) > 300 else concepts_content)
                else:
                    print("❌ No Concepts/Tools found")
                
                print(f"\n❓ FOLLOW-UP PROMPTS:")
                if 'Follow-up Prompts' in sections:
                    prompts_content = sections['Follow-up Prompts']
                    print(prompts_content[:300] + "..." if len(prompts_content) > 300 else prompts_content)
                else:
                    print("❌ No Follow-up Prompts found")
                
                print("\n" + "="*60 + "\n")
                
            except Exception as e:
                print(f"❌ Query {i} failed: {e}")
                print("="*60 + "\n")
        
        print("🎉 Comprehensive 7 queries test completed!")
        print("📋 Results documented above for manual review")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_7_queries() 