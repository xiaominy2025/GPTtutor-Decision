#!/usr/bin/env python3
"""
Final test to verify tooltips metadata functionality
"""

import subprocess

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

if __name__ == "__main__":
    test_final_functionality() 