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

def run_full_test_suite():
    """Run the complete test suite"""
    print("🚀 ThinkPal V1.6.3 Full Test Suite")
    print("=" * 50)
    
    all_passed = True
    try:
        test_thinkpal_structure_compliance()
        test_concept_extraction()
        test_followup_query_concepts()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        all_passed = False
    return all_passed

if __name__ == "__main__":
    success = run_full_test_suite()
    sys.exit(0 if success else 1) 