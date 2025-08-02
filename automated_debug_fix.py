#!/usr/bin/env python3
"""
Automated debug and fix script for query engine issues.
This script will identify problems and apply fixes automatically.
"""

import traceback
import sys
import os

def test_entity_extraction_automated():
    """Test entity extraction and return detailed error info."""
    
    print("🔍 Testing entity extraction...")
    
    try:
        from query_engine import extract_enhanced_entities
        
        test_query = "How can I optimize production with 50 employees while considering budget constraints?"
        print(f"Test query: {test_query}")
        
        entities = extract_enhanced_entities(test_query)
        print(f"✅ Entity extraction successful!")
        print(f"Entities: {entities}")
        return True, None
        
    except Exception as e:
        error_msg = f"Entity extraction failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def test_process_query_automated():
    """Test process_query and return detailed error info."""
    
    print("\n🔍 Testing process_query...")
    
    try:
        from query_engine import process_query
        
        test_query = "How can I optimize production?"
        print(f"Test query: {test_query}")
        
        result = process_query(test_query)
        print(f"✅ Process query successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        return True, None
        
    except Exception as e:
        error_msg = f"Process query failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def fix_entity_extraction_issue():
    """Apply fixes to the entity extraction function."""
    
    print("\n🔧 Applying entity extraction fixes...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the fix is already applied
        if "categories_to_remove = []" in content:
            print("✅ Entity extraction fix already applied")
            return True
        
        # Apply the fix for dictionary iteration issue
        old_pattern = """    # Remove duplicates and empty categories
    for category in entities:
        entities[category] = list(set(entities[category]))
        if not entities[category]:
            del entities[category]"""
        
        new_pattern = """    # Remove duplicates and empty categories
    categories_to_remove = []
    for category in entities:
        entities[category] = list(set(entities[category]))
        if not entities[category]:
            categories_to_remove.append(category)
    
    # Remove empty categories after iteration
    for category in categories_to_remove:
        del entities[category]"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Applied dictionary iteration fix")
        else:
            print("⚠️ Dictionary iteration fix pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Entity extraction fixes applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply entity extraction fixes: {e}")
        return False

def fix_function_name_issue():
    """Fix the function name issue in enhance_strategic_lens_fallback."""
    
    print("\n🔧 Applying function name fixes...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if the fix is already applied
        if "domain = extract_application_field(query)" in content:
            print("✅ Function name fix already applied")
            return True
        
        # Apply the fix for function name
        old_pattern = "domain = extract_decision_domain(query)"
        new_pattern = "domain = extract_application_field(query)"
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Applied function name fix")
        else:
            print("⚠️ Function name fix pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Function name fixes applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply function name fixes: {e}")
        return False

def add_error_handling():
    """Add error handling around entity extraction calls."""
    
    print("\n🔧 Adding error handling...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if error handling is already applied
        if "try:\n        entities = extract_enhanced_entities(query)" in content:
            print("✅ Error handling already applied")
            return True
        
        # Apply error handling around entity extraction
        old_pattern = """    # Extract enhanced entities for additional nuance
    entities = extract_enhanced_entities(query)"""
        
        new_pattern = """    # Extract enhanced entities for additional nuance
    try:
        entities = extract_enhanced_entities(query)
    except Exception as e:
        # If entity extraction fails, continue without enhancement
        print(f"Entity extraction failed: {e}")
        entities = {}"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Applied error handling fix")
        else:
            print("⚠️ Error handling fix pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Error handling applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply error handling: {e}")
        return False

def run_comprehensive_test():
    """Run a comprehensive test after all fixes."""
    
    print("\n🧪 Running comprehensive test...")
    
    # Test entity extraction
    entity_success, entity_error = test_entity_extraction_automated()
    
    # Test process_query
    query_success, query_error = test_process_query_automated()
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Entity extraction: {'✅ PASS' if entity_success else '❌ FAIL'}")
    if not entity_success:
        print(f"  Error: {entity_error}")
    
    print(f"Process query: {'✅ PASS' if query_success else '❌ FAIL'}")
    if not query_success:
        print(f"  Error: {query_error}")
    
    if entity_success and query_success:
        print("\n🎉 ALL TESTS PASSED! The query engine is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Additional fixes may be needed.")
        return False

def main():
    """Run the automated debug and fix process."""
    
    print("🤖 AUTOMATED DEBUG AND FIX PROCESS")
    print("=" * 60)
    
    # Step 1: Test current state
    print("\n📋 Step 1: Testing current state...")
    initial_entity_success, _ = test_entity_extraction_automated()
    initial_query_success, _ = test_process_query_automated()
    
    # Step 2: Apply fixes
    print("\n📋 Step 2: Applying fixes...")
    
    # Apply entity extraction fix
    fix_entity_extraction_issue()
    
    # Apply function name fix
    fix_function_name_issue()
    
    # Add error handling
    add_error_handling()
    
    # Step 3: Test after fixes
    print("\n📋 Step 3: Testing after fixes...")
    final_success = run_comprehensive_test()
    
    # Step 4: Summary
    print("\n📋 Step 4: Final summary...")
    if final_success:
        print("🎉 SUCCESS: All issues have been resolved!")
        print("The query engine should now work correctly.")
    else:
        print("⚠️ WARNING: Some issues may remain.")
        print("Please check the error messages above for additional fixes needed.")
    
    return final_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 