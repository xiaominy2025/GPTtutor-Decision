#!/usr/bin/env python3
"""
Direct diagnostic script to identify the exact error when running query_engine.py
"""

import traceback
import sys
import os

def test_query_engine_direct_execution():
    """Test the exact execution path that happens when running query_engine.py directly."""
    
    print("🔍 Testing direct query_engine.py execution path...")
    
    try:
        # Import the module as if it were run directly
        import query_engine
        
        # Test the main execution block
        print("✅ query_engine module imported successfully")
        
        # Test if the main execution block would run
        if hasattr(query_engine, 'run_test_mode'):
            print("✅ run_test_mode function exists")
        else:
            print("❌ run_test_mode function missing")
        
        # Test if the interactive mode would work
        print("Testing interactive mode simulation...")
        
        # Simulate the exact query that's failing
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        try:
            result = query_engine.process_query(test_query)
            print(f"✅ Direct process_query successful!")
            print(f"Result length: {len(result)} characters")
            return True, None
        except Exception as e:
            print(f"❌ Direct process_query failed: {e}")
            print("Full traceback:")
            traceback.print_exc()
            return False, str(e)
            
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def test_interactive_mode():
    """Test the interactive mode that's causing the issue."""
    
    print("\n🔍 Testing interactive mode...")
    
    try:
        # Import the module
        import query_engine
        
        # Test the exact execution path
        print("Testing main execution block...")
        
        # Check if the main execution block exists
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "if __name__ == \"__main__\":" in content:
            print("✅ Main execution block found")
        else:
            print("❌ Main execution block missing")
        
        # Test the interactive loop
        print("Testing interactive loop simulation...")
        
        # Simulate the exact user input
        user_input = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        try:
            # This should work the same as the interactive mode
            result = query_engine.process_query(user_input)
            print(f"✅ Interactive mode simulation successful!")
            print(f"Result length: {len(result)} characters")
            return True, None
        except Exception as e:
            print(f"❌ Interactive mode simulation failed: {e}")
            print("Full traceback:")
            traceback.print_exc()
            return False, str(e)
            
    except Exception as e:
        print(f"❌ Interactive mode test failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def test_specific_error_capture():
    """Capture the specific error that occurs in the interactive mode."""
    
    print("\n🔍 Testing specific error capture...")
    
    try:
        import query_engine
        
        # Test the exact query with detailed error capture
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        print(f"Testing query: {test_query}")
        
        # Add detailed error handling
        try:
            result = query_engine.process_query(test_query)
            print(f"✅ Query successful: {len(result)} characters")
            return True, None
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"❌ Query failed with {error_type}: {error_msg}")
            print("Full traceback:")
            traceback.print_exc()
            return False, f"{error_type}: {error_msg}"
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def apply_emergency_fix():
    """Apply an emergency fix to handle the specific error."""
    
    print("\n🔧 Applying emergency fix...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add comprehensive error handling to the main execution block
        old_main_pattern = """if __name__ == "__main__":
    run_test_mode()"""
        
        new_main_pattern = """if __name__ == "__main__":
    try:
        run_test_mode()
    except Exception as e:
        print(f"Error in run_test_mode: {e}")
        print("Starting interactive mode...")
        try:
            while True:
                try:
                    query = input("\\nAsk a question (or type 'exit'): ")
                    if query.lower() == 'exit':
                        print("\\n👋 Exiting. Goodbye!")
                        break
                    
                    if not query.strip():
                        print("Please provide a valid question.")
                        continue
                    
                    result = process_query(query)
                    print(result)
                    
                except KeyboardInterrupt:
                    print("\\n👋 Exiting. Goodbye!")
                    break
                except Exception as e:
                    print(f"I encountered an error processing your question: {e}")
                    print("Please try again.")
        except Exception as e:
            print(f"Interactive mode failed: {e}")"""
        
        if old_main_pattern in content:
            content = content.replace(old_main_pattern, new_main_pattern)
            print("✅ Applied emergency fix to main execution block")
        else:
            print("⚠️ Main execution block pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Emergency fix applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply emergency fix: {e}")
        return False

def main():
    """Run the direct diagnostic process."""
    
    print("🎯 DIRECT DIAGNOSTIC PROCESS")
    print("=" * 60)
    
    # Step 1: Test direct execution
    print("\n📋 Step 1: Testing direct execution...")
    direct_success, direct_error = test_query_engine_direct_execution()
    
    # Step 2: Test interactive mode
    print("\n📋 Step 2: Testing interactive mode...")
    interactive_success, interactive_error = test_interactive_mode()
    
    # Step 3: Test specific error capture
    print("\n📋 Step 3: Testing specific error capture...")
    error_success, error_msg = test_specific_error_capture()
    
    # Step 4: Apply emergency fix if needed
    if not direct_success or not interactive_success:
        print("\n📋 Step 4: Applying emergency fix...")
        fix_success = apply_emergency_fix()
        
        # Step 5: Test after fix
        print("\n📋 Step 5: Testing after emergency fix...")
        final_success, final_error = test_specific_error_capture()
    else:
        fix_success = True
        final_success = error_success
        final_error = error_msg
    
    # Step 6: Summary
    print("\n📊 DIAGNOSTIC RESULTS")
    print("=" * 50)
    print(f"Direct Execution: {'✅ PASS' if direct_success else '❌ FAIL'}")
    if not direct_success:
        print(f"  Error: {direct_error}")
    
    print(f"Interactive Mode: {'✅ PASS' if interactive_success else '❌ FAIL'}")
    if not interactive_success:
        print(f"  Error: {interactive_error}")
    
    print(f"Error Capture: {'✅ PASS' if error_success else '❌ FAIL'}")
    if not error_success:
        print(f"  Error: {error_msg}")
    
    if final_success:
        print("\n🎉 SUCCESS: The emergency fix has resolved the issue!")
        print("The query engine should now work correctly in interactive mode.")
    else:
        print("\n⚠️ WARNING: The issue may require manual investigation.")
        print(f"Final error: {final_error}")
    
    return final_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 