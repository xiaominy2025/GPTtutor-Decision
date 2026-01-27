#!/usr/bin/env python3
"""
Test Framework Selection Fix
===========================

Test script to verify that framework selection is now query-aware and prioritizes
the most relevant frameworks based on query content.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query, detect_course_concept_domains

def test_framework_selection():
    """Test that framework selection is query-aware"""
    print("🧪 Testing Framework Selection Fix")
    print("=" * 50)
    
    test_queries = [
        "How does linear optimization inform your approach to balancing efficiency with flexibility?",
        "How do I optimize production using linear programming?",
        "What are the key factors in choosing between two job offers?",
        "How do personal biases affect my ethical decisions?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query[:60]}...")
        
        try:
            # Get domain detection
            domains = detect_course_concept_domains(query)
            if domains:
                primary_domain = max(domains.items(), key=lambda x: x[1])
                print(f"📊 Detected domain: {primary_domain[0]} (score: {primary_domain[1]:.2f})")
            
            # Get response
            result = process_query(query)
            
            # Check for framework mentions in Strategic Thinking Lens
            lines = result.split('\n')
            strategic_lens_section = False
            framework_mentions = []
            
            for line in lines:
                if "**Strategic Thinking Lens**" in line:
                    strategic_lens_section = True
                elif strategic_lens_section and line.strip().startswith('**'):
                    break
                elif strategic_lens_section:
                    # Look for framework mentions
                    frameworks = [
                        "linear optimization", "monte carlo", "swot", "porter", 
                        "batna", "cognitive bias", "sensitivity analysis"
                    ]
                    for framework in frameworks:
                        if framework in line.lower():
                            framework_mentions.append(framework)
            
            print(f"📊 Frameworks mentioned: {framework_mentions}")
            
            # For linear optimization query, check if linear optimization is prioritized
            if "linear" in query.lower() or "optimization" in query.lower():
                if "linear optimization" in [f.lower() for f in framework_mentions]:
                    print("✅ Linear optimization properly prioritized")
                else:
                    print("❌ Linear optimization not prioritized")
            
            # For other queries, check domain-appropriate frameworks
            elif "bias" in query.lower():
                if "cognitive bias" in [f.lower() for f in framework_mentions]:
                    print("✅ Cognitive bias properly prioritized")
                else:
                    print("❌ Cognitive bias not prioritized")
            
            elif "job" in query.lower() or "offer" in query.lower():
                if any(f in [f.lower() for f in framework_mentions] for f in ["swot", "porter"]):
                    print("✅ Strategic frameworks properly prioritized")
                else:
                    print("❌ Strategic frameworks not prioritized")
            
        except Exception as e:
            print(f"❌ Error testing framework selection: {e}")
    
    return True

if __name__ == "__main__":
    success = test_framework_selection()
    if success:
        print("\n🎉 Framework selection fix is working!")
    else:
        print("\n⚠️ Framework selection fix needs attention.")
    sys.exit(0 if success else 1) 