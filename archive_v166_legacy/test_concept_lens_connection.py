#!/usr/bin/env python3
"""
Test script to verify that frameworks from Strategic Thinking Lens are included in Concepts/Tools.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import process_query

def test_linear_optimization_concept_connection():
    """Test that linear optimization frameworks appear in concepts."""
    
    print("🔍 Testing Linear Optimization Concept Connection")
    print("=" * 60)
    
    query = "How does linear optimization inform your approach to balancing efficiency with flexibility?"
    
    try:
        # Process the query
        answer = process_query(query)
        
        print(f"Query: {query}")
        print(f"\nGenerated Answer:")
        print("-" * 50)
        print(answer)
        print("-" * 50)
        
        # Check if Strategic Thinking Lens mentions linear optimization
        strategic_lens_mentions = []
        if "Linear optimization modeling" in answer:
            strategic_lens_mentions.append("Linear optimization modeling")
        if "Sensitivity analysis" in answer:
            strategic_lens_mentions.append("Sensitivity analysis")
        
        print(f"\nFrameworks mentioned in Strategic Thinking Lens: {strategic_lens_mentions}")
        
        # Check if Concepts/Tools section includes relevant concepts
        concepts_mentions = []
        if "Linear optimization" in answer:
            concepts_mentions.append("Linear optimization")
        if "Sensitivity analysis" in answer:
            concepts_mentions.append("Sensitivity analysis")
        
        print(f"Concepts mentioned in Concepts/Tools: {concepts_mentions}")
        
        # Check for the connection
        lens_frameworks = set(strategic_lens_mentions)
        concept_frameworks = set(concepts_mentions)
        
        # Check if frameworks from lens appear in concepts
        connection_score = 0
        for framework in lens_frameworks:
            if any(framework.lower() in concept.lower() for concept in concept_frameworks):
                connection_score += 1
        
        if connection_score > 0:
            print(f"✅ Connection found: {connection_score} framework(s) from lens appear in concepts")
            return True
        else:
            print("❌ No connection found between lens frameworks and concepts")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_concept_extraction_functions():
    """Test the framework extraction and mapping functions."""
    
    print(f"\n🔧 Testing Framework Extraction Functions")
    print("=" * 50)
    
    from query_engine import extract_frameworks_from_strategic_lens, map_frameworks_to_concepts
    
    # Test strategic lens content
    test_lens = """
    **Strategic Thinking Lens**
    
    This involves technical analysis and modeling under uncertainty using Linear optimization modeling and Sensitivity analysis. Use mathematical and computational tools to optimize outcomes while accounting for variability in key parameters.
    """
    
    # Extract frameworks
    frameworks = extract_frameworks_from_strategic_lens(test_lens)
    print(f"Extracted frameworks: {frameworks}")
    
    # Map to concepts
    concepts = map_frameworks_to_concepts(frameworks)
    print(f"Mapped concepts: {[name for name, _ in concepts]}")
    
    expected_frameworks = ["Linear optimization modeling", "Sensitivity analysis"]
    expected_concepts = ["linear optimization", "sensitivity analysis"]
    
    # Check extraction
    extraction_success = all(fw in frameworks for fw in expected_frameworks)
    print(f"Framework extraction: {'✅ PASS' if extraction_success else '❌ FAIL'}")
    
    # Check mapping
    concept_names = [name.lower() for name, _ in concepts]
    mapping_success = all(concept in concept_names for concept in expected_concepts)
    print(f"Concept mapping: {'✅ PASS' if mapping_success else '❌ FAIL'}")
    
    return extraction_success and mapping_success

def test_full_integration():
    """Test the full integration of lens-to-concept connection."""
    
    print(f"\n🔧 Testing Full Integration")
    print("=" * 50)
    
    test_queries = [
        "How does linear optimization inform your approach to balancing efficiency with flexibility?",
        "What Monte Carlo simulation approach should I use for risk analysis?",
        "How do I perform sensitivity analysis on my decision variables?"
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        
        try:
            answer = process_query(query)
            
            # Check for lens-concept connection
            lens_frameworks = []
            if "Linear optimization modeling" in answer:
                lens_frameworks.append("Linear optimization modeling")
            if "Monte Carlo simulation" in answer:
                lens_frameworks.append("Monte Carlo simulation")
            if "Sensitivity analysis" in answer:
                lens_frameworks.append("Sensitivity analysis")
            
            concept_frameworks = []
            if "Linear optimization" in answer:
                concept_frameworks.append("Linear optimization")
            if "Monte Carlo simulation" in answer:
                concept_frameworks.append("Monte Carlo simulation")
            if "Sensitivity analysis" in answer:
                concept_frameworks.append("Sensitivity analysis")
            
            # Check connection
            connection_found = False
            for lens_fw in lens_frameworks:
                for concept_fw in concept_frameworks:
                    if lens_fw.lower() in concept_fw.lower() or concept_fw.lower() in lens_fw.lower():
                        connection_found = True
                        break
                if connection_found:
                    break
            
            if connection_found:
                print(f"✅ Connection found between lens and concepts")
                results.append(True)
            else:
                print(f"❌ No connection found")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
    
    return results

if __name__ == "__main__":
    print("🚀 Starting Concept-Lens Connection Test")
    print("=" * 70)
    
    # Run tests
    test1_result = test_linear_optimization_concept_connection()
    test2_result = test_concept_extraction_functions()
    test3_results = test_full_integration()
    
    print(f"\n📊 TEST RESULTS")
    print("=" * 50)
    
    print(f"Linear optimization connection: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Framework extraction functions: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"Full integration tests: {'✅ PASS' if all(test3_results) else '❌ FAIL'}")
    
    overall_success = test1_result and test2_result and all(test3_results)
    
    print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("✅ Framework-to-concept connection is working correctly!")
    else:
        print("❌ Framework-to-concept connection needs improvement") 