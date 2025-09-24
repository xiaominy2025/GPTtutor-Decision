#!/usr/bin/env python3
"""
Test script to verify bullet point formatting fixes for follow-up questions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query_engine import format_final_output, generate_domain_aware_followup_questions

def test_bullet_point_formatting():
    """Test various bullet point formatting scenarios."""
    
    print("🔍 Testing Bullet Point Formatting Fixes")
    print("=" * 50)
    
    # Test cases with different bullet point formats
    test_cases = [
        {
            "name": "Hierarchical Bullet Points",
            "input": """**Follow-up Prompts**

• How does linear optimization inform your approach to balancing efficiency with flexibility?
  ○ How would you quantify the key variables?
  ○ What strategic factors are relevant?""",
            "expected": "All questions should start with '- '"
        },
        {
            "name": "Numbered List",
            "input": """**Follow-up Prompts**

1. How does linear optimization inform your approach to balancing efficiency with flexibility?
2. How would you quantify the key variables?
3. What strategic factors are relevant?""",
            "expected": "All questions should start with '- '"
        },
        {
            "name": "Mixed Format",
            "input": """**Follow-up Prompts**

• How does linear optimization inform your approach?
1. How would you quantify the key variables?
  - What strategic factors are relevant?""",
            "expected": "All questions should start with '- '"
        },
        {
            "name": "Indented Sub-bullets",
            "input": """**Follow-up Prompts**

- How does linear optimization inform your approach?
  - How would you quantify the key variables?
  - What strategic factors are relevant?""",
            "expected": "All questions should start with '- '"
        },
        {
            "name": "Asterisk Bullets",
            "input": """**Follow-up Prompts**

* How does linear optimization inform your approach?
* How would you quantify the key variables?
* What strategic factors are relevant?""",
            "expected": "All questions should start with '- '"
        }
    ]
    
    formatting_issues = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"Input format: {test_case['expected']}")
        
        try:
            # Test the format_final_output function
            formatted_output = format_final_output(test_case['input'])
            
            # Check if all follow-up questions are properly formatted
            lines = formatted_output.split('\n')
            followup_section = False
            question_lines = []
            
            for line in lines:
                if '**Follow-up Prompts**' in line:
                    followup_section = True
                    continue
                elif followup_section and line.strip().startswith('**'):
                    break
                elif followup_section and line.strip():
                    question_lines.append(line.strip())
            
            # Check formatting of question lines
            properly_formatted = True
            for j, line in enumerate(question_lines, 1):
                if not line.startswith('- '):
                    properly_formatted = False
                    formatting_issues.append({
                        "test_case": test_case['name'],
                        "line_index": j,
                        "issue": "Line doesn't start with '- '",
                        "line": line
                    })
                    print(f"❌ Line {j} not properly formatted: '{line}'")
                else:
                    print(f"✅ Line {j} properly formatted: '{line}'")
            
            if properly_formatted:
                print(f"✅ All {len(question_lines)} lines properly formatted")
            else:
                print(f"❌ Found formatting issues in {test_case['name']}")
                
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
            formatting_issues.append({
                "test_case": test_case['name'],
                "issue": f"Processing error: {e}"
            })
    
    # Test fallback questions formatting
    print(f"\n🔧 Testing Fallback Questions Formatting")
    print("=" * 50)
    
    test_queries = [
        "How should I choose between two job offers?",
        "What linear optimization approach should I use?",
        "How do cognitive biases affect decision making?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Fallback Test {i}: {query}")
        
        try:
            fallback_questions = generate_domain_aware_followup_questions(query)
            
            if fallback_questions:
                print(f"✅ Generated {len(fallback_questions)} fallback questions")
                
                # Check formatting
                for j, question in enumerate(fallback_questions, 1):
                    if question.strip().startswith('- '):
                        print(f"✅ Question {j} properly formatted: '{question.strip()}'")
                    else:
                        print(f"❌ Question {j} formatting issue: '{question.strip()}'")
                        formatting_issues.append({
                            "test_case": f"Fallback Test {i}",
                            "question_index": j,
                            "issue": "Fallback question doesn't start with '- '",
                            "question": question.strip()
                        })
            else:
                print("⚠️ No fallback questions generated")
                
        except Exception as e:
            print(f"❌ Error in fallback test {i}: {e}")
    
    # Summary
    print(f"\n📊 BULLET POINT FORMATTING SUMMARY")
    print("=" * 50)
    
    if formatting_issues:
        print(f"❌ Found {len(formatting_issues)} formatting issues:")
        for issue in formatting_issues:
            print(f"  - {issue['test_case']}: {issue['issue']}")
            if 'line' in issue:
                print(f"    Line: '{issue['line']}'")
            if 'question' in issue:
                print(f"    Question: '{issue['question']}'")
    else:
        print("✅ No bullet point formatting issues found")
    
    return formatting_issues

def test_specific_hierarchical_scenarios():
    """Test specific scenarios that might cause hierarchical bullet point issues."""
    
    print(f"\n🔧 Testing Specific Hierarchical Scenarios")
    print("=" * 50)
    
    # Test the exact format from the image description
    image_format = """**Follow-up Prompts**

• How does linear optimization inform your approach to balancing efficiency with flexibility?
  ○ How would you quantify the key variables?
  ○ What strategic factors are relevant?"""
    
    print("📋 Testing Image Format (Hierarchical Bullets)")
    print("Input format: Main bullet with sub-bullets")
    
    try:
        formatted_output = format_final_output(image_format)
        lines = formatted_output.split('\n')
        
        # Find the follow-up section
        followup_lines = []
        in_followup = False
        
        for line in lines:
            if '**Follow-up Prompts**' in line:
                in_followup = True
                continue
            elif in_followup and line.strip().startswith('**'):
                break
            elif in_followup and line.strip():
                followup_lines.append(line.strip())
        
        print(f"✅ Found {len(followup_lines)} follow-up lines")
        
        # Check if all lines start with '- '
        all_properly_formatted = True
        for i, line in enumerate(followup_lines, 1):
            if not line.startswith('- '):
                all_properly_formatted = False
                print(f"❌ Line {i} not properly formatted: '{line}'")
            else:
                print(f"✅ Line {i} properly formatted: '{line}'")
        
        if all_properly_formatted:
            print("✅ All hierarchical bullets converted to flat format")
        else:
            print("❌ Some hierarchical bullets not converted properly")
            
    except Exception as e:
        print(f"❌ Error testing image format: {e}")

if __name__ == "__main__":
    print("🚀 Starting Bullet Point Formatting Analysis")
    print("=" * 60)
    
    # Run the tests
    formatting_issues = test_bullet_point_formatting()
    test_specific_hierarchical_scenarios()
    
    print(f"\n✅ Bullet Point Formatting Analysis Complete")
    print("=" * 60)
    
    if formatting_issues:
        print(f"❌ Found {len(formatting_issues)} bullet point formatting issues that need to be addressed")
    else:
        print("✅ No bullet point formatting issues detected") 