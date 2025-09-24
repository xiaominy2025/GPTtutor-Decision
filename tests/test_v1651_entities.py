#!/usr/bin/env python3
"""
Comprehensive Test Suite for Engent Labs Decision Query Engine V1.6.5.1
Entity Weighting, Word Count, and Answer Clarity Optimization

Test Categories:
1. Domain Coverage (behavioral, strategic, technical, negotiation)
2. Entity Dimension Coverage (timeframe, stakeholders, criteria, uncertainty/complexity)
3. Answer Quality Controls (word count, duplication, clarity)
4. Edge / Stress Tests (short, long, ambiguous, rare glossary terms)
5. Entity Weight Tuning Tests (different weight factors)
"""

import pytest
import json
import re
import sys
import os
from typing import Dict, List, Any, Tuple
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add parent directory to path to import query_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the query engine and clarity helpers
import query_engine
from tests.helpers.clarity import calculate_clarity_score, analyze_text_clarity, validate_clarity_threshold

class TestV1651EntityOptimization:
    """Comprehensive test suite for V1.6.5.1 entity weighting optimization"""
    
    def setup_method(self):
        """Setup test method with logging capabilities"""
        self.test_results = []
        self.start_time = datetime.now()
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment with feature flags"""
        # Store original settings
        self.original_use_enhanced_entities = getattr(query_engine, 'USE_ENHANCED_ENTITIES', False)
        self.original_entity_weight_factor = getattr(query_engine, 'ENTITY_WEIGHT_FACTOR', 0.0)
        
        # Set test defaults
        query_engine.USE_ENHANCED_ENTITIES = False
        query_engine.ENTITY_WEIGHT_FACTOR = 0.3
        
        yield
        
        # Restore original settings
        query_engine.USE_ENHANCED_ENTITIES = self.original_use_enhanced_entities
        query_engine.ENTITY_WEIGHT_FACTOR = self.original_entity_weight_factor
    
    def log_test_result(self, test_name: str, query: str, baseline_answer: str, enhanced_answer: str, 
                       baseline_metrics: Dict, enhanced_metrics: Dict, comparison: Dict):
        """Log detailed test results for reporting"""
        test_result = {
            'test_name': test_name,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'baseline_metrics': baseline_metrics,
            'enhanced_metrics': enhanced_metrics,
            'comparison': comparison,
            'entities_extracted': self.extract_entities_from_query(query),
            'concepts_tools': self.extract_concepts_from_answer(enhanced_answer)
        }
        self.test_results.append(test_result)
    
    def extract_entities_from_query(self, query: str) -> Dict[str, Any]:
        """Extract entities from query for logging purposes"""
        # This would be implemented when entity extraction is available
        return {
            'timeframe': [],
            'stakeholders': [],
            'criteria': [],
            'uncertainty': [],
            'complexity': []
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        if not self.test_results:
            return
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if not result['comparison'].get('quality_degradation', True))
        failed_tests = total_tests - passed_tests
        
        # Calculate average metrics
        avg_concept_accuracy = sum(result['comparison']['concept_accuracy'] for result in self.test_results) / total_tests
        avg_duplication_rate = sum(result['enhanced_metrics']['duplication_rate'] for result in self.test_results) / total_tests
        avg_clarity_score = sum(result['enhanced_metrics'].get('overall_clarity_score', 0) for result in self.test_results) / total_tests
        
        report = {
            'test_suite_info': {
                'name': 'V1.6.5.1 Entity Weighting Optimization Test Suite',
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0
            },
            'summary_metrics': {
                'average_concept_accuracy': avg_concept_accuracy,
                'average_duplication_rate': avg_duplication_rate,
                'average_clarity_score': avg_clarity_score
            },
            'detailed_results': self.test_results
        }
        
        # Save report to file
        report_path = 'reports/v1651_test_results.json'
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Test Report Generated: {report_path}")
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
        print(f"🎯 Average Concept Accuracy: {avg_concept_accuracy:.3f}")
        print(f"📏 Average Duplication Rate: {avg_duplication_rate:.3f}")
        print(f"✨ Average Clarity Score: {avg_clarity_score:.3f}")
    
    def teardown_method(self):
        """Generate test report after each test class"""
        self.generate_test_report()
    
    def validate_output(self, answer: str) -> Dict[str, Any]:
        """Validate output metrics for quality control"""
        metrics = {
            'word_counts': {},
            'duplication_rate': 0.0,
            'clarity_scores': {},
            'concept_accuracy': 0.0,
            'entity_influence': 0.0
        }
        
        # Extract sections
        sections = self.extract_sections(answer)
        
        # Calculate word counts and clarity scores per section
        for section_name, content in sections.items():
            word_count = len(content.split())
            metrics['word_counts'][section_name] = word_count
            
            # Calculate clarity score for each section
            clarity_score = calculate_clarity_score(content)
            metrics['clarity_scores'][section_name] = clarity_score
        
        # Calculate overall duplication rate
        all_text = ' '.join(sections.values()).lower()
        words = re.findall(r'\b\w+\b', all_text)
        unique_words = set(words)
        metrics['duplication_rate'] = (len(words) - len(unique_words)) / len(words) if words else 0.0
        
        # Calculate overall clarity score (average of section scores)
        if metrics['clarity_scores']:
            metrics['overall_clarity_score'] = sum(metrics['clarity_scores'].values()) / len(metrics['clarity_scores'])
        else:
            metrics['overall_clarity_score'] = 0.0
        
        return metrics
    
    def extract_sections(self, answer: str) -> Dict[str, str]:
        """Extract sections from answer"""
        sections = {}
        
        # Extract Strategic Thinking Lens
        lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*(.*?)(?=\*\*|\Z)', answer, re.DOTALL)
        if lens_match:
            sections['strategic_thinking_lens'] = lens_match.group(1).strip()
        
        # Extract Story in Action
        story_match = re.search(r'\*\*Story in Action\*\*(.*?)(?=\*\*|\Z)', answer, re.DOTALL)
        if story_match:
            sections['story_in_action'] = story_match.group(1).strip()
        
        # Extract Follow-up Prompts
        prompts_match = re.search(r'\*\*Follow-up Prompts\*\*(.*?)(?=\*\*|\Z)', answer, re.DOTALL)
        if prompts_match:
            sections['follow_up_prompts'] = prompts_match.group(1).strip()
        
        # Extract Concepts/Tools
        concepts_match = re.search(r'\*\*Concepts/Tools\*\*(.*?)(?=\*\*|\Z)', answer, re.DOTALL)
        if concepts_match:
            sections['concepts_tools'] = concepts_match.group(1).strip()
        
        return sections
    
    def extract_concepts_from_answer(self, answer: str) -> List[str]:
        """Extract concept names from Concepts/Tools section"""
        concepts = []
        concepts_match = re.search(r'\*\*Concepts/Tools\*\*(.*?)(?=\*\*|\Z)', answer, re.DOTALL)
        if concepts_match:
            content = concepts_match.group(1)
            # Extract concept names (before colons)
            concept_lines = re.findall(r'^([^:\n]+?):\s*', content, re.MULTILINE)
            concepts = [concept.strip() for concept in concept_lines]
        return concepts
    
    def compare_ab_results(self, query: str, baseline_answer: str, enhanced_answer: str) -> Dict[str, Any]:
        """Compare A/B results for entity weighting analysis"""
        baseline_metrics = self.validate_output(baseline_answer)
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        baseline_concepts = self.extract_concepts_from_answer(baseline_answer)
        enhanced_concepts = self.extract_concepts_from_answer(enhanced_answer)
        
        # Calculate concept accuracy
        concept_overlap = len(set(baseline_concepts) & set(enhanced_concepts))
        concept_accuracy = concept_overlap / len(baseline_concepts) if baseline_concepts else 1.0
        
        comparison = {
            'concept_accuracy': concept_accuracy,
            'word_count_changes': {},
            'duplication_changes': enhanced_metrics['duplication_rate'] - baseline_metrics['duplication_rate'],
            'clarity_changes': enhanced_metrics['clarity_score'] - baseline_metrics['clarity_score'],
            'quality_degradation': False
        }
        
        # Check word count changes
        for section in baseline_metrics['word_counts']:
            if section in enhanced_metrics['word_counts']:
                baseline_count = baseline_metrics['word_counts'][section]
                enhanced_count = enhanced_metrics['word_counts'][section]
                comparison['word_count_changes'][section] = enhanced_count - baseline_count
        
        # Determine quality degradation
        if (concept_accuracy < 0.95 or 
            comparison['duplication_changes'] > 0.08 or
            comparison['clarity_changes'] < -0.1):
            comparison['quality_degradation'] = True
        
        return comparison

    # ============================================================================
    # CATEGORY 1: DOMAIN COVERAGE TESTS (Behavioral, Strategic, Technical, Negotiation)
    # ============================================================================
    
    @pytest.mark.parametrize("query,expected_entities,word_count_range,duplication_threshold", [
        # Behavioral Domain Tests
        ("How do cognitive biases affect team decision making?", 
         ["stakeholders", "cognitive_behaviors"], 
         {"strategic_thinking_lens": (90, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What psychological factors influence investment decisions?", 
         ["stakeholders", "timeframe", "cognitive_behaviors"], 
         {"strategic_thinking_lens": (90, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How can leaders overcome confirmation bias in strategic planning?", 
         ["stakeholders", "timeframe", "cognitive_behaviors"], 
         {"strategic_thinking_lens": (90, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What role does anchoring bias play in salary negotiations?", 
         ["stakeholders", "criteria", "cognitive_behaviors"], 
         {"strategic_thinking_lens": (90, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do group dynamics affect organizational decision making?", 
         ["stakeholders", "cognitive_behaviors"], 
         {"strategic_thinking_lens": (90, 140), "story_in_action": (60, 80)},
         0.15),
        
        # Strategic Domain Tests
        ("Should we pursue cost leadership or differentiation strategy?", 
         ["stakeholders", "timeframe", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we analyze competitive positioning in our industry?", 
         ["stakeholders", "timeframe", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What factors should we consider for market entry strategy?", 
         ["stakeholders", "timeframe", "criteria", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we evaluate strategic partnerships?", 
         ["stakeholders", "criteria", "timeframe"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What's the best approach for portfolio management?", 
         ["stakeholders", "timeframe", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        # Technical Domain Tests
        ("How do we optimize production capacity using linear programming?", 
         ["stakeholders", "timeframe", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What forecasting method should we use for demand planning?", 
         ["stakeholders", "timeframe", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we model uncertainty in supply chain decisions?", 
         ["stakeholders", "timeframe", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What's the best approach for scenario analysis?", 
         ["stakeholders", "timeframe", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we use Monte Carlo simulation for risk assessment?", 
         ["stakeholders", "timeframe", "uncertainty"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        # Negotiation Domain Tests
        ("How do we determine our BATNA in supplier negotiations?", 
         ["stakeholders", "criteria", "timeframe"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What's our reservation point for this deal?", 
         ["stakeholders", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we find the ZOPA in partnership negotiations?", 
         ["stakeholders", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("What negotiation strategy should we use for this contract?", 
         ["stakeholders", "timeframe", "criteria"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
        
        ("How do we create value in integrative negotiations?", 
         ["stakeholders", "criteria", "timeframe"], 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)},
         0.15),
    ])
    def test_domain_coverage(self, query, expected_entities, word_count_range, duplication_threshold):
        """Test domain coverage across behavioral, strategic, technical, and negotiation domains"""
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate metrics
        baseline_metrics = self.validate_output(baseline_answer)
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count compliance
        for section, (min_words, max_words) in word_count_range.items():
            if section in enhanced_metrics['word_counts']:
                word_count = enhanced_metrics['word_counts'][section]
                assert min_words <= word_count <= max_words, f"{section}: {word_count} words (expected {min_words}-{max_words})"
        
        # Check duplication rate
        assert enhanced_metrics['duplication_rate'] < duplication_threshold, f"Duplication rate {enhanced_metrics['duplication_rate']:.3f} exceeds threshold {duplication_threshold}"
        
        # Check clarity scores for key sections
        for section in ['strategic_thinking_lens', 'story_in_action']:
            if section in enhanced_metrics['clarity_scores']:
                clarity_score = enhanced_metrics['clarity_scores'][section]
                assert clarity_score >= 0.6, f"{section}: clarity score {clarity_score:.3f} below 0.6 threshold"
        
        # Compare A/B results
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        assert comparison['concept_accuracy'] >= 0.95, f"Concept accuracy {comparison['concept_accuracy']:.3f} below 95% threshold"
        assert not comparison['quality_degradation'], "Quality degradation detected"

    # ============================================================================
    # CATEGORY 2: ENTITY DIMENSION COVERAGE TESTS
    # ============================================================================
    
    @pytest.mark.parametrize("query,entity_dimensions,validation_metrics", [
        # Timeframe Entity Tests (4 tests)
        ("What's our short-term strategy for market entry?", 
         {"timeframe": "short_term"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we plan for long-term sustainability?", 
         {"timeframe": "long_term"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What immediate actions should we take?", 
         {"timeframe": "immediate"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("When should we implement this strategy?", 
         {"timeframe": "ambiguous"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        # Stakeholder Entity Tests (4 tests)
        ("How do we align employees in this decision?", 
         {"stakeholders": ["employees"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What do our customers think about this strategy?", 
         {"stakeholders": ["customers"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we satisfy our investors?", 
         {"stakeholders": ["investors"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What do regulators require for this decision?", 
         {"stakeholders": ["regulators"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        # Criteria Entity Tests (4 tests)
        ("What financial criteria should guide our choice?", 
         {"criteria": ["financial"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we evaluate strategic criteria?", 
         {"criteria": ["strategic"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What operational factors should we consider?", 
         {"criteria": ["operational"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we assess risk criteria?", 
         {"criteria": ["risk"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        # Uncertainty/Complexity Entity Tests (4 tests)
        ("How do we handle high uncertainty in this market?", 
         {"uncertainty": "high", "complexity": "high"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What if demand is unpredictable?", 
         {"uncertainty": "medium", "complexity": "medium"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we manage complex trade-offs?", 
         {"complexity": "high", "uncertainty": "low"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What if this is a simple decision?", 
         {"complexity": "low", "uncertainty": "low"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        # Mixed Entity Tests (4 tests)
        ("How do we handle short-term employee concerns with high uncertainty?", 
         {"timeframe": "short_term", "stakeholders": ["employees"], "uncertainty": "high"}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What financial criteria matter for long-term investor satisfaction?", 
         {"criteria": ["financial"], "timeframe": "long_term", "stakeholders": ["investors"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("How do we manage operational complexity for immediate customer needs?", 
         {"criteria": ["operational"], "complexity": "high", "timeframe": "immediate", "stakeholders": ["customers"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
        
        ("What strategic risks do regulators see in our approach?", 
         {"criteria": ["strategic", "risk"], "stakeholders": ["regulators"]}, 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80)}),
    ])
    def test_entity_dimension_coverage(self, query, entity_dimensions, validation_metrics):
        """Test entity dimension coverage (timeframe, stakeholders, criteria, uncertainty/complexity)"""
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate metrics
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count compliance
        for section, (min_words, max_words) in validation_metrics.items():
            if section in enhanced_metrics['word_counts']:
                word_count = enhanced_metrics['word_counts'][section]
                assert min_words <= word_count <= max_words, f"{section}: {word_count} words (expected {min_words}-{max_words})"
        
        # Check clarity scores for key sections
        for section in ['strategic_thinking_lens', 'story_in_action']:
            if section in enhanced_metrics['clarity_scores']:
                clarity_score = enhanced_metrics['clarity_scores'][section]
                assert clarity_score >= 0.6, f"{section}: clarity score {clarity_score:.3f} below 0.6 threshold"
        
        # Compare A/B results
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        assert comparison['concept_accuracy'] >= 0.95, f"Concept accuracy {comparison['concept_accuracy']:.3f} below 95% threshold"
        assert not comparison['quality_degradation'], "Quality degradation detected"

    # ============================================================================
    # CATEGORY 3: ANSWER QUALITY CONTROLS TESTS
    # ============================================================================
    
    @pytest.mark.parametrize("query,quality_requirements", [
        # Word Count Control Tests
        ("How do we optimize production capacity?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("What's the best forecasting method?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("How do we handle supply chain uncertainty?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("What negotiation strategy should we use?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("How do cognitive biases affect decisions?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        # Duplication Control Tests
        ("What's our competitive advantage?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("How do we evaluate strategic options?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("What factors influence investment decisions?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        # Clarity Control Tests
        ("How do we assess risk in this decision?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("What's the best approach for scenario planning?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("How do we balance multiple objectives?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
        
        ("What criteria should guide our choice?", 
         {"strategic_thinking_lens": (100, 140), "story_in_action": (60, 80), "duplication_threshold": 0.08}),
    ])
    def test_answer_quality_controls(self, query, quality_requirements):
        """Test answer quality controls (word count, duplication, clarity)"""
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate metrics
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count compliance
        for section, (min_words, max_words) in quality_requirements.items():
            if section in enhanced_metrics['word_counts']:
                word_count = enhanced_metrics['word_counts'][section]
                assert min_words <= word_count <= max_words, f"{section}: {word_count} words (expected {min_words}-{max_words})"
        
        # Check duplication rate
        duplication_threshold = quality_requirements.get('duplication_threshold', 0.08)
        assert enhanced_metrics['duplication_rate'] < duplication_threshold, f"Duplication rate {enhanced_metrics['duplication_rate']:.3f} exceeds threshold {duplication_threshold}"
        
        # Check clarity scores for key sections
        for section in ['strategic_thinking_lens', 'story_in_action']:
            if section in enhanced_metrics['clarity_scores']:
                clarity_score = enhanced_metrics['clarity_scores'][section]
                assert clarity_score >= 0.6, f"{section}: clarity score {clarity_score:.3f} below 0.6 threshold"
        
        # Compare A/B results
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        assert comparison['concept_accuracy'] >= 0.95, f"Concept accuracy {comparison['concept_accuracy']:.3f} below 95% threshold"
        assert not comparison['quality_degradation'], "Quality degradation detected"

    # ============================================================================
    # CATEGORY 4: EDGE / STRESS TESTS
    # ============================================================================
    
    @pytest.mark.parametrize("query,test_type,expected_behavior", [
        # Short Query Tests
        ("Help", "short_query", "graceful_handling"),
        ("What?", "short_query", "graceful_handling"),
        ("Decision", "short_query", "graceful_handling"),
        
        # Long Query Tests
        ("How do we optimize production capacity while considering multiple stakeholders including suppliers, customers, and employees, while also managing uncertainty in demand forecasting and balancing cost efficiency with quality standards, all while maintaining competitive positioning in a dynamic market environment with changing regulations and technological disruptions?", 
         "long_query", "comprehensive_analysis"),
        
        ("What's the best approach for strategic planning when we need to consider short-term operational efficiency, long-term market positioning, stakeholder alignment across multiple departments, risk management for various scenarios, resource allocation constraints, competitive dynamics, technological trends, regulatory compliance, and organizational culture factors?", 
         "long_query", "comprehensive_analysis"),
        
        # Ambiguous Query Tests
        ("I need to decide", "ambiguous_query", "clarification_handling"),
        ("What should I do?", "ambiguous_query", "clarification_handling"),
        ("Help me choose", "ambiguous_query", "clarification_handling"),
        
        # Rare Glossary Terms Tests
        ("How do we use Monte Carlo simulation for risk assessment?", 
         "rare_glossary", "concept_extraction"),
        ("What's the value of ZOPA in negotiations?", 
         "rare_glossary", "concept_extraction"),
        ("How do we apply prospect theory to investment decisions?", 
         "rare_glossary", "concept_extraction"),
        
        # Mixed Domain Tests
        ("How do cognitive biases affect our Monte Carlo simulation results?", 
         "mixed_domain", "balanced_analysis"),
        ("What's our BATNA for this linear optimization problem?", 
         "mixed_domain", "balanced_analysis"),
        ("How do we use game theory in scenario analysis?", 
         "mixed_domain", "balanced_analysis"),
        
        # Stress Tests
        ("How do we optimize production capacity using linear programming while considering Monte Carlo simulation for uncertainty, applying game theory for competitive analysis, using prospect theory for risk assessment, implementing BATNA analysis for negotiations, and balancing stakeholder alignment across multiple departments?", 
         "stress_test", "comprehensive_handling"),
        
        ("What's the best approach for strategic planning when we need to consider cognitive biases, competitive positioning, supply chain optimization, risk management, stakeholder alignment, technological disruption, regulatory compliance, and organizational culture, all while using decision trees, sensitivity analysis, and scenario planning?", 
         "stress_test", "comprehensive_handling"),
    ])
    def test_edge_stress_cases(self, query, test_type, expected_behavior):
        """Test edge cases and stress scenarios"""
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate that both answers are generated
        assert baseline_answer, "Baseline answer should be generated"
        assert enhanced_answer, "Enhanced answer should be generated"
        
        # Extract sections
        baseline_sections = self.extract_sections(baseline_answer)
        enhanced_sections = self.extract_sections(enhanced_answer)
        
        # Validate structure
        required_sections = ['strategic_thinking_lens', 'story_in_action', 'follow_up_prompts', 'concepts_tools']
        for section in required_sections:
            assert section in enhanced_sections, f"Missing required section: {section}"
        
        # Validate metrics
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count limits (relaxed for stress tests)
        if test_type == "stress_test":
            assert enhanced_metrics['word_counts'].get('strategic_thinking_lens', 0) <= 200, "Strategic Thinking Lens too long"
            assert enhanced_metrics['word_counts'].get('story_in_action', 0) <= 120, "Story in Action too long"
        else:
            assert enhanced_metrics['word_counts'].get('strategic_thinking_lens', 0) <= 160, "Strategic Thinking Lens too long"
            assert enhanced_metrics['word_counts'].get('story_in_action', 0) <= 100, "Story in Action too long"
        
        # Check duplication rate (relaxed for stress tests)
        max_duplication = 0.10 if test_type == "stress_test" else 0.08
        assert enhanced_metrics['duplication_rate'] < max_duplication, f"Duplication rate {enhanced_metrics['duplication_rate']:.3f} exceeds threshold {max_duplication}"
        
        # Check clarity scores (relaxed for stress tests)
        min_clarity = 0.5 if test_type == "stress_test" else 0.6
        for section in ['strategic_thinking_lens', 'story_in_action']:
            if section in enhanced_metrics['clarity_scores']:
                clarity_score = enhanced_metrics['clarity_scores'][section]
                assert clarity_score >= min_clarity, f"{section}: clarity score {clarity_score:.3f} below {min_clarity} threshold"
        
        # Compare A/B results (relaxed for stress tests)
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        min_accuracy = 0.90 if test_type == "stress_test" else 0.95
        assert comparison['concept_accuracy'] >= min_accuracy, f"Concept accuracy {comparison['concept_accuracy']:.3f} below {min_accuracy} threshold"

    # ============================================================================
    # ENTITY WEIGHTING OPTIMIZATION TESTS
    # ============================================================================
    
    @pytest.mark.parametrize("weight_factor", [0.1, 0.2, 0.3])
    def test_entity_weight_factor_optimization(self, weight_factor):
        """Test different entity weight factors for optimization"""
        query = "How do we optimize production capacity while considering stakeholder interests?"
        
        # Set entity weight factor
        query_engine.ENTITY_WEIGHT_FACTOR = weight_factor
        
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate metrics
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count compliance
        assert 120 <= enhanced_metrics['word_counts'].get('strategic_thinking_lens', 0) <= 140, "Strategic Thinking Lens word count out of range"
        assert 60 <= enhanced_metrics['word_counts'].get('story_in_action', 0) <= 80, "Story in Action word count out of range"
        
        # Check duplication rate
        assert enhanced_metrics['duplication_rate'] < 0.08, f"Duplication rate {enhanced_metrics['duplication_rate']:.3f} exceeds 8% threshold"
        
        # Compare A/B results
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        assert comparison['concept_accuracy'] >= 0.95, f"Concept accuracy {comparison['concept_accuracy']:.3f} below 95% threshold"
        assert not comparison['quality_degradation'], "Quality degradation detected"
    
    def test_entity_weight_factor_gradual_increase(self):
        """Test gradual entity weight factor increase"""
        query = "How do we evaluate strategic options using decision analysis?"
        
        results = {}
        
        for weight_factor in [0.0, 0.1, 0.2, 0.3]:
            query_engine.ENTITY_WEIGHT_FACTOR = weight_factor
            query_engine.USE_ENHANCED_ENTITIES = True
            
            answer = query_engine.process_query(query, {"course_id": "decision"})
            metrics = self.validate_output(answer)
            
            results[weight_factor] = {
                'word_counts': metrics['word_counts'],
                'duplication_rate': metrics['duplication_rate'],
                'clarity_scores': metrics['clarity_scores']
            }
        
        # Validate that quality is maintained across weight factors
        for weight_factor, result in results.items():
            # Check word count compliance
            assert 120 <= result['word_counts'].get('strategic_thinking_lens', 0) <= 140, f"Weight {weight_factor}: Strategic Thinking Lens word count out of range"
            assert 60 <= result['word_counts'].get('story_in_action', 0) <= 80, f"Weight {weight_factor}: Story in Action word count out of range"
            
            # Check duplication rate
            assert result['duplication_rate'] < 0.08, f"Weight {weight_factor}: Duplication rate {result['duplication_rate']:.3f} exceeds 8% threshold"
            
            # Check clarity scores for key sections
            for section in ['strategic_thinking_lens', 'story_in_action']:
                if section in result['clarity_scores']:
                    clarity_score = result['clarity_scores'][section]
                    assert clarity_score >= 0.6, f"Weight {weight_factor}: {section} clarity score {clarity_score:.3f} below 0.6 threshold"

    # ============================================================================
    # ENTITY WEIGHT TUNING TESTS
    # ============================================================================
    
    @pytest.mark.parametrize("weight_factor", [0.1, 0.2, 0.3])
    def test_entity_weight_factor_tuning(self, weight_factor):
        """Test different entity weight factors for optimization"""
        query = "How do we optimize production capacity while considering stakeholder interests?"
        
        # Set entity weight factor
        query_engine.ENTITY_WEIGHT_FACTOR = weight_factor
        
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate metrics
        enhanced_metrics = self.validate_output(enhanced_answer)
        
        # Check word count compliance
        assert 120 <= enhanced_metrics['word_counts'].get('strategic_thinking_lens', 0) <= 140, "Strategic Thinking Lens word count out of range"
        assert 60 <= enhanced_metrics['word_counts'].get('story_in_action', 0) <= 80, "Story in Action word count out of range"
        
        # Check duplication rate
        assert enhanced_metrics['duplication_rate'] < 0.08, f"Duplication rate {enhanced_metrics['duplication_rate']:.3f} exceeds 8% threshold"
        
        # Check clarity scores for key sections
        for section in ['strategic_thinking_lens', 'story_in_action']:
            if section in enhanced_metrics['clarity_scores']:
                clarity_score = enhanced_metrics['clarity_scores'][section]
                assert clarity_score >= 0.6, f"{section}: clarity score {clarity_score:.3f} below 0.6 threshold"
        
        # Compare A/B results
        comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
        assert comparison['concept_accuracy'] >= 0.95, f"Concept accuracy {comparison['concept_accuracy']:.3f} below 95% threshold"
        assert not comparison['quality_degradation'], "Quality degradation detected"
    
    def test_entity_weight_factor_gradual_increase(self):
        """Test gradual entity weight factor increase"""
        query = "How do we evaluate strategic options using decision analysis?"
        
        results = {}
        
        for weight_factor in [0.0, 0.1, 0.2, 0.3]:
            query_engine.ENTITY_WEIGHT_FACTOR = weight_factor
            query_engine.USE_ENHANCED_ENTITIES = True
            
            answer = query_engine.process_query(query, {"course_id": "decision"})
            metrics = self.validate_output(answer)
            
            results[weight_factor] = {
                'word_counts': metrics['word_counts'],
                'duplication_rate': metrics['duplication_rate'],
                'clarity_scores': metrics['clarity_scores']
            }
        
        # Validate that quality is maintained across weight factors
        for weight_factor, result in results.items():
            # Check word count compliance
            assert 120 <= result['word_counts'].get('strategic_thinking_lens', 0) <= 140, f"Weight {weight_factor}: Strategic Thinking Lens word count out of range"
            assert 60 <= result['word_counts'].get('story_in_action', 0) <= 80, f"Weight {weight_factor}: Story in Action word count out of range"
            
            # Check duplication rate
            assert result['duplication_rate'] < 0.08, f"Weight {weight_factor}: Duplication rate {result['duplication_rate']:.3f} exceeds 8% threshold"
            
            # Check clarity scores for key sections
            for section in ['strategic_thinking_lens', 'story_in_action']:
                if section in result['clarity_scores']:
                    clarity_score = result['clarity_scores'][section]
                    assert clarity_score >= 0.6, f"Weight {weight_factor}: {section} clarity score {clarity_score:.3f} below 0.6 threshold"

    # ============================================================================
    # COMPREHENSIVE A/B TESTING SUITE
    # ============================================================================
    
    def test_comprehensive_ab_comparison(self):
        """Comprehensive A/B testing with detailed metrics"""
        test_queries = [
            "How do we optimize production capacity?",
            "What's the best forecasting method?",
            "How do we handle supply chain uncertainty?",
            "What negotiation strategy should we use?",
            "How do cognitive biases affect decisions?",
            "What's our competitive advantage?",
            "How do we evaluate strategic options?",
            "What factors influence investment decisions?",
            "How do we assess risk in this decision?",
            "What's the best approach for scenario planning?"
        ]
        
        results = {
            'queries_improved': 0,
            'queries_degraded': 0,
            'queries_stable': 0,
            'total_concept_accuracy': 0.0,
            'total_duplication_change': 0.0,
            'total_clarity_change': 0.0
        }
        
        for query in test_queries:
            # Test with enhanced entities disabled
            query_engine.USE_ENHANCED_ENTITIES = False
            baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
            
            # Test with enhanced entities enabled
            query_engine.USE_ENHANCED_ENTITIES = True
            enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
            
            # Compare results
            comparison = self.compare_ab_results(query, baseline_answer, enhanced_answer)
            
            # Track results
            if comparison['concept_accuracy'] >= 0.95 and not comparison['quality_degradation']:
                if comparison['clarity_changes'] > 0.08:
                    results['queries_improved'] += 1
                else:
                    results['queries_stable'] += 1
            else:
                results['queries_degraded'] += 1
            
            results['total_concept_accuracy'] += comparison['concept_accuracy']
            results['total_duplication_change'] += comparison['duplication_changes']
            results['total_clarity_change'] += comparison['clarity_changes']
        
        # Calculate averages
        num_queries = len(test_queries)
        results['avg_concept_accuracy'] = results['total_concept_accuracy'] / num_queries
        results['avg_duplication_change'] = results['total_duplication_change'] / num_queries
        results['avg_clarity_change'] = results['total_clarity_change'] / num_queries
        
        # Validate overall results
        assert results['avg_concept_accuracy'] >= 0.95, f"Average concept accuracy {results['avg_concept_accuracy']:.3f} below 95% threshold"
        assert results['queries_degraded'] <= 1, f"Too many degraded queries: {results['queries_degraded']}"
        assert results['avg_duplication_change'] < 0.02, f"Average duplication increase {results['avg_duplication_change']:.3f} too high"
        
        # Log results for analysis
        print(f"\nA/B Testing Results:")
        print(f"Queries improved: {results['queries_improved']}")
        print(f"Queries stable: {results['queries_stable']}")
        print(f"Queries degraded: {results['queries_degraded']}")
        print(f"Average concept accuracy: {results['avg_concept_accuracy']:.3f}")
        print(f"Average duplication change: {results['avg_duplication_change']:.3f}")
        print(f"Average clarity change: {results['avg_clarity_change']:.3f}")

    # ============================================================================
    # API COMPATIBILITY TESTS
    # ============================================================================
    
    def test_api_compatibility(self):
        """Test API compatibility and JSON output format"""
        query = "How do we optimize production capacity?"
        
        # Test with enhanced entities disabled
        query_engine.USE_ENHANCED_ENTITIES = False
        baseline_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Test with enhanced entities enabled
        query_engine.USE_ENHANCED_ENTITIES = True
        enhanced_answer = query_engine.process_query(query, {"course_id": "decision"})
        
        # Validate that both answers have the same structure
        baseline_sections = self.extract_sections(baseline_answer)
        enhanced_sections = self.extract_sections(enhanced_answer)
        
        # Check that all required sections are present
        required_sections = ['strategic_thinking_lens', 'story_in_action', 'follow_up_prompts', 'concepts_tools']
        for section in required_sections:
            assert section in baseline_sections, f"Baseline missing section: {section}"
            assert section in enhanced_sections, f"Enhanced missing section: {section}"
        
        # Validate JSON compatibility (if API returns JSON)
        # This would be tested in actual API integration tests
        
        # Validate that enhanced answer doesn't break existing functionality
        assert len(enhanced_answer) > 0, "Enhanced answer should not be empty"
        assert "Strategic Thinking Lens" in enhanced_answer, "Enhanced answer should contain Strategic Thinking Lens"
        assert "Story in Action" in enhanced_answer, "Enhanced answer should contain Story in Action"
        assert "Follow-up Prompts" in enhanced_answer, "Enhanced answer should contain Follow-up Prompts"
        assert "Concepts/Tools" in enhanced_answer, "Enhanced answer should contain Concepts/Tools"

if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short"]) 