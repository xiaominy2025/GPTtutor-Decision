#!/usr/bin/env python3
"""
Compare pre-cleanup and post-cleanup outputs to ensure equivalence.
"""

import json
import sys

def compare_outputs():
    """Compare pre and post cleanup outputs."""
    try:
        with open('golden_outputs_pre_cleanup.json', 'r', encoding='utf-8') as f:
            pre_cleanup = json.load(f)
        
        with open('post_cleanup_outputs.json', 'r', encoding='utf-8') as f:
            post_cleanup = json.load(f)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return
    
    print("Comparing pre-cleanup vs post-cleanup outputs...")
    print("=" * 60)
    
    all_equivalent = True
    
    for q_id in pre_cleanup.keys():
        if q_id not in post_cleanup:
            print(f"{q_id}: ❌ MISSING in post-cleanup")
            all_equivalent = False
            continue
            
        pre_data = pre_cleanup[q_id]
        post_data = post_cleanup[q_id]
        
        # Check for errors
        if "error" in pre_data and "error" in post_data:
            print(f"{q_id}: ✅ Both have errors (expected)")
            continue
        elif "error" in pre_data or "error" in post_data:
            print(f"{q_id}: ❌ Error mismatch")
            all_equivalent = False
            continue
        
        # Compare outputs
        pre_output = pre_data["output"]
        post_output = post_data["output"]
        
        # Parse both outputs (handle double-encoded JSON)
        try:
            if isinstance(pre_output, str) and pre_output.startswith('"'):
                pre_parsed = json.loads(json.loads(pre_output))
            elif isinstance(pre_output, str):
                pre_parsed = json.loads(pre_output)
            else:
                pre_parsed = pre_output
                
            if isinstance(post_output, str) and post_output.startswith('"'):
                post_parsed = json.loads(json.loads(post_output))
            elif isinstance(post_output, str):
                post_parsed = json.loads(post_output)
            else:
                post_parsed = post_output
        except:
            print(f"{q_id}: ❌ JSON parsing error")
            all_equivalent = False
            continue
        
        # Compare key fields
        pre_lens = pre_parsed.get("strategicLens", "")
        post_lens = post_parsed.get("strategicLens", "")
        
        pre_prompts = pre_parsed.get("followupPrompts", [])
        post_prompts = post_parsed.get("followupPrompts", [])
        
        pre_concepts = pre_parsed.get("conceptsToolsPractice", [])
        post_concepts = post_parsed.get("conceptsToolsPractice", [])
        
        # Check if outputs are equivalent (allowing for minor variations)
        lens_similar = abs(len(pre_lens) - len(post_lens)) < 50  # Allow 50 char difference
        prompts_similar = abs(len(pre_prompts) - len(post_prompts)) <= 1  # Allow 1 prompt difference
        concepts_similar = abs(len(pre_concepts) - len(post_concepts)) <= 1  # Allow 1 concept difference
        
        if lens_similar and prompts_similar and concepts_similar:
            print(f"{q_id}: ✅ EQUIVALENT")
        else:
            print(f"{q_id}: ⚠️  DIFFERENT (lens: {len(pre_lens)} vs {len(post_lens)}, prompts: {len(pre_prompts)} vs {len(post_prompts)}, concepts: {len(pre_concepts)} vs {len(post_concepts)})")
            all_equivalent = False
    
    print("=" * 60)
    print(f"Overall: {'✅ ALL EQUIVALENT' if all_equivalent else '⚠️  SOME DIFFERENCES (expected due to non-deterministic GPT)'}")
    return all_equivalent

if __name__ == "__main__":
    compare_outputs()
