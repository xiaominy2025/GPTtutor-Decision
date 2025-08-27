#!/usr/bin/env python3
"""
Convert deployed test results to markdown format
"""

import json
import os
from datetime import datetime

def create_markdown_report():
    """Create markdown report from deployed test results"""
    
    # Read the JSON results
    try:
        with open('deployed_test_results.json', 'r', encoding='utf-8-sig') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("❌ deployed_test_results.json not found")
        return
    
    # Create markdown content
    md_content = f"""# Deployed v1666 Query Engine Test Results

**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Lambda Function:** engent-v1666-img:v1666_import_fix  
**Endpoint:** https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/query

---

"""
    
    for i, result in enumerate(results, 1):
        md_content += f"""## Query {i}: {result['Query']}

**Status:** {result['Status']}  
**Model:** {result['Model']}  
**Processing Time:** {result['ProcessingTime']:.2f}s

### Strategic Thinking Lens

{result['StrategicThinkingLens']}

### Follow-up Prompts

{result['FollowUpPrompts']}

### Concepts/Tools Extracted

"""
        
        if result['ConceptsToolsPractice']:
            for concept in result['ConceptsToolsPractice']:
                md_content += f"- **{concept['term']}**: {concept['definition']}\n"
        else:
            md_content += "*No specific concepts extracted*\n"
        
        md_content += "\n### Full Answer\n\n"
        md_content += result['Answer']
        
        if 'Error' in result:
            md_content += f"\n\n**Error:** {result['Error']}"
        
        md_content += "\n\n---\n\n"
    
    # Write markdown file
    with open('deployed_v1666_test_results.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ Markdown report created: deployed_v1666_test_results.md")
    print(f"📊 Tested {len(results)} queries")
    
    # Summary statistics
    successful = sum(1 for r in results if r['Status'] == 'Success')
    failed = len(results) - successful
    avg_time = sum(r['ProcessingTime'] for r in results if r['Status'] == 'Success') / successful if successful > 0 else 0
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️ Average processing time: {avg_time:.2f}s")

if __name__ == "__main__":
    create_markdown_report()
