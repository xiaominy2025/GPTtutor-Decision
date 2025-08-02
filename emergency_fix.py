#!/usr/bin/env python3
"""
Emergency fix for query_engine.py structure issue.
"""

def fix_query_engine_structure():
    """Fix the structure issue in query_engine.py."""
    
    print("🔧 Applying emergency structure fix...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the main execution block
        main_start = content.find("if __name__ == \"__main__\":")
        if main_start == -1:
            print("❌ Main execution block not found")
            return False
        
        # Find the end of the main execution block
        main_end = content.find("def generate_domain_aware_followup_prompt", main_start)
        if main_end == -1:
            print("❌ Could not find end of main execution block")
            return False
        
        # Extract the main execution block
        main_block = content[main_start:main_end]
        
        # Find the rest of the file (functions after main)
        rest_of_file = content[main_end:]
        
        # Reconstruct the file with main execution block at the end
        new_content = content[:main_start] + rest_of_file + "\n\n" + main_block
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print("✅ Structure fix applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply structure fix: {e}")
        return False

def test_fixed_query_engine():
    """Test the fixed query engine."""
    
    print("\n🧪 Testing fixed query engine...")
    
    try:
        from query_engine import process_query
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        
        result = process_query(test_query)
        print(f"✅ Query processing successful!")
        print(f"Result length: {len(result)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the emergency fix."""
    
    print("🚨 EMERGENCY STRUCTURE FIX")
    print("=" * 50)
    
    # Apply the fix
    fix_success = fix_query_engine_structure()
    
    if fix_success:
        # Test the fix
        test_success = test_fixed_query_engine()
        
        if test_success:
            print("\n🎉 SUCCESS: Structure fix applied and tested!")
            print("The query engine should now work correctly.")
        else:
            print("\n⚠️ Fix applied but test failed. Additional investigation needed.")
    else:
        print("\n❌ Failed to apply structure fix.")
    
    return fix_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Emergency fix completed successfully!")
    else:
        print("\n❌ Emergency fix failed!") 