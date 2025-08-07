#!/usr/bin/env python3
"""
Focused Automated Testing and Fixing Process
Runs core functionality tests and automatically fixes issues without user intervention.
"""

import os
import sys
import json
import time
import traceback
import re
from typing import Dict, List, Any
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def log_message(message: str, level: str = "INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(filepath)

def clean_json_content(content: str) -> str:
    """Remove JavaScript-style comments and fix JSON formatting"""
    # Remove single-line comments (// ...)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    
    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove trailing commas before closing brackets/braces
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n', '\n', content)
    
    return content.strip()

def read_json_file(filepath: str) -> Dict:
    """Read and parse a JSON file with comment cleaning"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        cleaned_content = clean_json_content(content)
        
        return json.loads(cleaned_content)
    except Exception as e:
        log_message(f"Failed to read {filepath}: {e}", "ERROR")
        return {}

def write_json_file(filepath: str, data: Dict):
    """Write data to a JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log_message(f"Successfully wrote {filepath}")
    except Exception as e:
        log_message(f"Failed to write {filepath}: {e}", "ERROR")

def test_core_functionality() -> Dict:
    """Test core functionality without pytest"""
    log_message("Testing core functionality...")
    
    test_results = {
        "imports": {"success": False, "error": None},
        "data_loading": {"success": False, "error": None},
        "concept_extraction": {"success": False, "error": None},
        "query_processing": {"success": False, "error": None},
        "syntax_check": {"success": False, "error": None}
    }
    
    # Test 1: Import functionality
    log_message("Testing imports...")
    try:
        import sentence_transformers
        import faiss
        import spacy
        import openai
        import numpy as np
        test_results["imports"]["success"] = True
        log_message("✅ All imports successful")
    except ImportError as e:
        test_results["imports"]["error"] = str(e)
        log_message(f"❌ Import error: {e}", "ERROR")
    
    # Test 2: Data loading
    log_message("Testing data loading...")
    try:
        from query_engine import load_data_lazily
        load_data_lazily()
        test_results["data_loading"]["success"] = True
        log_message("✅ Data loading successful")
    except Exception as e:
        test_results["data_loading"]["error"] = str(e)
        log_message(f"❌ Data loading error: {e}", "ERROR")
    
    # Test 3: Concept extraction
    log_message("Testing concept extraction...")
    try:
        from query_engine import get_top_ranked_concepts
        
        test_queries = [
            "How do I reduce groupthink in team decisions?",
            "What tools help evaluate uncertain outcomes?",
            "How can I model risks in product launch?"
        ]
        
        concept_results = []
        for query in test_queries:
            try:
                concepts = get_top_ranked_concepts(query, top_k=3)
                concept_results.append({
                    "query": query,
                    "concepts": [c[0] for c in concepts],
                    "success": len(concepts) > 0
                })
            except Exception as e:
                concept_results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        successful_concepts = sum(1 for r in concept_results if r["success"])
        test_results["concept_extraction"]["success"] = successful_concepts > 0
        test_results["concept_extraction"]["details"] = concept_results
        
        if successful_concepts > 0:
            log_message(f"✅ Concept extraction: {successful_concepts}/{len(concept_results)} successful")
        else:
            log_message("❌ Concept extraction failed", "ERROR")
            
    except Exception as e:
        test_results["concept_extraction"]["error"] = str(e)
        log_message(f"❌ Concept extraction error: {e}", "ERROR")
    
    # Test 4: Query processing
    log_message("Testing query processing...")
    try:
        from query_engine import process_query
        
        test_queries = [
            "I need to decide between two job offers",
            "How do I optimize my supply chain?",
            "What are the risks of this investment?"
        ]
        
        processing_results = []
        for query in test_queries:
            try:
                start_time = time.time()
                response = process_query(query)
                processing_time = time.time() - start_time
                
                # Check response structure
                has_strategic_lens = "**Strategic Thinking Lens**" in response
                has_story = "**Story in Action**" in response
                has_followup = "**Follow-up Prompts**" in response
                has_concepts = "**Concepts/Tools**" in response
                
                processing_results.append({
                    "query": query,
                    "processing_time": processing_time,
                    "response_length": len(response),
                    "has_strategic_lens": has_strategic_lens,
                    "has_story": has_story,
                    "has_followup": has_followup,
                    "has_concepts": has_concepts,
                    "success": all([has_strategic_lens, has_story, has_followup, has_concepts])
                })
                
            except Exception as e:
                processing_results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        successful_queries = sum(1 for r in processing_results if r["success"])
        test_results["query_processing"]["success"] = successful_queries > 0
        test_results["query_processing"]["details"] = processing_results
        
        if successful_queries > 0:
            log_message(f"✅ Query processing: {successful_queries}/{len(processing_results)} successful")
        else:
            log_message("❌ Query processing failed", "ERROR")
            
    except Exception as e:
        test_results["query_processing"]["error"] = str(e)
        log_message(f"❌ Query processing error: {e}", "ERROR")
    
    # Test 5: Syntax check
    log_message("Testing syntax...")
    try:
        import py_compile
        py_compile.compile("query_engine.py", doraise=True)
        test_results["syntax_check"]["success"] = True
        log_message("✅ Syntax check passed")
    except Exception as e:
        test_results["syntax_check"]["error"] = str(e)
        log_message(f"❌ Syntax error: {e}", "ERROR")
    
    return test_results

def analyze_test_results(test_results: Dict) -> Dict:
    """Analyze test results and identify issues"""
    log_message("Analyzing test results...")
    
    analysis = {
        "overall_status": "PASS",
        "issues": [],
        "recommendations": [],
        "metrics": {}
    }
    
    # Count successful tests
    successful_tests = sum(1 for test_name, result in test_results.items() if result.get("success", False))
    total_tests = len(test_results)
    
    analysis["metrics"]["test_success_rate"] = successful_tests / total_tests if total_tests > 0 else 0
    analysis["metrics"]["successful_tests"] = successful_tests
    analysis["metrics"]["total_tests"] = total_tests
    
    # Check each test
    for test_name, result in test_results.items():
        if not result.get("success", False):
            analysis["issues"].append(f"{test_name}: {result.get('error', 'Unknown error')}")
    
    # Determine overall status
    if successful_tests < total_tests:
        analysis["overall_status"] = "FAIL"
        analysis["issues"].append(f"Only {successful_tests}/{total_tests} tests passed")
    
    # Generate recommendations
    if "imports" in test_results and not test_results["imports"]["success"]:
        analysis["recommendations"].append("Install missing dependencies")
    
    if "data_loading" in test_results and not test_results["data_loading"]["success"]:
        analysis["recommendations"].append("Check data files and vector index")
    
    if "concept_extraction" in test_results and not test_results["concept_extraction"]["success"]:
        analysis["recommendations"].append("Review concept extraction logic")
    
    if "query_processing" in test_results and not test_results["query_processing"]["success"]:
        analysis["recommendations"].append("Check query processing pipeline")
    
    if "syntax_check" in test_results and not test_results["syntax_check"]["success"]:
        analysis["recommendations"].append("Fix syntax errors in query_engine.py")
    
    return analysis

def auto_fix_issues(analysis: Dict, test_results: Dict) -> Dict:
    """Automatically fix identified issues"""
    log_message("Starting automatic fixes...")
    
    fixes_applied = []
    
    # Fix 1: Check for missing data files
    required_files = [
        "vector_index.faiss",
        "metadata.json",
        "courses/decision/course_config.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        log_message(f"Missing required files: {missing_files}", "WARNING")
        fixes_applied.append(f"Missing files: {missing_files}")
    
    # Fix 2: Check for undefined functions in query_engine.py
    log_message("Checking for undefined functions...")
    try:
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Functions that might be referenced but not defined
        undefined_functions = [
            "extract_enhanced_entities",
            "detect_followup_query", 
            "generate_concept_tooltips",
            "generate_domain_aware_followup_prompt",
            "extract_application_fields"
        ]
        
        missing_functions = []
        for func_name in undefined_functions:
            if func_name in content and f"def {func_name}" not in content:
                missing_functions.append(func_name)
        
        if missing_functions:
            log_message(f"Missing functions: {missing_functions}", "WARNING")
            fixes_applied.append(f"Missing functions: {missing_functions}")
            
            # Try to add stub functions
            log_message("Adding stub functions...")
            stub_functions = []
            for func_name in missing_functions:
                if func_name == "extract_enhanced_entities":
                    stub_functions.append("""
def extract_enhanced_entities(query: str) -> Dict:
    \"\"\"Extract enhanced entities from query (stub implementation)\"\"\"
    return {
        "stakeholders": {},
        "timeframe": {},
        "criteria": {},
        "uncertainty": {},
        "complexity": {},
        "confidence": 0.0,
        "entity_neutral": True
    }
""")
                elif func_name == "detect_followup_query":
                    stub_functions.append("""
def detect_followup_query(query: str) -> bool:
    \"\"\"Detect if query is a follow-up (stub implementation)\"\"\"
    followup_indicators = ["what about", "how about", "and", "also", "further", "more"]
    return any(indicator in query.lower() for indicator in followup_indicators)
""")
                elif func_name == "generate_concept_tooltips":
                    stub_functions.append("""
def generate_concept_tooltips(concepts: List[Tuple[str, str]]) -> List[Dict]:
    \"\"\"Generate concept tooltips (stub implementation)\"\"\"
    return [{"term": concept[0], "definition": concept[1]} for concept in concepts]
""")
                elif func_name == "generate_domain_aware_followup_prompt":
                    stub_functions.append("""
def generate_domain_aware_followup_prompt(query: str, domain: str) -> str:
    \"\"\"Generate domain-aware followup prompt (stub implementation)\"\"\"
    return f"Consider the {domain} aspects of: {query}"
""")
                elif func_name == "extract_application_fields":
                    stub_functions.append("""
def extract_application_fields(query: str) -> List[str]:
    \"\"\"Extract application fields from query (stub implementation)\"\"\"
    return ["general"]
""")
            
            # Add stub functions to query_engine.py
            if stub_functions:
                try:
                    with open("query_engine.py", "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Add stub functions before the last function
                    stub_code = "\n".join(stub_functions)
                    content += f"\n\n# Stub functions for missing implementations\n{stub_code}"
                    
                    with open("query_engine.py", "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    log_message("✅ Added stub functions")
                    fixes_applied.append("Added stub functions for missing implementations")
                    
                except Exception as e:
                    log_message(f"❌ Failed to add stub functions: {e}", "ERROR")
                    fixes_applied.append(f"Failed to add stub functions: {e}")
        
    except Exception as e:
        log_message(f"Error checking functions: {e}", "ERROR")
        fixes_applied.append(f"Function check error: {e}")
    
    return {
        "fixes_applied": fixes_applied,
        "success": len(fixes_applied) == 0
    }

def generate_test_report(test_results: Dict, analysis: Dict, fixes: Dict) -> str:
    """Generate a comprehensive test report"""
    log_message("Generating test report...")
    
    report = f"""
# Focused Automated Testing Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Status: {analysis['overall_status']}

## Test Results Summary

### Core Functionality Tests
- Test Success Rate: {analysis['metrics']['test_success_rate']:.1%}
- Successful Tests: {analysis['metrics']['successful_tests']}/{analysis['metrics']['total_tests']}

### Individual Test Results
"""
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
        error = result.get("error", "")
        report += f"- {test_name}: {status}"
        if error:
            report += f" ({error})"
        report += "\n"
    
    report += f"""
## Issues Identified
"""
    
    for issue in analysis.get("issues", []):
        report += f"- {issue}\n"
    
    report += f"""
## Recommendations
"""
    
    for rec in analysis.get("recommendations", []):
        report += f"- {rec}\n"
    
    report += f"""
## Fixes Applied
"""
    
    for fix in fixes.get("fixes_applied", []):
        report += f"- {fix}\n"
    
    if not fixes.get("fixes_applied"):
        report += "- No fixes needed\n"
    
    report += f"""
## Detailed Results

### Test Details
"""
    
    for test_name, result in test_results.items():
        report += f"""
#### {test_name}
- Status: {'PASS' if result.get('success', False) else 'FAIL'}
"""
        if "error" in result and result["error"]:
            report += f"- Error: {result['error']}\n"
        
        if "details" in result:
            details = result["details"]
            if isinstance(details, list):
                for i, detail in enumerate(details):
                    report += f"- Test {i+1}: {'PASS' if detail.get('success', False) else 'FAIL'}\n"
                    if "error" in detail:
                        report += f"  - Error: {detail['error']}\n"
    
    return report

def main():
    """Main focused automated testing and fixing process"""
    log_message("Starting focused automated testing and fixing process...")
    
    # Step 1: Run core functionality tests
    log_message("Step 1: Running core functionality tests...")
    test_results = test_core_functionality()
    
    # Step 2: Analyze results
    log_message("Step 2: Analyzing results...")
    analysis = analyze_test_results(test_results)
    
    # Step 3: Auto-fix issues
    log_message("Step 3: Auto-fixing issues...")
    fixes = auto_fix_issues(analysis, test_results)
    
    # Step 4: Generate report
    log_message("Step 4: Generating report...")
    report = generate_test_report(test_results, analysis, fixes)
    
    # Step 5: Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"focused_test_report_{timestamp}.md"
    
    try:
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        log_message(f"Report saved to {report_filename}")
    except Exception as e:
        log_message(f"Failed to save report: {e}", "ERROR")
    
    # Step 6: Save detailed results
    results_filename = f"focused_test_results_{timestamp}.json"
    detailed_results = {
        "timestamp": timestamp,
        "test_results": test_results,
        "analysis": analysis,
        "fixes": fixes
    }
    
    try:
        write_json_file(results_filename, detailed_results)
        log_message(f"Detailed results saved to {results_filename}")
    except Exception as e:
        log_message(f"Failed to save detailed results: {e}", "ERROR")
    
    # Step 7: Final summary
    log_message("Focused automated testing and fixing process completed!")
    log_message(f"Overall Status: {analysis['overall_status']}")
    log_message(f"Issues Found: {len(analysis.get('issues', []))}")
    log_message(f"Fixes Applied: {len(fixes.get('fixes_applied', []))}")
    
    return analysis["overall_status"] == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 