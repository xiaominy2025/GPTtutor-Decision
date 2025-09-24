#!/usr/bin/env python3
"""
Comprehensive Test Suite for V1.6.6 Step 2 Refinements
Validates adaptive word count, connector variety, smooth flow, and performance
"""

import pytest
import sys
import os
import time
import json
import re
from typing import Dict, List, Any, Tuple
from collections import Counter

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the query engine
try:
    from query_engine import (
        process_query, 
        load_data_lazily,
        detect_course_concept_domains,
        merge_and_extend_with_story,
        extract_sections_from_response
    )
    QUERY_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Query engine import failed: {e}")
    QUERY_ENGINE_AVAILABLE = False

class TestV166Step2Refinements:
    """Test suite for V1.6.6 Step 2 refinements"""
    
    # Test queries organized by domain count
    TEST_QUERIES_1_DOMAIN = [
        "I need to decide between two job offers with different salaries",
        "How do I choose the best investment option?",
        "What should I consider when buying a house?",
        "I'm trying to decide whether to start my own business",
        "How do I negotiate a better salary?",
        "What factors should I consider when choosing a career path?"
    ]
    
    TEST_QUERIES_2_DOMAINS = [
        "I need to decide between a high-paying job in finance and a lower-paying job in tech that I enjoy more",
        "How do I balance financial security with personal fulfillment in my career choice?",
        "Should I invest in stocks or real estate given my current financial situation?",
        "I'm considering a business partnership that involves both financial and personal risks",
        "How do I negotiate a contract that benefits both my company and the client?",
        "What should I prioritize: career advancement or work-life balance?"
    ]
    
    TEST_QUERIES_3_DOMAINS = [
        "I need to decide between a high-paying finance job, a tech startup with equity, or starting my own business",
        "How do I balance financial security, personal fulfillment, and family responsibilities in my career?",
        "Should I invest in stocks, real estate, or cryptocurrency given market uncertainty and my risk tolerance?",
        "I'm considering a business partnership that involves financial risks, personal relationships, and market uncertainty",
        "How do I negotiate a complex contract involving multiple stakeholders with different interests?",
        "What should I prioritize: career advancement, work-life balance, or financial stability?"
    ]
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        if not QUERY_ENGINE_AVAILABLE:
            pytest.skip("Query engine not available")
    
    def count_words(self, text: str) -> int:
        """Count words in text, excluding markdown formatting"""
        # Remove markdown formatting
        clean_text = re.sub(r'\*\*.*?\*\*', '', text)
        clean_text = re.sub(r'#+', '', clean_text)
        clean_text = re.sub(r'[-•*]', '', clean_text)
        # Count words
        words = clean_text.split()
        return len(words)
    
    def extract_lens_section(self, response: str) -> str:
        """Extract the Strategic Thinking Lens section from response"""
        match = re.search(r'\*\*Strategic Thinking Lens\*\*.*?(?=\*\*|\Z)', response, re.DOTALL | re.IGNORECASE)
        if match:
            lens_text = match.group(0)
            # Remove the header
            lens_text = re.sub(r'\*\*Strategic Thinking Lens\*\*', '', lens_text, flags=re.IGNORECASE)
            return lens_text.strip()
        return ""
    
    def detect_connectors(self, text: str) -> List[str]:
        """Detect connectors used in the text"""
        connectors = [
            "For example,",
            "For instance,",
            "Consider,",
            "Take,",
            "Imagine,",
            "Picture,",
            "Think of,",
            "Let's say,",
            "Suppose,",
            "Say,"
        ]
        found_connectors = []
        for connector in connectors:
            if connector.lower() in text.lower():
                found_connectors.append(connector)
        return found_connectors
    
    def check_duplication(self, lens_text: str) -> Dict[str, Any]:
        """Check for duplication between reasoning and story parts"""
        # Split into paragraphs
        paragraphs = [p.strip() for p in lens_text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 2:
            return {"has_duplication": False, "duplication_score": 0.0}
        
        # Check for similar phrases between paragraphs
        reasoning = paragraphs[0].lower()
        story = ' '.join(paragraphs[1:]).lower()
        
        # Simple similarity check
        reasoning_words = set(re.findall(r'\b\w+\b', reasoning))
        story_words = set(re.findall(r'\b\w+\b', story))
        
        common_words = reasoning_words.intersection(story_words)
        total_unique_words = len(reasoning_words.union(story_words))
        
        duplication_score = len(common_words) / total_unique_words if total_unique_words > 0 else 0.0
        
        return {
            "has_duplication": duplication_score > 0.3,  # More than 30% overlap
            "duplication_score": duplication_score
        }
    
    def test_adaptive_word_count_compliance(self):
        """Test adaptive word count compliance for different domain counts"""
        print("\nTesting Adaptive Word Count Compliance")
        print("=" * 50)
        
        results = {
            "1_domain": {"tests": [], "compliance_rate": 0.0},
            "2_domains": {"tests": [], "compliance_rate": 0.0},
            "3_domains": {"tests": [], "compliance_rate": 0.0}
        }
        
        # Test 1 domain queries
        for query in self.TEST_QUERIES_1_DOMAIN[:3]:  # Test first 3
            start_time = time.time()
            response = process_query(query)
            end_time = time.time()
            
            lens_text = self.extract_lens_section(response)
            word_count = self.count_words(lens_text)
            
            # Expected: 90-120 words for 1 domain
            is_compliant = 90 <= word_count <= 120
            
            test_result = {
                "query": query,
                "word_count": word_count,
                "is_compliant": is_compliant,
                "response_time": end_time - start_time,
                "lens_text": lens_text[:200] + "..." if len(lens_text) > 200 else lens_text
            }
            
            results["1_domain"]["tests"].append(test_result)
            print(f"1 Domain - {word_count} words: {'PASS' if is_compliant else 'FAIL'}")
        
        # Test 2 domain queries
        for query in self.TEST_QUERIES_2_DOMAINS[:3]:  # Test first 3
            start_time = time.time()
            response = process_query(query)
            end_time = time.time()
            
            lens_text = self.extract_lens_section(response)
            word_count = self.count_words(lens_text)
            
            # Expected: 115-135 words for 2 domains
            is_compliant = 115 <= word_count <= 135
            
            test_result = {
                "query": query,
                "word_count": word_count,
                "is_compliant": is_compliant,
                "response_time": end_time - start_time,
                "lens_text": lens_text[:200] + "..." if len(lens_text) > 200 else lens_text
            }
            
            results["2_domains"]["tests"].append(test_result)
            print(f"2 Domains - {word_count} words: {'PASS' if is_compliant else 'FAIL'}")
        
        # Test 3 domain queries
        for query in self.TEST_QUERIES_3_DOMAINS[:3]:  # Test first 3
            start_time = time.time()
            response = process_query(query)
            end_time = time.time()
            
            lens_text = self.extract_lens_section(response)
            word_count = self.count_words(lens_text)
            
            # Expected: 135-150 words for 3 domains
            is_compliant = 135 <= word_count <= 150
            
            test_result = {
                "query": query,
                "word_count": word_count,
                "is_compliant": is_compliant,
                "response_time": end_time - start_time,
                "lens_text": lens_text[:200] + "..." if len(lens_text) > 200 else lens_text
            }
            
            results["3_domains"]["tests"].append(test_result)
            print(f"3 Domains - {word_count} words: {'PASS' if is_compliant else 'FAIL'}")
        
        # Calculate compliance rates
        for domain_type in results:
            compliant_tests = sum(1 for test in results[domain_type]["tests"] if test["is_compliant"])
            total_tests = len(results[domain_type]["tests"])
            compliance_rate = (compliant_tests / total_tests) * 100 if total_tests > 0 else 0
            results[domain_type]["compliance_rate"] = compliance_rate
        
        # Assertions
        assert results["1_domain"]["compliance_rate"] >= 60, f"1 domain compliance too low: {results['1_domain']['compliance_rate']}%"
        assert results["2_domains"]["compliance_rate"] >= 60, f"2 domains compliance too low: {results['2_domains']['compliance_rate']}%"
        assert results["3_domains"]["compliance_rate"] >= 60, f"3 domains compliance too low: {results['3_domains']['compliance_rate']}%"
        
        print(f"\nCompliance Rates:")
        print(f"1 Domain: {results['1_domain']['compliance_rate']:.1f}%")
        print(f"2 Domains: {results['2_domains']['compliance_rate']:.1f}%")
        print(f"3 Domains: {results['3_domains']['compliance_rate']:.1f}%")
        
        return results
    
    def test_connector_variety(self):
        """Test connector variety across responses"""
        print("\nTesting Connector Variety")
        print("=" * 40)
        
        all_connectors = []
        connector_counts = Counter()
        
        # Test queries from all domain counts
        all_queries = (self.TEST_QUERIES_1_DOMAIN[:2] + 
                      self.TEST_QUERIES_2_DOMAINS[:2] + 
                      self.TEST_QUERIES_3_DOMAINS[:2])
        
        for query in all_queries:
            response = process_query(query)
            lens_text = self.extract_lens_section(response)
            connectors = self.detect_connectors(lens_text)
            
            all_connectors.extend(connectors)
            connector_counts.update(connectors)
            
            print(f"Query: {query[:50]}...")
            print(f"Connectors found: {connectors}")
            print("-" * 30)
        
        # Check variety requirements
        unique_connectors = len(set(all_connectors))
        most_common_connector = connector_counts.most_common(1)[0] if connector_counts else ("", 0)
        most_common_percentage = (most_common_connector[1] / len(all_connectors)) * 100 if all_connectors else 0
        
        print(f"\nConnector Analysis:")
        print(f"Total connectors used: {len(all_connectors)}")
        print(f"Unique connectors: {unique_connectors}")
        print(f"Most common connector: {most_common_connector[0]} ({most_common_percentage:.1f}%)")
        
        # Assertions
        assert unique_connectors >= 2, f"Not enough connector variety: {unique_connectors} unique connectors"
        assert most_common_percentage <= 60, f"Single connector overused: {most_common_percentage:.1f}%"
        
        print("PASS: Connector variety requirements met!")
        return {
            "total_connectors": len(all_connectors),
            "unique_connectors": unique_connectors,
            "most_common_percentage": most_common_percentage,
            "connector_distribution": dict(connector_counts)
        }
    
    def test_smooth_flow_and_structure(self):
        """Test smooth flow and proper structure"""
        print("\nTesting Smooth Flow and Structure")
        print("=" * 45)
        
        flow_results = []
        
        # Test a variety of queries
        test_queries = [
            self.TEST_QUERIES_1_DOMAIN[0],
            self.TEST_QUERIES_2_DOMAINS[0],
            self.TEST_QUERIES_3_DOMAINS[0]
        ]
        
        for query in test_queries:
            response = process_query(query)
            lens_text = self.extract_lens_section(response)
            
            # Check for multiple paragraphs
            paragraphs = [p.strip() for p in lens_text.split('\n\n') if p.strip()]
            has_multiple_paragraphs = len(paragraphs) >= 2
            
            # Check for reasoning + example structure
            has_connector = len(self.detect_connectors(lens_text)) > 0
            
            # Check for duplication
            duplication_check = self.check_duplication(lens_text)
            
            # Check for all 3 sections
            has_lens = "**Strategic Thinking Lens**" in response
            has_prompts = "**Follow-up Prompts**" in response
            has_concepts = "**Concepts/Tools**" in response
            has_all_sections = has_lens and has_prompts and has_concepts
            
            flow_result = {
                "query": query,
                "has_multiple_paragraphs": has_multiple_paragraphs,
                "has_connector": has_connector,
                "has_duplication": duplication_check["has_duplication"],
                "duplication_score": duplication_check["duplication_score"],
                "has_all_sections": has_all_sections,
                "lens_text": lens_text[:300] + "..." if len(lens_text) > 300 else lens_text
            }
            
            flow_results.append(flow_result)
            
            print(f"Query: {query[:50]}...")
            print(f"  Multiple paragraphs: {'PASS' if has_multiple_paragraphs else 'FAIL'}")
            print(f"  Has connector: {'PASS' if has_connector else 'FAIL'}")
            print(f"  No duplication: {'PASS' if not duplication_check['has_duplication'] else 'FAIL'}")
            print(f"  All sections: {'PASS' if has_all_sections else 'FAIL'}")
            print("-" * 30)
        
        # Calculate success rates
        multiple_paragraphs_rate = sum(1 for r in flow_results if r["has_multiple_paragraphs"]) / len(flow_results) * 100
        connector_rate = sum(1 for r in flow_results if r["has_connector"]) / len(flow_results) * 100
        no_duplication_rate = sum(1 for r in flow_results if not r["has_duplication"]) / len(flow_results) * 100
        all_sections_rate = sum(1 for r in flow_results if r["has_all_sections"]) / len(flow_results) * 100
        
        print(f"\nFlow Quality Metrics:")
        print(f"Multiple paragraphs: {multiple_paragraphs_rate:.1f}%")
        print(f"Has connector: {connector_rate:.1f}%")
        print(f"No duplication: {no_duplication_rate:.1f}%")
        print(f"All sections present: {all_sections_rate:.1f}%")
        
        # Assertions
        assert multiple_paragraphs_rate >= 80, f"Too few responses have multiple paragraphs: {multiple_paragraphs_rate}%"
        assert connector_rate >= 80, f"Too few responses have connectors: {connector_rate}%"
        assert no_duplication_rate >= 70, f"Too much duplication: {100 - no_duplication_rate}%"
        assert all_sections_rate >= 90, f"Missing sections in too many responses: {100 - all_sections_rate}%"
        
        return flow_results
    
    def test_fallback_simulation(self):
        """Test fallback handling when GPT-3.5 fails"""
        print("\nTesting Fallback Simulation")
        print("=" * 35)
        
        # Test with a query that should trigger fallback
        query = "I need to decide between two job offers"
        
        # Simulate fallback by temporarily modifying the merge function
        original_merge_function = merge_and_extend_with_story
        
        def mock_fallback_merge(lens_text: str, story_text: str, domain_count: int) -> str:
            """Mock fallback merge function"""
            merged_lens = lens_text.strip() + "\n\nFor example, " + story_text.strip().capitalize()
            return merged_lens
        
        # Replace the function temporarily
        import query_engine
        query_engine.merge_and_extend_with_story = mock_fallback_merge
        
        try:
            response = process_query(query)
            lens_text = self.extract_lens_section(response)
            
            # Check fallback characteristics
            has_new_paragraph = "\n\n" in lens_text
            has_connector = "For example," in lens_text
            word_count = self.count_words(lens_text)
            is_within_tolerance = 90 <= word_count <= 150  # Broad tolerance for fallback
            
            print(f"Fallback response characteristics:")
            print(f"  New paragraph: {'PASS' if has_new_paragraph else 'FAIL'}")
            print(f"  Has connector: {'PASS' if has_connector else 'FAIL'}")
            print(f"  Word count: {word_count} (tolerance: 90-150)")
            print(f"  Within tolerance: {'PASS' if is_within_tolerance else 'FAIL'}")
            
            # Assertions
            assert has_new_paragraph, "Fallback should create new paragraph"
            assert has_connector, "Fallback should add connector"
            assert is_within_tolerance, f"Fallback word count out of tolerance: {word_count}"
            
            print("PASS: Fallback simulation successful!")
            
        finally:
            # Restore original function
            query_engine.merge_and_extend_with_story = original_merge_function
    
    def test_performance_monitoring(self):
        """Test performance metrics"""
        print("\nTesting Performance Monitoring")
        print("=" * 35)
        
        performance_results = []
        
        # Test with a variety of queries
        test_queries = [
            self.TEST_QUERIES_1_DOMAIN[0],
            self.TEST_QUERIES_2_DOMAINS[0],
            self.TEST_QUERIES_3_DOMAINS[0]
        ]
        
        for query in test_queries:
            start_time = time.time()
            response = process_query(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            word_count = self.count_words(response)
            
            performance_result = {
                "query": query,
                "response_time": response_time,
                "word_count": word_count,
                "words_per_second": word_count / response_time if response_time > 0 else 0
            }
            
            performance_results.append(performance_result)
            
            print(f"Query: {query[:50]}...")
            print(f"  Response time: {response_time:.2f}s")
            print(f"  Word count: {word_count}")
            print(f"  Words/second: {performance_result['words_per_second']:.1f}")
            print("-" * 30)
        
        # Calculate averages
        avg_response_time = sum(r["response_time"] for r in performance_results) / len(performance_results)
        avg_word_count = sum(r["word_count"] for r in performance_results) / len(performance_results)
        avg_words_per_second = sum(r["words_per_second"] for r in performance_results) / len(performance_results)
        
        print(f"\nPerformance Summary:")
        print(f"Average response time: {avg_response_time:.2f}s")
        print(f"Average word count: {avg_word_count:.1f}")
        print(f"Average words/second: {avg_words_per_second:.1f}")
        
        # Assertions
        assert avg_response_time < 8.0, f"Average response time too high: {avg_response_time:.2f}s"
        assert avg_word_count > 100, f"Average word count too low: {avg_word_count:.1f}"
        
        print("PASS: Performance requirements met!")
        return performance_results
    
    def test_regression_comparison(self):
        """Test regression against V1.6.6 Step 1"""
        print("\nTesting Regression Comparison")
        print("=" * 35)
        
        # Test that Step 2 refinements don't break Step 1 functionality
        query = "I need to decide between two job offers"
        
        response = process_query(query)
        
        # Check that all required sections are present
        required_sections = [
            "**Strategic Thinking Lens**",
            "**Follow-up Prompts**",
            "**Concepts/Tools**"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in response:
                missing_sections.append(section)
        
        # Check that Story section is properly merged (not present as separate section)
        has_separate_story = "**Story in Action**" in response
        
        print(f"Required sections present: {'PASS' if not missing_sections else 'FAIL'}")
        print(f"Story properly merged: {'PASS' if not has_separate_story else 'FAIL'}")
        
        if missing_sections:
            print(f"Missing sections: {missing_sections}")
        
        # Assertions
        assert not missing_sections, f"Missing required sections: {missing_sections}"
        assert not has_separate_story, "Story section should be merged, not separate"
        
        print("PASS: Regression test passed!")
        return {
            "missing_sections": missing_sections,
            "has_separate_story": has_separate_story
        }

def run_comprehensive_test_suite():
    """Run the comprehensive test suite and generate report"""
    print("Starting V1.6.6 Step 2 Refinements Test Suite")
    print("=" * 60)
    
    test_suite = TestV166Step2Refinements()
    
    # Run all tests
    results = {}
    
    try:
        results["word_count"] = test_suite.test_adaptive_word_count_compliance()
        results["connector_variety"] = test_suite.test_connector_variety()
        results["flow_quality"] = test_suite.test_smooth_flow_and_structure()
        results["fallback"] = test_suite.test_fallback_simulation()
        results["performance"] = test_suite.test_performance_monitoring()
        results["regression"] = test_suite.test_regression_comparison()
        
        # Generate comprehensive report
        print("\nCOMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Word count compliance summary
        print("\nWord Count Compliance:")
        for domain_type, data in results["word_count"].items():
            if domain_type != "compliance_rate":
                print(f"{domain_type.replace('_', ' ').title()}: {data['compliance_rate']:.1f}%")
        
        # Connector variety summary
        print(f"\nConnector Variety:")
        print(f"Unique connectors: {results['connector_variety']['unique_connectors']}")
        print(f"Most common percentage: {results['connector_variety']['most_common_percentage']:.1f}%")
        
        # Flow quality summary
        flow_results = results["flow_quality"]
        multiple_paragraphs_rate = sum(1 for r in flow_results if r["has_multiple_paragraphs"]) / len(flow_results) * 100
        connector_rate = sum(1 for r in flow_results if r["has_connector"]) / len(flow_results) * 100
        no_duplication_rate = sum(1 for r in flow_results if not r["has_duplication"]) / len(flow_results) * 100
        
        print(f"\nFlow Quality:")
        print(f"Multiple paragraphs: {multiple_paragraphs_rate:.1f}%")
        print(f"Has connector: {connector_rate:.1f}%")
        print(f"No duplication: {no_duplication_rate:.1f}%")
        
        # Performance summary
        avg_response_time = sum(r["response_time"] for r in results["performance"]) / len(results["performance"])
        print(f"\nPerformance:")
        print(f"Average response time: {avg_response_time:.2f}s")
        
        print("\nPASS: All tests completed successfully!")
        
        # Save detailed results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_filename = f"v166_step2_test_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed report saved to: {report_filename}")
        
    except Exception as e:
        print(f"FAIL: Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test_suite()
    sys.exit(0 if success else 1) 