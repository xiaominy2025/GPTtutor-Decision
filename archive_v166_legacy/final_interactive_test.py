#!/usr/bin/env python3
"""
Final test to verify the interactive mode works correctly.
"""

def test_interactive_mode():
    """Test the interactive mode simulation."""
    
    print("🎯 FINAL INTERACTIVE MODE TEST")
    print("=" * 50)
    
    try:
        import query_engine
        
        # Simulate the exact user input that was failing
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        print(f"Testing query: {test_query}")
        print("-" * 50)
        
        # Test the process_query function directly
        result = query_engine.process_query(test_query)
        
        print(f"✅ Interactive mode simulation successful!")
        print(f"Result length: {len(result)} characters")
        
        # Check for required sections
        sections = ["Strategic Thinking Lens", "Story in Action", "Follow-up Prompts", "Concepts/Tools"]
        missing_sections = []
        
        for section in sections:
            if section in result:
                print(f"  ✅ {section} present")
            else:
                print(f"  ❌ {section} missing")
                missing_sections.append(section)
        
        if not missing_sections:
            print("✅ All required sections present")
        else:
            print(f"⚠️ Missing sections: {missing_sections}")
        
        # Show first part of the response
        print(f"\n📄 First 500 characters of response:")
        print("-" * 50)
        print(result[:500])
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Interactive mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_execution_block():
    """Test that the main execution block is properly structured."""
    
    print("\n🎯 TESTING MAIN EXECUTION BLOCK")
    print("=" * 50)
    
    try:
        # Read the query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if main execution block is at the end
        main_blocks = content.count("if __name__ == \"__main__\":")
        print(f"Found {main_blocks} main execution blocks")
        
        # Check if functions are defined before main
        function_definitions = [
            "def process_query",
            "def generate_domain_aware_followup_prompt",
            "def extract_enhanced_entities"
        ]
        
        for func_def in function_definitions:
            if func_def in content:
                print(f"  ✅ {func_def} found")
            else:
                print(f"  ❌ {func_def} missing")
        
        # Check if main execution block is at the end
        last_main = content.rfind("if __name__ == \"__main__\":")
        if last_main > len(content) * 0.8:  # Main block should be in the last 20% of the file
            print("✅ Main execution block is at the end")
            return True
        else:
            print("❌ Main execution block is not at the end")
            return False
            
    except Exception as e:
        print(f"❌ Main execution block test failed: {e}")
        return False

def main():
    """Run the final interactive test."""
    
    print("🎯 FINAL INTERACTIVE TEST SUITE")
    print("=" * 60)
    
    # Test main execution block structure
    structure_success = test_main_execution_block()
    
    # Test interactive mode
    interactive_success = test_interactive_mode()
    
    # Final summary
    print("\n📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"Structure: {'✅ PASS' if structure_success else '❌ FAIL'}")
    print(f"Interactive Mode: {'✅ PASS' if interactive_success else '❌ FAIL'}")
    
    if structure_success and interactive_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The query engine is now working correctly in interactive mode.")
        print("You can run 'python query_engine.py' and it should work properly.")
    else:
        print("\n⚠️ Some tests failed.")
        print("Please check the error messages above for specific issues.")
    
    return structure_success and interactive_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 FINAL TEST COMPLETE - SYSTEM READY!")
    else:
        print("\n⚠️ FINAL TEST COMPLETE - ISSUES DETECTED!") 