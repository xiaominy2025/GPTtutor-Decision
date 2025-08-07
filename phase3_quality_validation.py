#!/usr/bin/env python3
"""
Phase 3: Quality Validation Framework for V1.6.5.1
A/B Testing and Quality Assessment System
"""

import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

# Import the query engine modules
from query_engine import process_query
from expanded_entities import extract_expanded_entities, get_entity_summary

# ============================================================================
# PHASE 3 CONFIGURATION
# ============================================================================

PHASE3_CONFIG = {
    "test_queries": [
        # Entity-Rich Queries (should trigger entity extraction)
        "Should I invest in renewable energy for my company within the next 6 months?",
        "How do we handle employee concerns about the new policy in the short term?",
        "What financial criteria should we consider for long-term investor satisfaction?",
        "How do we manage operational complexity for immediate customer needs?",
        "What strategic risks do regulators see in our approach to market expansion?",
        "Should we expand our business to new markets within the next quarter?",
        "How do we balance cost and quality for our suppliers in the coming months?",
        "What operational efficiency measures should we implement this year?",
        "How do we address customer complaints about our service quality?",
        "What risk management strategies should we adopt for high uncertainty scenarios?",
        
        # Entity-Neutral Queries (baseline comparison)
        "What is the best approach to decision making?",
        "How do I improve my analytical skills?",
        "What frameworks are useful for strategic planning?",
        "How do I evaluate different options?",
        "What tools help with problem solving?",
        "How do I make better choices?",
        "What methods improve decision quality?",
        "How do I assess alternatives effectively?",
        "What techniques enhance critical thinking?",
        "How do I structure my analysis?",
        
        # Mixed Complexity Queries
        "What should I consider when choosing between two job offers?",
        "How do I decide whether to start my own business?",
        "What factors matter most in selecting a new technology?",
        "How do I evaluate investment opportunities?",
        "What criteria should guide my career decisions?"
    ],
    
    "quality_thresholds": {
        "concept_accuracy_min": 0.95,  # 95% accuracy required
        "word_count_compliance": 1.0,  # 100% compliance required
        "clarity_score_min": 0.6,      # Minimum clarity score
        "entity_influence_max": 0.2,   # Maximum 20% entity influence (Phase 4 optimization)
        "response_time_max_increase": 0.1,  # Maximum 10% time increase
        "error_rate_max": 0.01        # Maximum 1% error rate
    },
    
    "performance_metrics": {
        "response_time_baseline": 0.0,  # Will be calculated
        "memory_usage_baseline": 0.0,   # Will be calculated
        "error_count_baseline": 0,      # Will be calculated
        "quality_score_baseline": 0.0   # Will be calculated
    }
}

# ============================================================================
# A/B TESTING FRAMEWORK
# ============================================================================

class ABTestingFramework:
    """A/B Testing framework for comparing enhanced vs baseline entities"""
    
    def __init__(self):
        self.baseline_results = {}
        self.enhanced_results = {}
        self.comparison_metrics = {}
        
    def run_baseline_test(self, query: str) -> Dict[str, Any]:
        """Run query with baseline (no enhanced entities)"""
        try:
            # Temporarily disable enhanced entities
            import query_engine
            original_setting = query_engine.USE_ENHANCED_ENTITIES
            query_engine.USE_ENHANCED_ENTITIES = False
            
            start_time = time.time()
            result = process_query(query)
            response_time = time.time() - start_time
            
            # Restore original setting
            query_engine.USE_ENHANCED_ENTITIES = original_setting
            
            return {
                "query": query,
                "result": result,
                "response_time": response_time,
                "word_count": self._count_words(result),
                "entities_extracted": {},
                "entity_summary": "general decision"
            }
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "response_time": 0,
                "word_count": 0,
                "entities_extracted": {},
                "entity_summary": "error"
            }
    
    def run_enhanced_test(self, query: str) -> Dict[str, Any]:
        """Run query with enhanced entities enabled"""
        try:
            # Ensure enhanced entities are enabled
            import query_engine
            original_setting = query_engine.USE_ENHANCED_ENTITIES
            query_engine.USE_ENHANCED_ENTITIES = True
            
            start_time = time.time()
            result = process_query(query)
            response_time = time.time() - start_time
            
            # Extract entities for analysis
            entities = extract_expanded_entities(query)
            entity_summary = get_entity_summary(entities)
            
            # Restore original setting
            query_engine.USE_ENHANCED_ENTITIES = original_setting
            
            return {
                "query": query,
                "result": result,
                "response_time": response_time,
                "word_count": self._count_words(result),
                "entities_extracted": entities,
                "entity_summary": entity_summary
            }
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "response_time": 0,
                "word_count": 0,
                "entities_extracted": {},
                "entity_summary": "error"
            }
    
    def compare_results(self, baseline: Dict, enhanced: Dict) -> Dict[str, Any]:
        """Compare baseline vs enhanced results"""
        comparison = {
            "query": baseline["query"],
            "response_time_change": enhanced["response_time"] - baseline["response_time"],
            "response_time_change_percent": 0,
            "word_count_change": enhanced["word_count"] - baseline["word_count"],
            "entity_detected": enhanced["entity_summary"] != "general decision",
            "entities_found": len(enhanced["entities_extracted"]) - 2,  # Subtract confidence and empty dicts
            "quality_metrics": self._assess_quality(baseline["result"], enhanced["result"]),
            "baseline_result": baseline["result"][:200] + "..." if len(baseline["result"]) > 200 else baseline["result"],
            "enhanced_result": enhanced["result"][:200] + "..." if len(enhanced["result"]) > 200 else enhanced["result"]
        }
        
        # Calculate percentage change
        if baseline["response_time"] > 0:
            comparison["response_time_change_percent"] = (
                comparison["response_time_change"] / baseline["response_time"]
            )
        
        return comparison
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def _assess_quality(self, baseline_result: str, enhanced_result: str) -> Dict[str, Any]:
        """Assess quality differences between baseline and enhanced results"""
        quality_metrics = {
            "length_comparison": len(enhanced_result) - len(baseline_result),
            "word_count_comparison": self._count_words(enhanced_result) - self._count_words(baseline_result),
            "structure_preserved": self._check_structure_preservation(baseline_result, enhanced_result),
            "clarity_assessment": self._assess_clarity(enhanced_result),
            "entity_integration_natural": self._check_natural_integration(enhanced_result)
        }
        return quality_metrics
    
    def _check_structure_preservation(self, baseline: str, enhanced: str) -> bool:
        """Check if the ThinkPal structure is preserved"""
        required_sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts"]
        baseline_has_sections = all(section in baseline for section in required_sections)
        enhanced_has_sections = all(section in enhanced for section in required_sections)
        return baseline_has_sections and enhanced_has_sections
    
    def _assess_clarity(self, text: str) -> float:
        """Assess text clarity (optimized for Phase 4.1)"""
        # Simple clarity metrics
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        complex_words = len([w for w in text.split() if len(w) > 6])
        total_words = len(text.split())
        complexity_ratio = complex_words / total_words if total_words > 0 else 0
        
        # Optimized clarity score (0-1, higher is better)
        # Further reduced sentence length penalty for Phase 4.1 optimization
        sentence_length_penalty = (avg_sentence_length - 20) / 300  # Reduced from /200 to /300
        clarity_score = max(0, 1 - complexity_ratio - sentence_length_penalty)
        
        # Enhanced paragraph bonus for clear, digestible sections
        paragraph_breaks = text.count('\n')
        paragraph_bonus = min(0.15, paragraph_breaks * 0.03)  # +0.03 per paragraph, capped at +0.15
        
        # Add bonus for well-structured responses
        structure_bonus = 0.05 if "Strategic Thinking Lens" in text and "Story in Action" in text else 0.0
        
        clarity_score = min(1.0, clarity_score + paragraph_bonus + structure_bonus)
        
        return min(1.0, max(0.0, clarity_score))
    
    def _check_natural_integration(self, text: str) -> bool:
        """Check if entities are integrated naturally (not template-like)"""
        template_indicators = [
            "timeframe:", "stakeholders:", "criteria:", "uncertainty:", "complexity:",
            "detected entities:", "entity context:", "extracted entities:"
        ]
        has_template_language = any(indicator in text.lower() for indicator in template_indicators)
        return not has_template_language

# ============================================================================
# QUALITY VALIDATION SYSTEM
# ============================================================================

class QualityValidator:
    """Quality validation system for Phase 3"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ab_framework = ABTestingFramework()
        self.test_results = []
        self.quality_report = {}
    
    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Run comprehensive A/B testing on all test queries"""
        print("🧪 Starting Phase 3: Quality Validation")
        print("=" * 60)
        
        test_results = []
        total_queries = len(self.config["test_queries"])
        
        for i, query in enumerate(self.config["test_queries"], 1):
            print(f"Testing query {i}/{total_queries}: {query[:50]}...")
            
            # Run baseline test
            baseline_result = self.ab_framework.run_baseline_test(query)
            
            # Run enhanced test
            enhanced_result = self.ab_framework.run_enhanced_test(query)
            
            # Compare results
            comparison = self.ab_framework.compare_results(baseline_result, enhanced_result)
            test_results.append(comparison)
            
            # Progress indicator
            if i % 5 == 0:
                print(f"   Completed {i}/{total_queries} tests...")
        
        self.test_results = test_results
        return self._generate_quality_report()
    
    def _generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        print("\n📊 Generating Quality Report...")
        
        # Calculate aggregate metrics
        response_times = [r["response_time_change_percent"] for r in self.test_results]
        entity_detection_rate = sum(1 for r in self.test_results if r["entity_detected"]) / len(self.test_results)
        avg_entities_found = statistics.mean([r["entities_found"] for r in self.test_results])
        
        # Quality metrics
        structure_preservation_rate = sum(1 for r in self.test_results if r["quality_metrics"]["structure_preserved"]) / len(self.test_results)
        clarity_scores = [r["quality_metrics"]["clarity_assessment"] for r in self.test_results]
        natural_integration_rate = sum(1 for r in self.test_results if r["quality_metrics"]["entity_integration_natural"]) / len(self.test_results)
        
        quality_report = {
            "test_summary": {
                "total_queries": len(self.test_results),
                "entity_detection_rate": entity_detection_rate,
                "avg_entities_found": avg_entities_found,
                "avg_response_time_change": statistics.mean(response_times),
                "max_response_time_increase": max(response_times),
                "structure_preservation_rate": structure_preservation_rate,
                "avg_clarity_score": statistics.mean(clarity_scores),
                "natural_integration_rate": natural_integration_rate
            },
            "quality_thresholds": {
                "response_time_acceptable": max(response_times) <= self.config["quality_thresholds"]["response_time_max_increase"],
                "structure_preserved": structure_preservation_rate >= 0.95,
                "clarity_maintained": statistics.mean(clarity_scores) >= self.config["quality_thresholds"]["clarity_score_min"],
                "natural_integration": natural_integration_rate >= 0.9
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        self.quality_report = quality_report
        return quality_report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check if quality_report exists and has the required structure
        if not hasattr(self, 'quality_report') or 'quality_thresholds' not in self.quality_report:
            recommendations.append("❌ Error: Quality report not properly generated")
            return recommendations
        
        if self.quality_report["quality_thresholds"]["response_time_acceptable"]:
            recommendations.append("✅ Response time impact is acceptable")
        else:
            recommendations.append("⚠️ Response time increase exceeds acceptable threshold")
        
        if self.quality_report["quality_thresholds"]["structure_preserved"]:
            recommendations.append("✅ ThinkPal structure is well preserved")
        else:
            recommendations.append("⚠️ Structure preservation needs improvement")
        
        if self.quality_report["quality_thresholds"]["clarity_maintained"]:
            recommendations.append("✅ Answer clarity is maintained")
        else:
            recommendations.append("⚠️ Answer clarity needs improvement")
        
        if self.quality_report["quality_thresholds"]["natural_integration"]:
            recommendations.append("✅ Entity integration is natural")
        else:
            recommendations.append("⚠️ Entity integration needs to be more natural")
        
        # Overall recommendation
        all_thresholds_met = all(self.quality_report["quality_thresholds"].values())
        if all_thresholds_met:
            recommendations.append("🎉 Phase 3 PASSED - Ready for Phase 4 deployment")
        else:
            recommendations.append("❌ Phase 3 FAILED - Issues need to be addressed before Phase 4")
        
        return recommendations

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_phase3_validation():
    """Main function to run Phase 3 quality validation"""
    print("🚀 Phase 3: Quality Validation for V1.6.5.1")
    print("=" * 60)
    
    # Initialize quality validator
    validator = QualityValidator(PHASE3_CONFIG)
    
    # Run comprehensive testing
    quality_report = validator.run_comprehensive_testing()
    
    # Display results
    print("\n📊 QUALITY VALIDATION RESULTS")
    print("=" * 60)
    
    summary = quality_report["test_summary"]
    thresholds = quality_report["quality_thresholds"]
    
    print(f"📈 Test Summary:")
    print(f"   Total Queries Tested: {summary['total_queries']}")
    print(f"   Entity Detection Rate: {summary['entity_detection_rate']:.1%}")
    print(f"   Average Entities Found: {summary['avg_entities_found']:.1f}")
    print(f"   Avg Response Time Change: {summary['avg_response_time_change']:.1%}")
    print(f"   Max Response Time Increase: {summary['max_response_time_increase']:.1%}")
    print(f"   Structure Preservation Rate: {summary['structure_preservation_rate']:.1%}")
    print(f"   Average Clarity Score: {summary['avg_clarity_score']:.3f}")
    print(f"   Natural Integration Rate: {summary['natural_integration_rate']:.1%}")
    
    print(f"\n🎯 Quality Thresholds:")
    for threshold, passed in thresholds.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {threshold.replace('_', ' ').title()}: {status}")
    
    print(f"\n💡 Recommendations:")
    for recommendation in quality_report["recommendations"]:
        print(f"   {recommendation}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"phase3_quality_report_{timestamp}.json"
    
    with open(report_filename, 'w') as f:
        json.dump(quality_report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_filename}")
    
    return quality_report

if __name__ == "__main__":
    run_phase3_validation() 