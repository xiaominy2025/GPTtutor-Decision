#!/usr/bin/env python3
"""
Contract validator to ensure API responses meet frontend requirements.
"""

import json
import sys
from typing import Dict, Any, List

def validate_response_contract(response_data: str) -> Dict[str, Any]:
    """
    Validate that response meets frontend contract requirements.
    
    Args:
        response_data: Either JSON string or already parsed dict
    
    Returns:
        Dict with validation results and any issues found.
    """
    if isinstance(response_data, str):
        try:
            response = json.loads(response_data)
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON: {e}",
                "issues": ["JSON parsing failed"]
            }
    else:
        response = response_data
    
    issues = []
    
    # Required keys
    required_keys = ["strategicLens", "followupPrompts", "conceptsToolsPractice"]
    for key in required_keys:
        if key not in response:
            issues.append(f"Missing required key: {key}")
    
    # Strategic lens validation
    if "strategicLens" in response:
        lens = response["strategicLens"]
        if not isinstance(lens, str):
            issues.append("strategicLens must be a string")
        elif len(lens.strip()) < 50:
            issues.append("strategicLens too short (< 50 chars)")
        elif len(lens.split()) < 20:
            issues.append("strategicLens too short (< 20 words)")
    
    # Follow-up prompts validation
    if "followupPrompts" in response:
        prompts = response["followupPrompts"]
        if not isinstance(prompts, list):
            issues.append("followupPrompts must be a list")
        elif len(prompts) < 2:
            issues.append("followupPrompts too few (< 2)")
        elif len(prompts) > 6:
            issues.append("followupPrompts too many (> 6)")
        else:
            for i, prompt in enumerate(prompts):
                if not isinstance(prompt, str):
                    issues.append(f"followupPrompts[{i}] must be a string")
                elif len(prompt.strip()) < 10:
                    issues.append(f"followupPrompts[{i}] too short (< 10 chars)")
    
    # Concepts validation
    if "conceptsToolsPractice" in response:
        concepts = response["conceptsToolsPractice"]
        if not isinstance(concepts, list):
            issues.append("conceptsToolsPractice must be a list")
        elif len(concepts) < 1:
            issues.append("conceptsToolsPractice too few (< 1)")
        elif len(concepts) > 8:
            issues.append("conceptsToolsPractice too many (> 8)")
        else:
            for i, concept in enumerate(concepts):
                if not isinstance(concept, dict):
                    issues.append(f"conceptsToolsPractice[{i}] must be a dict")
                elif "term" not in concept or "definition" not in concept:
                    issues.append(f"conceptsToolsPractice[{i}] missing term/definition")
                elif not isinstance(concept["term"], str) or not isinstance(concept["definition"], str):
                    issues.append(f"conceptsToolsPractice[{i}] term/definition must be strings")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "response_keys": list(response.keys())
    }

def validate_test_corpus(corpus_file: str = "post_cleanup_outputs.json"):
    """Validate all responses in the test corpus."""
    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
    except FileNotFoundError:
        print(f"Corpus file {corpus_file} not found")
        return
    
    print(f"Validating {len(corpus)} responses from {corpus_file}")
    print("=" * 60)
    
    all_valid = True
    for q_id, data in corpus.items():
        if "error" in data:
            print(f"{q_id}: ERROR - {data['error']}")
            all_valid = False
            continue
            
        # Handle double-encoded JSON from run_query_once
        output = data["output"]
        if isinstance(output, str) and output.startswith('"'):
            # Double-encoded JSON string
            try:
                output = json.loads(output)
            except:
                pass
        result = validate_response_contract(output)
        status = "✅ VALID" if result["valid"] else "❌ INVALID"
        print(f"{q_id}: {status}")
        
        if not result["valid"]:
            all_valid = False
            for issue in result["issues"]:
                print(f"  - {issue}")
            print(f"  Keys: {result['response_keys']}")
        print()
    
    print("=" * 60)
    print(f"Overall: {'✅ ALL VALID' if all_valid else '❌ SOME INVALID'}")
    return all_valid

if __name__ == "__main__":
    validate_test_corpus()
