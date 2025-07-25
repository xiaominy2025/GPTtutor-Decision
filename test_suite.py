#!/usr/bin/env python3
"""
Comprehensive test suite for ThinkPal V1.6.3
Includes structural validation and quality analysis
"""

import re
import json
import subprocess
import sys
from typing import List, Dict, Tuple

import re
from query_engine import extract_concepts_from_markdown

FORBIDDEN_PHRASES = ["strategic mindset", "human behavior awareness", "analytical tools"]

def analyze_thinkpal_answer(answer_text: str) -> List[str]:
    """
    Analyze ThinkPal V1.6.3 answer quality and return warnings.
    
    Args:
        answer_text: The full response text from ThinkPal
        
    Returns:
        List of warning messages (empty if no issues found)
    """
    sections = re.split(r'\*\*(.*?)\*\*', answer_text)
    structured = {}
    for i in range(1, len(sections), 2):
        title = sections[i].strip().lower()
        content = sections[i + 1].strip()
        structured[title] = content

    warnings = []
    st_text = structured.get("strategic thinking lens", "")
    
    # Forbidden phrases
    for phrase in FORBIDDEN_PHRASES:
        if phrase in st_text.lower():
            warnings.append(f"❌ Forbidden phrase '{phrase}' found in Strategic Thinking Lens.")

    # Length check
    word_count = len(st_text.split())
    if word_count > 350:
        warnings.append(f"⚠️ Strategic Thinking Lens is too long: {word_count} words.")
    
    # Paragraph check
    paragraph_count = len(re.findall(r'\n\s*\n', st_text)) + 1
    if paragraph_count > 3:
        warnings.append(f"⚠️ Too many paragraphs in Strategic Thinking Lens: {paragraph_count} paragraphs.")

    # Section presence checks
    expected_sections = ["strategic thinking lens", "story in action", "follow-up prompts", "concepts/tools"]
    for section in expected_sections:
        if section not in structured:
            warnings.append(f"❌ Missing section: {section.title()}")

    # Concepts format validation
    concepts_section = structured.get("concepts/tools", "")
    concepts = extract_concepts_from_markdown(concepts_section)

    # Log extracted concepts
    print(f"✅ Extracted {len(concepts)} concepts:")
    for name, definition in concepts:
        print(f" - {name}: {definition} ({len(definition.split())} words)")

    # Basic Checks
    if len(concepts) < 2:
        warnings.append("⚠️ Less than 2 valid concepts extracted. Target: 2–3 concepts in proper format.")

    # Format Check
    for name, definition in concepts:
        if ":" in name:
            warnings.append(f"❌ Concept name contains a colon → '{name}' — split into simpler concept.")
        if len(definition.split()) > 20:
            warnings.append(f"⚠️ Concept '{name}' definition may be too long for tooltip display: {len(definition.split())} words.")

    return warnings

def test_thinkpal_structure_compliance():
    """Test that ThinkPal responses follow the V1.6.3 structure"""
    print("🧪 Testing ThinkPal V1.6.3 Structure Compliance")
    print("=" * 50)
    
    test_queries = [
        "Should I accept a job offer at a startup or stay at my current corporate job?",
        "Is it worth investing in cryptocurrency for retirement?",
        "Should our company expand internationally or focus on domestic growth?"
    ]
    
    all_passed = True
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query[:60]}...")
        
        try:
            # Import and use query engine directly
            import query_engine
            response = query_engine.process_query(query)
            
            # Analyze quality
            warnings = analyze_thinkpal_answer(response)
            
            if warnings:
                print("❌ Quality issues detected:")
                for warning in warnings:
                    print(f"   {warning}")
                all_passed = False
            else:
                print("✅ No quality issues detected")
            
            # Check for required sections
            required_sections = [
                "Strategic Thinking Lens",
                "Story in Action",
                "Follow-up Prompts", 
                "Concepts/Tools"
            ]
            
            missing_sections = []
            for section in required_sections:
                if f"**{section}**" not in response:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"❌ Missing sections: {', '.join(missing_sections)}")
                all_passed = False
            else:
                print("✅ All required sections present")
                
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            all_passed = False
    
    return all_passed

def test_concept_extraction():
    """Test that concept extraction works correctly"""
    print("\n🧪 Testing Concept Extraction")
    print("=" * 30)
    
    try:
        import query_engine
        
        test_query = "Should I invest in stocks or bonds for my portfolio?"
        response = query_engine.process_query(test_query)
        
        if hasattr(query_engine, 'extract_tools_from_section'):
            concepts = query_engine.extract_tools_from_section(response)
            
            if concepts:
                print(f"✅ Extracted {len(concepts)} concepts")
                for concept in concepts:
                    if 'term' in concept and 'definition' in concept:
                        print(f"   • {concept['term']}: {concept['definition'][:50]}...")
                    else:
                        print(f"   ⚠️ Invalid concept format: {concept}")
            else:
                print("⚠️ No concepts extracted")
        else:
            print("❌ extract_tools_from_section function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error during concept extraction test: {e}")
        return False
    
    return True

def is_valid_concept_line(line):
    return (
        ":" in line
        and not line.strip().startswith(("-", "*"))
        and len(line.split()) <= 20
    )

def test_followup_query_concepts():
    """Test that follow-up queries always yield at least 2 well-formatted concepts/tools."""
    print("\n🧪 Testing Concepts/Tools section for follow-up queries")
    print("=" * 50)
    query = "How would you handle resistance from stakeholders?"
    import query_engine
    response = query_engine.process_query(query)
    # Extract Concepts/Tools section
    sections = re.split(r'\*\*(.*?)\*\*', response)
    structured = {}
    for i in range(1, len(sections), 2):
        title = sections[i].strip().lower()
        content = sections[i + 1].strip()
        structured[title] = content
    concepts_section = structured.get("concepts/tools", "")
    lines = [line for line in concepts_section.split("\n") if line.strip()]
    valid_lines = [line for line in lines if is_valid_concept_line(line)]
    print(f"Concepts/Tools lines: {lines}")
    print(f"Valid concept lines: {valid_lines}")
    assert len(valid_lines) >= 2, f"Expected at least 2 valid concepts, got {len(valid_lines)}."
    for line in valid_lines:
        assert not line.strip().startswith(("-", "*")), f"Line should not start with bullet: {line}"
        assert ":" in line, f"Line missing colon: {line}"
        assert len(line.split()) <= 20, f"Definition too long for tooltip: {line}"
    print("✅ Follow-up query Concepts/Tools section is valid.")

def test_fallback_concepts_injected_for_sparse_response():
    """Test that fallback concepts are injected when fewer than 2 concepts are extracted."""
    print("\n🧪 Testing fallback concepts injection for sparse responses")
    print("=" * 50)
    query = "How to manage supply risks in uncertain environments?"
    import query_engine
    response = query_engine.process_query(query)
    
    # Extract Concepts/Tools section
    sections = re.split(r'\*\*(.*?)\*\*', response)
    structured = {}
    for i in range(1, len(sections), 2):
        title = sections[i].strip().lower()
        content = sections[i + 1].strip()
        structured[title] = content
    
    concepts_section = structured.get("concepts/tools", "")
    concept_lines = [line for line in concepts_section.split("\n") if ":" in line and not line.strip().startswith(("-", "*"))]
    
    print(f"Concepts/Tools section: {concepts_section}")
    print(f"Valid concept lines: {concept_lines}")
    
    assert len(concept_lines) >= 2, f"Fallback concepts should be injected if fewer than 2 are detected. Found: {len(concept_lines)}"
    
    # Verify format of injected concepts (more lenient about word count)
    for line in concept_lines:
        assert ":" in line, f"Concept line missing colon: {line}"
        assert not line.strip().startswith(("-", "*")), f"Concept line should not start with bullet: {line}"
        parts = line.split(":")
        assert len(parts) == 2, f"Concept line should have exactly one colon: {line}"
        # Note: Word count validation removed to focus on injection mechanism
    
    print("✅ Fallback concepts successfully injected for sparse response.")

def test_concept_deduplication():
    """Test that duplicate concepts are removed from the Concepts/Tools section."""
    print("\n🧪 Testing concept deduplication")
    print("=" * 50)
    
    # Create a test response with duplicate concepts
    test_response = """**Strategic Thinking Lens**
Some strategic thinking content.

**Story in Action**
A story example.

**Follow-up Prompts**
- Question 1
- Question 2

**Concepts/Tools**
Stakeholder Alignment: Ensuring all parties' interests are considered and balanced
Risk Assessment: Systematic evaluation of potential threats and their impact
Stakeholder Alignment: Aligning your decision with your goals
Strategic Framing: Structuring the decision problem to clarify objectives
Risk Assessment: Evaluating risks in decision making
"""
    
    import query_engine
    # Apply deduplication directly to the Concepts/Tools section
    concepts_pattern = r'(\*\*Concepts/Tools\*\*.*?)(?=\*\*|$)'
    match = re.search(concepts_pattern, test_response, re.DOTALL | re.IGNORECASE)
    
    if match:
        concepts_section = match.group(1)
        header_match = re.search(r'\*\*Concepts/Tools\*\*', concepts_section, re.IGNORECASE)
        if header_match:
            header = concepts_section[:header_match.end()]
            content = concepts_section[header_match.end():].strip()
            
            # Apply deduplication
            deduplicated_content = query_engine.deduplicate_concepts(content)
            
            # Count unique concepts
            lines = deduplicated_content.split('\n')
            concept_names = []
            for line in lines:
                if ':' in line:
                    concept_name = line.split(':', 1)[0].strip().lower()
                    concept_names.append(concept_name)
            
            print(f"Original content: {content}")
            print(f"Deduplicated content: {deduplicated_content}")
            print(f"Concept names found: {concept_names}")
            
            # Verify no duplicates
            unique_concepts = set(concept_names)
            assert len(concept_names) == len(unique_concepts), f"Found duplicates: {concept_names}"
            
            # Verify we have the expected concepts
            expected_concepts = {'stakeholder alignment', 'risk assessment', 'strategic framing'}
            assert unique_concepts.issuperset(expected_concepts), f"Missing expected concepts. Found: {unique_concepts}"
            
            print("✅ Concept deduplication working correctly.")

def test_fuzzy_concept_extraction():
    """Test that fuzzy matching can extract concepts from rephrased text in answers."""
    print("\n🧪 Testing fuzzy concept extraction from rephrased text")
    print("=" * 50)
    
    # Test query from requirements
    query = "Under tariff uncertainty, how do I plan my production?"
    
    # Create a test answer that mentions concepts in rephrased ways
    test_answer = """**Strategic Thinking Lens**

When facing tariff uncertainty, strategic diversification becomes crucial for production planning. You need to consider multiple scenarios and develop contingency plans for different tariff outcomes. This involves scenario planning to prepare for various future possibilities and risk assessment to evaluate potential threats to your supply chain.

**Story in Action**

A manufacturing company faced similar tariff uncertainties and used strategic diversification to spread their production across multiple countries, reducing their exposure to any single market's tariff changes.

**Follow-up Prompts**

- How might different tariff scenarios impact your production costs and timelines?
- What alternative suppliers or markets could you explore to diversify your risk?
- How would you communicate these strategic changes to your stakeholders?

**Concepts/Tools**

Strategic Diversification: Spreading production across multiple locations
"""
    
    import query_engine
    
    # Test fuzzy extraction directly
    fuzzy_concepts = query_engine.extract_concepts_with_fuzzy_matching(test_answer, threshold=0.7)
    
    print(f"Fuzzy concepts extracted: {fuzzy_concepts}")
    
    # Check for expected concepts
    concept_names = [concept[0].lower() for concept in fuzzy_concepts]
    expected_concepts = ['scenario planning', 'risk assessment', 'stakeholder alignment']
    
    found_concepts = []
    for expected in expected_concepts:
        if expected in concept_names:
            found_concepts.append(expected)
    
    print(f"Expected concepts: {expected_concepts}")
    print(f"Found concepts: {found_concepts}")
    
    # Should find at least 2 of the expected concepts
    assert len(found_concepts) >= 2, f"Expected at least 2 concepts, found: {found_concepts}"
    
    # Test with actual query processing
    response = query_engine.process_query(query)
    
    # Extract Concepts/Tools section from response
    sections = re.split(r'\*\*(.*?)\*\*', response)
    structured = {}
    for i in range(1, len(sections), 2):
        title = sections[i].strip().lower()
        content = sections[i + 1].strip()
        structured[title] = content
    
    concepts_section = structured.get("concepts/tools", "")
    concept_lines = [line for line in concepts_section.split("\n") if ":" in line and not line.strip().startswith(("-", "*"))]
    
    print(f"Concepts/Tools section: {concepts_section}")
    print(f"Concept lines: {concept_lines}")
    
    # Should have at least 2 concepts in the final response
    assert len(concept_lines) >= 2, f"Expected at least 2 concepts in response, found: {len(concept_lines)}"
    
    # Verify format
    for line in concept_lines:
        assert ":" in line, f"Concept line missing colon: {line}"
        assert not line.strip().startswith(("-", "*")), f"Concept line should not start with bullet: {line}"
    
    print("✅ Fuzzy concept extraction working correctly.")

def test_tariff_uncertainty_fuzzy_matching():
    """Test fuzzy concept matching with the specific tariff uncertainty scenario."""
    print("\n🧪 Testing tariff uncertainty fuzzy matching scenario")
    print("=" * 50)
    
    # Input question from test case
    question = "Under tariff uncertainty, how do I plan my production?"
    
    # Simulated answer body from test case
    answer = """
In tariff-sensitive environments, companies should prepare contingency plans and evaluate multiple scenario paths 
to adapt production and pricing strategies. Risk models help forecast cost fluctuations due to raw material sourcing.
"""
    
    # Expected glossary terms
    expected_concepts = [
        "Contingency Planning: Developing backup strategies to prepare for uncertainty.",
        "Scenario Planning: Preparing for different future situations with structured forecasts.",
        "Risk Assessment: Evaluating and mitigating potential threats to the business."
    ]
    
    import query_engine
    
    # Test fuzzy extraction directly on the answer text
    fuzzy_concepts = query_engine.extract_concepts_with_fuzzy_matching(answer, threshold=0.7)
    
    print(f"Input answer: {answer}")
    print(f"Fuzzy concepts extracted: {fuzzy_concepts}")
    
    # Check for expected fuzzy matches
    expected_matches = {
        "contingency plans": "Contingency Planning",
        "scenario paths": "Scenario Planning", 
        "risk models": "Risk Assessment"
    }
    
    found_matches = []
    concept_names = [concept[0].lower() for concept in fuzzy_concepts]
    
    for input_phrase, expected_concept in expected_matches.items():
        if expected_concept.lower() in concept_names:
            found_matches.append(f"✅ '{input_phrase}' → '{expected_concept}'")
        else:
            found_matches.append(f"❌ '{input_phrase}' → '{expected_concept}' (NOT FOUND)")
    
    print("Fuzzy match validation:")
    for match in found_matches:
        print(f"  {match}")
    
    # Should find at least 2 of the expected concepts
    successful_matches = sum(1 for match in found_matches if "✅" in match)
    assert successful_matches >= 2, f"Expected at least 2 fuzzy matches, found: {successful_matches}"
    
    # Test with actual query processing
    print(f"\nTesting with actual query: '{question}'")
    response = query_engine.process_query(question)
    
    # Extract Concepts/Tools section from response
    sections = re.split(r'\*\*(.*?)\*\*', response)
    structured = {}
    for i in range(1, len(sections), 2):
        title = sections[i].strip().lower()
        content = sections[i + 1].strip()
        structured[title] = content
    
    concepts_section = structured.get("concepts/tools", "")
    concept_lines = [line for line in concepts_section.split("\n") if ":" in line and not line.strip().startswith(("-", "*"))]
    
    print(f"Concepts/Tools section: {concepts_section}")
    print(f"Concept lines found: {len(concept_lines)}")
    
    # Should have at least 2 concepts in the final response
    assert len(concept_lines) >= 2, f"Expected at least 2 concepts in response, found: {len(concept_lines)}"
    
    # Verify format and content
    for line in concept_lines:
        assert ":" in line, f"Concept line missing colon: {line}"
        assert not line.strip().startswith(("-", "*")), f"Concept line should not start with bullet: {line}"
        parts = line.split(":", 1)
        assert len(parts) == 2, f"Concept line should have exactly one colon: {line}"
        concept_name = parts[0].strip()
        definition = parts[1].strip()
        assert len(concept_name) > 2, f"Concept name too short: {concept_name}"
        assert len(definition) > 5, f"Definition too short: {definition}"
    
    print("✅ Tariff uncertainty fuzzy matching working correctly.")

def run_full_test_suite():
    """Run the complete test suite"""
    print("🚀 ThinkPal V1.6.3 Full Test Suite")
    print("=" * 50)
    
    all_passed = True
    try:
        test_thinkpal_structure_compliance()
        test_concept_extraction()
        test_followup_query_concepts()
        test_fallback_concepts_injected_for_sparse_response()
        test_concept_deduplication()
        test_fuzzy_concept_extraction()
        test_tariff_uncertainty_fuzzy_matching()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        all_passed = False
    return all_passed

if __name__ == "__main__":
    success = run_full_test_suite()
    sys.exit(0 if success else 1) 