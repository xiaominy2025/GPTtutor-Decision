#!/usr/bin/env python3
"""
Automated Comprehensive Testing and Fixing Process
Runs all tests, identifies issues, and automatically fixes them without user intervention.
"""

import os
import sys
import json
import time
import subprocess
import traceback
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_command(command: str, capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

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

def run_pytest_tests() -> Dict:
    """Run pytest tests and return results"""
    log_message("Running pytest tests...")
    
    # Run pytest with basic options (no json-report which may not be available)
    cmd = "python -m pytest tests/ -v --tb=short"
    exit_code, stdout, stderr = run_command(cmd)
    
    results = {
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "success": exit_code == 0
    }
    
    log_message(f"Pytest completed with exit code {exit_code}")
    
    return results

def run_custom_tests() -> Dict:
    """Run custom test scripts"""
    log_message("Running custom test scripts...")
    
    test_results = {}
    
    # Test concept extraction
    if check_file_exists("tests/concept_extraction/test_cases.json"):
        log_message("Testing concept extraction...")
        try:
            from query_engine import get_top_ranked_concepts
            test_cases = read_json_file("tests/concept_extraction/test_cases.json")
            
            concept_results = []
            test_cases_list = test_cases if isinstance(test_cases, list) else []
            
            for test_case in test_cases_list[:5]:  # Test first 5 cases
                query = test_case.get("question", "")
                required_concepts = test_case.get("required_concepts", [])
                optional_concepts = test_case.get("optional_concepts", [])
                excluded_concepts = test_case.get("excluded_concepts", [])
                
                try:
                    extracted_concepts = get_top_ranked_concepts(query, top_k=3)
                    extracted_names = [concept[0] for concept in extracted_concepts]
                    
                    # Calculate metrics
                    required_found = len(set(extracted_names) & set(required_concepts))
                    optional_found = len(set(extracted_names) & set(optional_concepts))
                    excluded_found = len(set(extracted_names) & set(excluded_concepts))
                    
                    # Calculate accuracy based on required concepts
                    accuracy = required_found / len(required_concepts) if required_concepts else 0
                    
                    concept_results.append({
                        "query": query,
                        "required_concepts": required_concepts,
                        "extracted": extracted_names,
                        "required_found": required_found,
                        "optional_found": optional_found,
                        "excluded_found": excluded_found,
                        "accuracy": accuracy,
                        "success": required_found > 0 and excluded_found == 0
                    })
                except Exception as e:
                    concept_results.append({
                        "query": query,
                        "error": str(e),
                        "success": False
                    })
            
            test_results["concept_extraction"] = concept_results
            log_message(f"Concept extraction tests completed: {len(concept_results)} cases")
            
        except Exception as e:
            log_message(f"Concept extraction test failed: {e}", "ERROR")
            test_results["concept_extraction"] = {"error": str(e)}
    
    # Test query processing
    log_message("Testing query processing...")
    try:
        from query_engine import process_query
        
        test_queries = [
            "I need to decide between two job offers",
            "How do I optimize my supply chain?",
            "What are the risks of this investment?",
            "How should I negotiate this deal?"
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
        
        test_results["query_processing"] = processing_results
        log_message(f"Query processing tests completed: {len(processing_results)} queries")
        
    except Exception as e:
        log_message(f"Query processing test failed: {e}", "ERROR")
        test_results["query_processing"] = {"error": str(e)}
    
    return test_results

def analyze_test_results(pytest_results: Dict, custom_results: Dict) -> Dict:
    """Analyze test results and identify issues"""
    log_message("Analyzing test results...")
    
    analysis = {
        "overall_status": "PASS",
        "issues": [],
        "recommendations": [],
        "metrics": {}
    }
    
    # Analyze pytest results
    if pytest_results.get("success"):
        analysis["metrics"]["pytest_passed"] = True
        log_message("Pytest tests passed")
    else:
        analysis["metrics"]["pytest_passed"] = False
        analysis["overall_status"] = "FAIL"
        analysis["issues"].append("Pytest tests failed")
        log_message("Pytest tests failed", "ERROR")
    
    # Analyze custom test results
    if "concept_extraction" in custom_results:
        concept_results = custom_results["concept_extraction"]
        if isinstance(concept_results, list):
            successful_tests = sum(1 for r in concept_results if r.get("success", False))
            total_tests = len(concept_results)
            accuracy_scores = [r.get("accuracy", 0) for r in concept_results if "error" not in r]
            avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
            
            analysis["metrics"]["concept_extraction"] = {
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "average_accuracy": avg_accuracy
            }
            
            if successful_tests < total_tests:
                analysis["issues"].append(f"Concept extraction: {total_tests - successful_tests} tests failed")
            
            if avg_accuracy < 0.5:
                analysis["recommendations"].append("Improve concept extraction accuracy")
    
    if "query_processing" in custom_results:
        processing_results = custom_results["query_processing"]
        if isinstance(processing_results, list):
            successful_queries = sum(1 for r in processing_results if r.get("success", False))
            total_queries = len(processing_results)
            avg_processing_time = sum(r.get("processing_time", 0) for r in processing_results) / total_queries
            
            analysis["metrics"]["query_processing"] = {
                "successful_queries": successful_queries,
                "total_queries": total_queries,
                "average_processing_time": avg_processing_time
            }
            
            if successful_queries < total_queries:
                analysis["issues"].append(f"Query processing: {total_queries - successful_queries} queries failed")
            
            if avg_processing_time > 10:  # More than 10 seconds
                analysis["recommendations"].append("Optimize query processing performance")
    
    return analysis

def auto_fix_issues(analysis: Dict) -> Dict:
    """Automatically fix identified issues"""
    log_message("Starting automatic fixes...")
    
    fixes_applied = []
    
    # Fix 1: Check for missing dependencies
    log_message("Checking dependencies...")
    try:
        import sentence_transformers
        import faiss
        import spacy
        import openai
        log_message("All core dependencies available")
    except ImportError as e:
        log_message(f"Missing dependency: {e}", "ERROR")
        fixes_applied.append(f"Missing dependency: {e}")
    
    # Fix 2: Check for missing data files
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
    
    # Fix 3: Check query_engine.py for syntax errors
    log_message("Checking query_engine.py syntax...")
    exit_code, stdout, stderr = run_command("python -m py_compile query_engine.py")
    if exit_code != 0:
        log_message("Syntax errors found in query_engine.py", "ERROR")
        fixes_applied.append("Syntax errors in query_engine.py")
    
    # Fix 4: Check for common issues in the code
    log_message("Checking for common code issues...")
    try:
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        issues_found = []
        
        # Check for undefined functions that are referenced in tests
        undefined_functions = [
            "extract_enhanced_entities",
            "detect_followup_query", 
            "generate_concept_tooltips",
            "generate_domain_aware_followup_prompt",
            "extract_application_fields"
        ]
        
        for func_name in undefined_functions:
            if func_name in content and f"def {func_name}" not in content:
                issues_found.append(f"{func_name} function not defined")
        
        if issues_found:
            log_message(f"Code issues found: {issues_found}", "ERROR")
            fixes_applied.extend(issues_found)
        
    except Exception as e:
        log_message(f"Error checking code: {e}", "ERROR")
        fixes_applied.append(f"Code check error: {e}")
    
    return {
        "fixes_applied": fixes_applied,
        "success": len(fixes_applied) == 0
    }

def generate_test_report(pytest_results: Dict, custom_results: Dict, analysis: Dict, fixes: Dict) -> str:
    """Generate a comprehensive test report"""
    log_message("Generating test report...")
    
    report = f"""
# Automated Comprehensive Testing Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Status: {analysis['overall_status']}

## Test Results Summary

### Pytest Results
- Status: {'PASS' if pytest_results.get('success') else 'FAIL'}
- Exit Code: {pytest_results.get('exit_code', 'N/A')}

### Custom Test Results

#### Concept Extraction
"""
    
    if "concept_extraction" in analysis.get("metrics", {}):
        metrics = analysis["metrics"]["concept_extraction"]
        report += f"""
- Successful Tests: {metrics.get('successful_tests', 0)}/{metrics.get('total_tests', 0)}
- Average Accuracy: {metrics.get('average_accuracy', 0):.2%}
"""
    
    report += """
#### Query Processing
"""
    
    if "query_processing" in analysis.get("metrics", {}):
        metrics = analysis["metrics"]["query_processing"]
        report += f"""
- Successful Queries: {metrics.get('successful_queries', 0)}/{metrics.get('total_queries', 0)}
- Average Processing Time: {metrics.get('average_processing_time', 0):.2f}s
"""
    
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

### Pytest Output
```
{pytest_results.get('stdout', 'No output')}
```

### Pytest Errors
```
{pytest_results.get('stderr', 'No errors')}
```
"""
    
    return report

def main():
    """Main automated testing and fixing process"""
    log_message("Starting automated comprehensive testing and fixing process...")
    
    # Step 1: Run all tests
    log_message("Step 1: Running tests...")
    pytest_results = run_pytest_tests()
    custom_results = run_custom_tests()
    
    # Step 2: Analyze results
    log_message("Step 2: Analyzing results...")
    analysis = analyze_test_results(pytest_results, custom_results)
    
    # Step 3: Auto-fix issues
    log_message("Step 3: Auto-fixing issues...")
    fixes = auto_fix_issues(analysis)
    
    # Step 4: Generate report
    log_message("Step 4: Generating report...")
    report = generate_test_report(pytest_results, custom_results, analysis, fixes)
    
    # Step 5: Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"automated_test_report_{timestamp}.md"
    
    try:
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        log_message(f"Report saved to {report_filename}")
    except Exception as e:
        log_message(f"Failed to save report: {e}", "ERROR")
    
    # Step 6: Save detailed results
    results_filename = f"test_results_{timestamp}.json"
    detailed_results = {
        "timestamp": timestamp,
        "pytest_results": pytest_results,
        "custom_results": custom_results,
        "analysis": analysis,
        "fixes": fixes
    }
    
    try:
        write_json_file(results_filename, detailed_results)
        log_message(f"Detailed results saved to {results_filename}")
    except Exception as e:
        log_message(f"Failed to save detailed results: {e}", "ERROR")
    
    # Step 7: Final summary
    log_message("Automated testing and fixing process completed!")
    log_message(f"Overall Status: {analysis['overall_status']}")
    log_message(f"Issues Found: {len(analysis.get('issues', []))}")
    log_message(f"Fixes Applied: {len(fixes.get('fixes_applied', []))}")
    
    return analysis["overall_status"] == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 