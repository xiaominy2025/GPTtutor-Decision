#!/usr/bin/env python3
"""
Test Linear Optimization Query
=============================

Test the specific query from the screenshot to see if linear optimization
is now properly emphasized over Monte Carlo simulation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query

def test_linear_optimization_query():
    """Test the specific linear optimization query"""
    print("🧪 Testing Linear Optimization Query")
    print("=" * 50)
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    print(f"📋 Query: {query}")
    
    try:
        result = process_query(query)
        
        # Extract Strategic Thinking Lens section
        lines = result.split('\n')
        strategic_lens_section = False
        lens_content = []
        
        for line in lines:
            if "**Strategic Thinking Lens**" in line:
                strategic_lens_section = True
            elif strategic_lens_section and line.strip().startswith('**'):
                break
            elif strategic_lens_section:
                lens_content.append(line)
        
        lens_text = '\n'.join(lens_content)
        print(f"\n📋 Strategic Thinking Lens Content:")
        print(lens_text)
        
        # Check framework emphasis
        linear_mentions = lens_text.lower().count('linear')
        monte_carlo_mentions = lens_text.lower().count('monte carlo')
        
        print(f"\n📊 Framework Mentions:")
        print(f"  Linear optimization: {linear_mentions}")
        print(f"  Monte Carlo: {monte_carlo_mentions}")
        
        if linear_mentions > monte_carlo_mentions:
            print("✅ Linear optimization properly emphasized")
        elif linear_mentions == monte_carlo_mentions:
            print("⚠️ Equal emphasis on both frameworks")
        else:
            print("❌ Monte Carlo still over-emphasized")
        
        # Check if linear optimization is mentioned first
        if 'linear' in lens_text.lower()[:200]:
            print("✅ Linear optimization mentioned early in the text")
        else:
            print("❌ Linear optimization not mentioned early")
        
        return linear_mentions >= monte_carlo_mentions
        
    except Exception as e:
        print(f"❌ Error testing linear optimization query: {e}")
        return False

if __name__ == "__main__":
    success = test_linear_optimization_query()
    if success:
        print("\n🎉 Linear optimization is now properly emphasized!")
    else:
        print("\n⚠️ Linear optimization emphasis needs improvement.")
    sys.exit(0 if success else 1) 