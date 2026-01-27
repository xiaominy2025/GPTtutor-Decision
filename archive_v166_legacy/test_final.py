#!/usr/bin/env python3
"""
Final test to verify tooltips metadata functionality
"""

import subprocess
import requests
import re

def test_final_functionality():
    """Test the final functionality with both questions"""
    
    test_questions = [
        "A close friend wants to join my startup as a co-founder, but I'm worried it could complicate things. Should I say yes?",
        "I'm thinking of switching majors halfway through college. Is it too risky?"
    ]
    
    print("🧪 Final Test: Tooltips Metadata Functionality")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 50)
        
        try:
            # Run the query engine
            result = subprocess.run(
                ['python', 'query_engine.py'],
                input=question + '\nexit\n',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            
            # Check for tooltips metadata
            if "[TOOLTIPS METADATA FOR UI]:" in output:
                print("✅ Tooltips metadata block found")
                
                # Extract and display the metadata
                metadata_start = output.find("[TOOLTIPS METADATA FOR UI]:")
                metadata_section = output[metadata_start:]
                print("📋 Metadata content:")
                print(metadata_section)
                
                # Verify JSON format
                try:
                    import json
                    json_start = metadata_section.find('{')
                    if json_start != -1:
                        json_content = metadata_section[json_start:]
                        # Find the end of the JSON object
                        brace_count = 0
                        json_end = 0
                        for i, char in enumerate(json_content):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break
                        
                        if json_end > 0:
                            json_only = json_content[:json_end]
                            metadata_dict = json.loads(json_only)
                            print(f"✅ Valid JSON with {len(metadata_dict)} tools")
                            for tool, definition in metadata_dict.items():
                                print(f"   • {tool}: {definition[:60]}...")
                        else:
                            print("❌ Could not find complete JSON object")
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}")
            else:
                print("❌ No tooltips metadata block found")
            
            # Check for required sections
            required_sections = [
                "**How to Strategize Your Decision**",
                "**Story in Action**",
                "**Reflection Prompts**",
                "**Concepts/Tools/Practice Reference**"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in output:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections: {', '.join(missing_sections)}")
            else:
                print("✅ All required sections present")
            
            # Check for debug messages
            debug_patterns = [
                '📚 Retrieved',
                '⏱️ Response time',
                '📈 Quality check',
                '🔧 Grammar & Clarity',
                '🔋 Token Efficiency',
                '📊 Sources:',
                '🎯 Synthesized Answer:',
                'DEBUG:'
            ]
            
            found_debug = []
            for pattern in debug_patterns:
                if pattern in output:
                    found_debug.append(pattern)
            
            if found_debug:
                print(f"❌ Found debug messages: {', '.join(found_debug)}")
            else:
                print("✅ No debug messages found")
            
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
        except Exception as e:
            print(f"❌ Error running test: {e}")
    
    print(f"\n✅ Final testing completed!")

def test_concepts_tools_practice_format():
    """Test that the conceptsToolsPractice field in the API response is a list of objects with 'term' and 'definition'."""
    url = "http://localhost:5000/query"
    payload = {"query": "How should I prioritize tasks when under tight deadlines?"}
    response = requests.post(url, json=payload)
    assert response.status_code == 200, f"API did not return 200 OK, got {response.status_code}"
    data = response.json()
    assert "data" in data, "Missing 'data' in response"
    assert "conceptsToolsPractice" in data["data"], "Missing 'conceptsToolsPractice' in response data"
    concepts = data["data"]["conceptsToolsPractice"]
    assert isinstance(concepts, list), f"'conceptsToolsPractice' is not a list: {type(concepts)}"
    for i, item in enumerate(concepts):
        assert isinstance(item, dict), f"Item {i} is not an object: {item}"
        assert "term" in item and "definition" in item, f"Item {i} missing keys: {item}"
        assert isinstance(item["term"], str) and item["term"].strip() != "", f"Item {i} has empty or non-string 'term': {item}"
        assert isinstance(item["definition"], str) and item["definition"].strip() != "", f"Item {i} has empty or non-string 'definition': {item}"
    print("✅ test_concepts_tools_practice_format passed: All concepts are valid objects with term and definition.")

def test_full_api_compliance_suite():
    """Automated suite to validate full ThinkPal v1.6 API compliance for a range of queries."""
    queries = [
        "How should I prioritize tasks when under tight deadlines?",
        "What is the best way to negotiate a salary increase?",
        "Should I switch majors halfway through college?",
        "How do I decide between two job offers?",
        "What if I have no idea what to do next?",
        "Explain the value of a SWOT analysis.",
        "What is a Decision Tree?",
        "Just say hello.",
        "",
        "What are the pros and cons of remote work?",
        "How do I handle uncertainty in business forecasting?",
        "What is the GROW Model?",
        "How do I make a decision when I feel stuck?"
    ]
    required_sections = [
        "**Strategic Thinking Lens**",
        "**Story in Action**",
        "**Reflection Prompts**",
        "**Concepts/Tools/Practice Reference**"
    ]
    failures = []
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Test {i}: {query}")
        url = "http://localhost:5000/query"
        payload = {"query": query}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            failures.append((query, "API error", response.text))
            continue
        data = response.json()
        answer = data["data"].get("answer", "")
        concepts = data["data"].get("conceptsToolsPractice", None)
        # Check all four sections
        missing_sections = [s for s in required_sections if s not in answer]
        if missing_sections:
            print(f"❌ Missing sections: {', '.join(missing_sections)}")
            failures.append((query, "Missing sections", answer))
        else:
            print("✅ All required sections present.")
        # Check conceptsToolsPractice
        if not isinstance(concepts, list):
            print(f"❌ conceptsToolsPractice is not a list: {concepts}")
            failures.append((query, "conceptsToolsPractice not a list", concepts))
        else:
            malformed = [item for item in concepts if not (isinstance(item, dict) and 'term' in item and 'definition' in item and isinstance(item['term'], str) and isinstance(item['definition'], str))]
            if malformed:
                print(f"❌ Malformed concepts: {malformed}")
                failures.append((query, "Malformed concepts", malformed))
            else:
                print(f"✅ conceptsToolsPractice valid ({len(concepts)} items)")
    print("\n=== SUMMARY ===")
    if not failures:
        print("🎉 All queries passed full API compliance!")
    else:
        print(f"❌ {len(failures)} failures detected:")
        for q, reason, detail in failures:
            print(f"- Query: {q}\n  Reason: {reason}\n  Detail: {detail}\n")

def is_valid_concept_entry(entry):
    return (
        isinstance(entry, dict)
        and "term" in entry and isinstance(entry["term"], str) and entry["term"].strip()
        and "definition" in entry and isinstance(entry["definition"], str) and entry["definition"].strip()
    )

def contains_all_sections(markdown: str) -> bool:
    required_sections = [
        "**Strategic Thinking Lens**",
        "**Story in Action**",
        "**Reflection Prompts**",
        "**Concepts/Tools/Practice Reference**"
    ]
    return all(section in markdown for section in required_sections)

def test_v16_full_structure_consistency():
    """Full backend sweep for ThinkPal v1.6 response structure consistency."""
    test_queries = [
        "How should I prioritize tasks when under tight deadlines?",
        "How do I approach negotiating for a new BMW X4?",
        "How can I encourage my team to speak up during meetings?",
        "How should I plan production with fluctuating demand and limited storage?",
        "What tools can help me evaluate whether to lease or buy equipment?",
        "How can I convince a risk-averse investor to fund my project?",
        "Should I pivot my startup based on early customer feedback?",
        "How do I decide between two job offers?",
        "What is the best way to negotiate a salary increase?",
        "Should I switch majors halfway through college?",
        "What if I have no idea what to do next?",
        "Explain the value of a SWOT analysis.",
        "What is a Decision Tree?",
        "Just say hello.",
        "What are the pros and cons of remote work?",
        "How do I handle uncertainty in business forecasting?",
        "What is the GROW Model?",
        "How do I make a decision when I feel stuck?",
        "How do I evaluate a new product launch?",
        "How can I improve my leadership skills?",
        "How do I manage stress during a crisis?",
        "How do I balance short-term and long-term goals?",
        "How do I assess the risks of international expansion?",
        "How do I build a high-performing team?"
    ]
    failures = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        url = "http://localhost:5000/query"
        payload = {"query": query}
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            failures.append((query, "API error", response.text))
            continue
        data = response.json()
        answer = data["data"].get("answer", "")
        concepts = data["data"].get("conceptsToolsPractice", None)
        # Check all four sections
        if not contains_all_sections(answer):
            print(f"❌ Missing one or more required sections.")
            failures.append((query, "Missing section(s)", answer))
        else:
            print("✅ All required sections present.")
        # Check conceptsToolsPractice
        if not isinstance(concepts, list):
            print(f"❌ conceptsToolsPractice is not a list: {concepts}")
            failures.append((query, "conceptsToolsPractice not a list", concepts))
        else:
            malformed = [item for item in concepts if not is_valid_concept_entry(item)]
            if malformed:
                print(f"❌ Malformed concepts: {malformed}")
                failures.append((query, "Malformed concepts", malformed))
            else:
                print(f"✅ conceptsToolsPractice valid ({len(concepts)} items)")
    print("\n=== SUMMARY ===")
    if not failures:
        print("🎉 All queries passed full v1.6 structure compliance!")
    else:
        print(f"❌ {len(failures)} failures detected:")
        for q, reason, detail in failures:
            print(f"- Query: {q}\n  Reason: {reason}\n  Detail: {detail}\n")

if __name__ == "__main__":
    test_final_functionality()
    test_concepts_tools_practice_format()
    test_full_api_compliance_suite()
    test_v16_full_structure_consistency() 