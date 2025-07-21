import json
import re
from query_engine import process_query, PREBUILT_TOOLTIPS

def run_tooltip_test_suite():
    with open("test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)
    passed = 0
    for i, case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {case['question']}")
        response = process_query(case['question'])
        found = []
        for concept in case["expected_tooltips"]:
            # Look for tooltip span for this concept (case-insensitive, singular/plural)
            pattern = r'<span class="tooltip" data-tooltip="[^"]*">' + re.escape(concept) + r'(s)?</span>'
            if re.search(pattern, response, re.IGNORECASE):
                print(f"✅ Tooltip injected for '{concept}'")
                found.append(concept)
            else:
                print(f"❌ Tooltip missing for '{concept}'")
        if found:
            passed += 1
        print(f"Recognized tooltips: {found if found else 'None'} | Missed: {[c for c in case['expected_tooltips'] if c not in found]}")
    print(f"\n{passed} / {len(test_cases)} test cases passed.")

if __name__ == "__main__":
    run_tooltip_test_suite() 