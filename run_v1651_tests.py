#!/usr/bin/env python3
"""
V1.6.5.1 Comprehensive Test Suite Runner
Executes entity weighting optimization tests and generates detailed report
"""

import pytest
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def run_comprehensive_test_suite():
    """Run the comprehensive V1.6.5.1 test suite"""
    print("🚀 V1.6.5.1 COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test file path
    test_file = "tests/test_v1651_entities.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Run tests with detailed output
    print("📋 Running comprehensive test suite...")
    print("-" * 40)
    
    # Run pytest with verbose output
    result = pytest.main([
        test_file,
        "-v",
        "--tb=short",
        "--durations=10",
        "--maxfail=5"
    ])
    
    print()
    print("=" * 60)
    print("📊 TEST EXECUTION COMPLETE")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result == 0:
        print("✅ All tests passed successfully!")
        return True
    else:
        print(f"❌ Some tests failed (exit code: {result})")
        return False

def generate_test_summary():
    """Generate a summary of test categories and expected outcomes"""
    print("\n📋 TEST CATEGORIES SUMMARY")
    print("=" * 60)
    
    categories = {
        "Domain Coverage": {
            "description": "Behavioral, Strategic, Technical, Negotiation domains",
            "test_count": 20,
            "success_criteria": [
                "Word count compliance (120-140 words for Strategic Thinking Lens)",
                "Word count compliance (60-80 words for Story in Action)",
                "Duplication rate < 5%",
                "Concept accuracy >= 95%",
                "No quality degradation"
            ]
        },
        "Entity Dimension Coverage": {
            "description": "Timeframe, Stakeholders, Criteria, Uncertainty/Complexity",
            "test_count": 12,
            "success_criteria": [
                "Entity extraction accuracy",
                "Entity integration quality",
                "Word count compliance",
                "Concept accuracy >= 95%"
            ]
        },
        "Answer Quality Controls": {
            "description": "Word count, duplication, clarity optimization",
            "test_count": 12,
            "success_criteria": [
                "Strategic Thinking Lens: 120-140 words",
                "Story in Action: 60-80 words",
                "Duplication rate < 5%",
                "Clarity score >= 0.6",
                "Concept accuracy >= 95%"
            ]
        },
        "Edge / Stress Tests": {
            "description": "Short, long, ambiguous, rare glossary terms",
            "test_count": 12,
            "success_criteria": [
                "Graceful handling of edge cases",
                "Comprehensive analysis for complex queries",
                "Concept extraction for rare terms",
                "Balanced analysis for mixed domains",
                "Stress test handling with relaxed thresholds"
            ]
        },
        "Entity Weighting Optimization": {
            "description": "Testing different weight factors (0.1, 0.2, 0.3)",
            "test_count": 4,
            "success_criteria": [
                "Quality maintained across weight factors",
                "Word count compliance at all weights",
                "Duplication rate < 5% at all weights",
                "Clarity score >= 0.6 at all weights"
            ]
        },
        "Comprehensive A/B Testing": {
            "description": "Detailed comparison of baseline vs enhanced",
            "test_count": 1,
            "success_criteria": [
                "Average concept accuracy >= 95%",
                "Queries degraded <= 1",
                "Average duplication change < 0.02",
                "Detailed metrics logging"
            ]
        },
        "API Compatibility": {
            "description": "JSON output format and structure validation",
            "test_count": 1,
            "success_criteria": [
                "Same structure as baseline",
                "All required sections present",
                "No breaking changes to API",
                "Enhanced functionality preserved"
            ]
        }
    }
    
    total_tests = sum(cat["test_count"] for cat in categories.values())
    
    for category, details in categories.items():
        print(f"\n🎯 {category}")
        print(f"   Description: {details['description']}")
        print(f"   Test Count: {details['test_count']}")
        print("   Success Criteria:")
        for criterion in details['success_criteria']:
            print(f"     • {criterion}")
    
    print(f"\n📊 TOTAL: {total_tests} test cases across 7 categories")
    print("=" * 60)

def validate_test_requirements():
    """Validate that all requirements for testing are met"""
    print("\n🔍 VALIDATING TEST REQUIREMENTS")
    print("=" * 60)
    
    requirements = {
        "query_engine.py": "Main query engine file",
        "tests/test_v1651_entities.py": "Comprehensive test suite",
        "vector_index.faiss": "Vector index for semantic search",
        "metadata.json": "Document metadata",
        "requirements.txt": "Python dependencies"
    }
    
    missing_files = []
    
    for file_path, description in requirements.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (MISSING)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All requirements met!")
        return True

def main():
    """Main test execution function"""
    print("🚀 V1.6.5.1 ENTITY WEIGHTING OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print("Testing entity weighting, word count, and answer clarity optimization")
    print("while maintaining stable quality and API compatibility.")
    print()
    
    # Validate requirements
    if not validate_test_requirements():
        print("\n❌ Test requirements not met. Please ensure all required files are present.")
        return False
    
    # Generate test summary
    generate_test_summary()
    
    # Run comprehensive test suite
    success = run_comprehensive_test_suite()
    
    if success:
        print("\n🎉 V1.6.5.1 TEST SUITE COMPLETED SUCCESSFULLY!")
        print("✅ Entity weighting optimization validated")
        print("✅ Word count controls working properly")
        print("✅ Answer clarity maintained")
        print("✅ API compatibility preserved")
        print("✅ Quality degradation prevented")
        print("\n📋 Ready to proceed with V1.6.5.1 implementation!")
    else:
        print("\n❌ V1.6.5.1 TEST SUITE FAILED!")
        print("Please review test failures and fix issues before proceeding.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 