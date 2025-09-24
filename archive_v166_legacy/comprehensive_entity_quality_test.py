#!/usr/bin/env python3
"""
Comprehensive test to check the quality of answers with enhanced entity addition.
This test evaluates how entity extraction improves answer relevance and specificity.
"""

from query_engine import (
    extract_enhanced_entities, 
    enhance_strategic_lens_with_entities,
    process_query,
    detect_course_concept_domains,
    extract_application_field
)

def test_entity_extraction_quality():
    """Test the quality and accuracy of entity extraction."""
    
    print("🧪 Entity Extraction Quality Test")
    print("=" * 70)
    
    # Test cases with known entities
    test_cases = [
        {
            "query": "How can I optimize production with 50 employees while considering budget constraints and team dynamics?",
            "expected_entities": {
                "quantitative_terms": ["50 employees"],
                "stakeholders": ["employees", "team"],
                "constraints": ["budget", "constraints"]
            },
            "description": "Quantitative + Stakeholders + Constraints"
        },
        {
            "query": "Should I invest in AI technology for my manufacturing business with 3 locations next year?",
            "expected_entities": {
                "technologies": ["ai"],
                "industries": ["manufacturing"],
                "quantitative_terms": ["3 locations"],
                "time_periods": ["next year"]
            },
            "description": "Technology + Industry + Quantitative + Time"
        },
        {
            "query": "What are the risks and opportunities of expanding to 5 new markets with 100 employees over the next 2 years?",
            "expected_entities": {
                "risks": ["risks"],
                "quantitative_terms": ["5 new markets", "100 employees"],
                "time_periods": ["next 2 years"],
                "stakeholders": ["employees"]
            },
            "description": "Risks + Quantitative + Time + Stakeholders"
        },
        {
            "query": "How do I reduce groupthink in my team of 25 people while maintaining efficiency and quality standards?",
            "expected_entities": {
                "quantitative_terms": ["25 people"],
                "stakeholders": ["team"],
                "constraints": ["efficiency", "quality", "standards"]
            },
            "description": "Behavioral + Quantitative + Constraints + Stakeholders"
        }
    ]
    
    total_accuracy = 0
    total_cases = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 60)
        
        # Extract entities
        entities = extract_enhanced_entities(test_case['query'])
        
        print("Extracted entities:")
        for category, values in entities.items():
            if values:
                print(f"  {category}: {values}")
        
        # Check accuracy against expected entities
        accuracy_score = 0
        total_expected = 0
        
        for expected_category, expected_values in test_case['expected_entities'].items():
            if expected_category in entities:
                extracted_values = entities[expected_category]
                matches = 0
                for expected_value in expected_values:
                    # Check if any extracted value contains the expected value
                    for extracted_value in extracted_values:
                        if expected_value.lower() in extracted_value.lower():
                            matches += 1
                            break
                
                category_accuracy = matches / len(expected_values) if expected_values else 0
                accuracy_score += category_accuracy
                total_expected += 1
                
                print(f"  ✅ {expected_category}: {matches}/{len(expected_values)} correct")
            else:
                print(f"  ❌ {expected_category}: Not found")
                total_expected += 1
        
        case_accuracy = accuracy_score / total_expected if total_expected > 0 else 0
        total_accuracy += case_accuracy
        
        print(f"Case accuracy: {case_accuracy:.2%}")
        print("=" * 60)
    
    overall_accuracy = total_accuracy / total_cases
    print(f"\n📊 OVERALL ENTITY EXTRACTION ACCURACY: {overall_accuracy:.2%}")
    
    return overall_accuracy

def test_strategic_lens_enhancement():
    """Test how entity enhancement improves strategic lens quality."""
    
    print("\n🎯 Strategic Lens Enhancement Quality Test")
    print("=" * 70)
    
    test_cases = [
        {
            "query": "How can I optimize production with 50 employees while considering budget constraints?",
            "base_lens": "This requires technical analysis and optimization.",
            "expected_enhancements": ["50 employees", "budget", "constraints"]
        },
        {
            "query": "Should I invest in AI technology for my manufacturing business next year?",
            "base_lens": "This involves strategic technology decisions.",
            "expected_enhancements": ["ai", "manufacturing", "next year"]
        }
    ]
    
    enhancement_scores = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}")
        print(f"Query: {test_case['query']}")
        print(f"Base lens: {test_case['base_lens']}")
        print("-" * 50)
        
        # Extract entities and enhance lens
        entities = extract_enhanced_entities(test_case['query'])
        enhanced_lens = enhance_strategic_lens_with_entities(test_case['base_lens'], entities)
        
        print(f"Enhanced lens: {enhanced_lens}")
        
        # Check for expected enhancements
        enhancements_found = 0
        for expected_enhancement in test_case['expected_enhancements']:
            if expected_enhancement.lower() in enhanced_lens.lower():
                enhancements_found += 1
                print(f"  ✅ Found: {expected_enhancement}")
            else:
                print(f"  ❌ Missing: {expected_enhancement}")
        
        enhancement_score = enhancements_found / len(test_case['expected_enhancements'])
        enhancement_scores.append(enhancement_score)
        
        print(f"Enhancement score: {enhancement_score:.2%}")
    
    avg_enhancement_score = sum(enhancement_scores) / len(enhancement_scores)
    print(f"\n📊 AVERAGE ENHANCEMENT SCORE: {avg_enhancement_score:.2%}")
    
    return avg_enhancement_score

def test_full_answer_quality():
    """Test the quality of full answers with entity enhancement."""
    
    print("\n🎯 Full Answer Quality Test")
    print("=" * 70)
    
    test_queries = [
        {
            "query": "How can I optimize production with 50 employees while considering budget constraints and team dynamics?",
            "expected_entities": ["50 employees", "budget", "team", "constraints"],
            "description": "Operations with quantitative and stakeholder context"
        },
        {
            "query": "Should I invest in AI technology for my manufacturing business with 3 locations next year?",
            "expected_entities": ["ai", "manufacturing", "3 locations", "next year"],
            "description": "Technology investment with industry and time context"
        },
        {
            "query": "What are the risks and opportunities of expanding to 5 new markets with 100 employees over the next 2 years?",
            "expected_entities": ["risks", "5 new markets", "100 employees", "next 2 years"],
            "description": "Strategic expansion with risk and quantitative context"
        }
    ]
    
    quality_scores = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        try:
            # Process query
            response = process_query(test_case['query'])
            
            # Extract entities
            entities = extract_enhanced_entities(test_case['query'])
            
            # Check if strategic lens contains entity-specific content
            if "Strategic Thinking Lens" in response:
                strategic_lens = response.split("Strategic Thinking Lens")[1].split("##")[0].strip()
                
                # Count entity terms found in strategic lens
                entity_terms_found = 0
                for expected_entity in test_case['expected_entities']:
                    if expected_entity.lower() in strategic_lens.lower():
                        entity_terms_found += 1
                        print(f"  ✅ Found in strategic lens: {expected_entity}")
                    else:
                        print(f"  ❌ Missing from strategic lens: {expected_entity}")
                
                # Calculate quality score
                quality_score = entity_terms_found / len(test_case['expected_entities'])
                quality_scores.append(quality_score)
                
                print(f"Strategic lens quality score: {quality_score:.2%}")
                print(f"Strategic lens length: {len(strategic_lens)} characters")
                
                # Check overall response quality
                sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts", "Concepts/Tools"]
                missing_sections = [s for s in sections if s not in response]
                
                if not missing_sections:
                    print("✅ All required sections present")
                else:
                    print(f"❌ Missing sections: {missing_sections}")
                
                print(f"Full response length: {len(response)} characters")
                
            else:
                print("❌ Strategic Thinking Lens not found in response")
                quality_scores.append(0)
                
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            quality_scores.append(0)
        
        print("=" * 50)
    
    avg_quality_score = sum(quality_scores) / len(quality_scores)
    print(f"\n📊 AVERAGE ANSWER QUALITY SCORE: {avg_quality_score:.2%}")
    
    return avg_quality_score

def test_entity_impact_comparison():
    """Compare answers with and without entity enhancement."""
    
    print("\n🔄 Entity Impact Comparison Test")
    print("=" * 70)
    
    test_query = "How can I optimize production with 50 employees while considering budget constraints and team dynamics?"
    
    print(f"Test Query: {test_query}")
    print("-" * 50)
    
    # Extract entities
    entities = extract_enhanced_entities(test_query)
    print("Extracted entities:")
    for category, values in entities.items():
        if values:
            print(f"  {category}: {values}")
    
    # Test base strategic lens vs enhanced
    base_lens = "This requires technical analysis and optimization."
    enhanced_lens = enhance_strategic_lens_with_entities(base_lens, entities)
    
    print(f"\nBase strategic lens: {base_lens}")
    print(f"Enhanced strategic lens: {enhanced_lens}")
    
    # Calculate enhancement metrics
    base_length = len(base_lens)
    enhanced_length = len(enhanced_lens)
    length_increase = ((enhanced_length - base_length) / base_length) * 100
    
    print(f"\n📊 ENHANCEMENT METRICS:")
    print(f"Base length: {base_length} characters")
    print(f"Enhanced length: {enhanced_length} characters")
    print(f"Length increase: {length_increase:.1f}%")
    
    # Count entity terms in enhanced lens
    entity_terms_in_enhanced = 0
    for category, values in entities.items():
        for value in values:
            if value.lower() in enhanced_lens.lower():
                entity_terms_in_enhanced += 1
    
    print(f"Entity terms incorporated: {entity_terms_in_enhanced}")
    
    return {
        "length_increase": length_increase,
        "entity_terms_incorporated": entity_terms_in_enhanced
    }

def run_comprehensive_quality_test():
    """Run all comprehensive quality tests."""
    
    print("🎯 COMPREHENSIVE ENTITY QUALITY TEST SUITE")
    print("=" * 80)
    
    # Run all tests
    entity_accuracy = test_entity_extraction_quality()
    enhancement_score = test_strategic_lens_enhancement()
    answer_quality = test_full_answer_quality()
    impact_metrics = test_entity_impact_comparison()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE QUALITY TEST RESULTS")
    print("=" * 80)
    
    print(f"✅ Entity Extraction Accuracy: {entity_accuracy:.2%}")
    print(f"✅ Strategic Lens Enhancement Score: {enhancement_score:.2%}")
    print(f"✅ Full Answer Quality Score: {answer_quality:.2%}")
    print(f"✅ Length Increase with Entities: {impact_metrics['length_increase']:.1f}%")
    print(f"✅ Entity Terms Incorporated: {impact_metrics['entity_terms_incorporated']}")
    
    # Overall assessment
    overall_score = (entity_accuracy + enhancement_score + answer_quality) / 3
    
    print(f"\n🎯 OVERALL QUALITY SCORE: {overall_score:.2%}")
    
    if overall_score >= 0.8:
        print("🎉 EXCELLENT: Enhanced entity extraction significantly improves answer quality!")
    elif overall_score >= 0.6:
        print("✅ GOOD: Enhanced entity extraction provides meaningful improvements.")
    elif overall_score >= 0.4:
        print("⚠️ FAIR: Enhanced entity extraction shows some improvement.")
    else:
        print("❌ NEEDS IMPROVEMENT: Enhanced entity extraction requires refinement.")
    
    return {
        "entity_accuracy": entity_accuracy,
        "enhancement_score": enhancement_score,
        "answer_quality": answer_quality,
        "overall_score": overall_score,
        "impact_metrics": impact_metrics
    }

if __name__ == "__main__":
    results = run_comprehensive_quality_test()
    print(f"\n🎯 Comprehensive Entity Quality Test Complete!") 