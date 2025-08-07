#!/usr/bin/env python3
"""
V1.6.6 Step 2 Testing Framework Runner
=======================================

This script runs the comprehensive testing suite for V1.6.6 Step 2 refinements
and generates detailed reports with performance metrics, quality scores, and
regression analysis.
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime

def run_test_suite():
    """Run the comprehensive test suite"""
    print("V1.6.6 Step 2 Testing Framework")
    print("=" * 60)
    print("Testing Goals:")
    print("• Adaptive word count compliance")
    print("• Connector variety validation")
    print("• Smooth flow in 3-section format")
    print("• Performance monitoring")
    print("• Fallback handling")
    print("• Regression comparison")
    print()
    
    # Run the test suite
    try:
        result = subprocess.run([
            sys.executable, "tests/test_v166_step2_refinements.py"
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("PASS: Test suite completed successfully!")
            print("\nTest Output:")
            print(result.stdout)
            
            if result.stderr:
                print("\nWarnings/Errors:")
                print(result.stderr)
                
            return True, result.stdout
            
        else:
            print("FAIL: Test suite failed!")
            print("\nTest Output:")
            print(result.stdout)
            print("\nTest Errors:")
            print(result.stderr)
            return False, result.stdout
            
    except subprocess.TimeoutExpired:
        print("FAIL: Test suite timed out after 10 minutes")
        return False, "Test suite timed out"
    except Exception as e:
        print(f"FAIL: Test suite failed with error: {e}")
        return False, str(e)

def analyze_test_results():
    """Analyze test results and generate insights"""
    print("\nAnalyzing Test Results")
    print("=" * 40)
    
    # Look for test report files
    report_files = [f for f in os.listdir('.') if f.startswith('v166_step2_test_report_') and f.endswith('.json')]
    
    if not report_files:
        print("FAIL: No test report files found")
        return None
    
    # Get the most recent report
    latest_report = max(report_files, key=os.path.getctime)
    
    try:
        with open(latest_report, 'r') as f:
            results = json.load(f)
        
        print(f"Analyzing report: {latest_report}")
        
        # Generate insights
        insights = {
            "timestamp": datetime.now().isoformat(),
            "report_file": latest_report,
            "word_count_compliance": {},
            "connector_variety": {},
            "flow_quality": {},
            "performance": {},
            "overall_score": 0
        }
        
        # Word count compliance analysis
        if "word_count" in results:
            word_count_data = results["word_count"]
            for domain_type, data in word_count_data.items():
                if domain_type != "compliance_rate":
                    insights["word_count_compliance"][domain_type] = {
                        "compliance_rate": data.get("compliance_rate", 0),
                        "status": "PASS" if data.get("compliance_rate", 0) >= 60 else "FAIL"
                    }
        
        # Connector variety analysis
        if "connector_variety" in results:
            connector_data = results["connector_variety"]
            insights["connector_variety"] = {
                "unique_connectors": connector_data.get("unique_connectors", 0),
                "most_common_percentage": connector_data.get("most_common_percentage", 0),
                "status": "PASS" if (connector_data.get("unique_connectors", 0) >= 2 and 
                                      connector_data.get("most_common_percentage", 0) <= 60) else "FAIL"
            }
        
        # Flow quality analysis
        if "flow_quality" in results:
            flow_data = results["flow_quality"]
            if flow_data:
                multiple_paragraphs_rate = sum(1 for r in flow_data if r.get("has_multiple_paragraphs", False)) / len(flow_data) * 100
                connector_rate = sum(1 for r in flow_data if r.get("has_connector", False)) / len(flow_data) * 100
                no_duplication_rate = sum(1 for r in flow_data if not r.get("has_duplication", True)) / len(flow_data) * 100
                
                insights["flow_quality"] = {
                    "multiple_paragraphs_rate": multiple_paragraphs_rate,
                    "connector_rate": connector_rate,
                    "no_duplication_rate": no_duplication_rate,
                    "status": "PASS" if (multiple_paragraphs_rate >= 80 and connector_rate >= 80 and no_duplication_rate >= 70) else "FAIL"
                }
        
        # Performance analysis
        if "performance" in results:
            perf_data = results["performance"]
            if perf_data:
                avg_response_time = sum(r.get("response_time", 0) for r in perf_data) / len(perf_data)
                avg_word_count = sum(r.get("word_count", 0) for r in perf_data) / len(perf_data)
                
                insights["performance"] = {
                    "avg_response_time": avg_response_time,
                    "avg_word_count": avg_word_count,
                    "status": "PASS" if avg_response_time < 8.0 else "FAIL"
                }
        
        # Calculate overall score
        scores = []
        if insights["word_count_compliance"]:
            compliance_scores = [data["compliance_rate"] for data in insights["word_count_compliance"].values()]
            scores.append(sum(compliance_scores) / len(compliance_scores))
        
        if insights["connector_variety"]:
            connector_score = 100 if insights["connector_variety"]["status"] == "PASS" else 50
            scores.append(connector_score)
        
        if insights["flow_quality"]:
            flow_score = (insights["flow_quality"]["multiple_paragraphs_rate"] + 
                         insights["flow_quality"]["connector_rate"] + 
                         insights["flow_quality"]["no_duplication_rate"]) / 3
            scores.append(flow_score)
        
        if insights["performance"]:
            perf_score = 100 if insights["performance"]["status"] == "PASS" else 50
            scores.append(perf_score)
        
        insights["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        return insights
        
    except Exception as e:
        print(f"FAIL: Error analyzing results: {e}")
        return None

def generate_summary_report(insights):
    """Generate a summary report"""
    if not insights:
        return
    
    print("\nV1.6.6 Step 2 Test Summary Report")
    print("=" * 50)
    print(f"Generated: {insights['timestamp']}")
    print(f"Report File: {insights['report_file']}")
    print()
    
    # Word count compliance
    print("Word Count Compliance:")
    for domain_type, data in insights["word_count_compliance"].items():
        print(f"  {domain_type.replace('_', ' ').title()}: {data['compliance_rate']:.1f}% {data['status']}")
    
    print()
    
    # Connector variety
    print("Connector Variety:")
    connector_data = insights["connector_variety"]
    print(f"  Unique connectors: {connector_data['unique_connectors']}")
    print(f"  Most common percentage: {connector_data['most_common_percentage']:.1f}%")
    print(f"  Status: {connector_data['status']}")
    
    print()
    
    # Flow quality
    print("Flow Quality:")
    flow_data = insights["flow_quality"]
    print(f"  Multiple paragraphs: {flow_data['multiple_paragraphs_rate']:.1f}%")
    print(f"  Has connector: {flow_data['connector_rate']:.1f}%")
    print(f"  No duplication: {flow_data['no_duplication_rate']:.1f}%")
    print(f"  Status: {flow_data['status']}")
    
    print()
    
    # Performance
    print("Performance:")
    perf_data = insights["performance"]
    print(f"  Average response time: {perf_data['avg_response_time']:.2f}s")
    print(f"  Average word count: {perf_data['avg_word_count']:.1f}")
    print(f"  Status: {perf_data['status']}")
    
    print()
    
    # Overall score
    print("Overall Score:")
    print(f"  {insights['overall_score']:.1f}/100")
    
    if insights['overall_score'] >= 80:
        print("  EXCELLENT - All requirements met!")
    elif insights['overall_score'] >= 60:
        print("  GOOD - Most requirements met")
    else:
        print("  NEEDS IMPROVEMENT - Some requirements not met")
    
    print()
    
    # Save summary report
    summary_filename = f"v166_step2_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_filename, 'w') as f:
        json.dump(insights, f, indent=2)
    
    print(f"Summary report saved to: {summary_filename}")

def main():
    """Main function to run the testing framework"""
    print("V1.6.6 Step 2 Testing Framework")
    print("Validating adaptive word count, connector variety, and smooth flow")
    print()
    
    # Run test suite
    success, output = run_test_suite()
    
    if success:
        # Analyze results
        insights = analyze_test_results()
        
        # Generate summary report
        generate_summary_report(insights)
        
        print("\nTesting framework completed successfully!")
        print("Check the generated reports for detailed analysis.")
        
    else:
        print("\nTesting framework failed!")
        print("Please check the error messages above and fix any issues.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 