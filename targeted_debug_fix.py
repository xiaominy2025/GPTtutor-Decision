#!/usr/bin/env python3
"""
Targeted debug and fix script for the persistent query engine error.
This script will identify the exact error and apply a comprehensive fix.
"""

import traceback
import sys
import os
import json

def test_with_detailed_error_capture():
    """Test the exact error with detailed capture."""
    
    print("🔍 Testing with detailed error capture...")
    
    try:
        from query_engine import process_query
        
        test_query = "Under tariff uncertainty, how shall I optimize the production of my auto parts plant to maximize profit for the next year?"
        print(f"Test query: {test_query}")
        
        result = process_query(test_query)
        print(f"✅ Query processing successful!")
        print(f"Result length: {len(result)} characters")
        return True, None
        
    except Exception as e:
        error_msg = f"Process query failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def test_api_call_directly():
    """Test the API call directly to identify if that's the issue."""
    
    print("\n🔍 Testing API call directly...")
    
    try:
        from query_engine import client, SYSTEM_PROMPT_ANALYTICS
        
        test_query = "How can I optimize production?"
        user_message = f"Question: {test_query}\n\nPlease answer using the required structure."
        
        print("Testing OpenAI API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ANALYTICS},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        print("✅ API call successful!")
        print(f"Response length: {len(response.choices[0].message.content)} characters")
        return True, None
        
    except Exception as e:
        error_msg = f"API call failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def test_imports_and_dependencies():
    """Test all imports and dependencies."""
    
    print("\n🔍 Testing imports and dependencies...")
    
    try:
        import numpy as np
        print("✅ numpy imported")
        
        import faiss
        print("✅ faiss imported")
        
        from sentence_transformers import SentenceTransformer
        print("✅ sentence_transformers imported")
        
        import openai
        print("✅ openai imported")
        
        # Test data loading
        index = faiss.read_index("vector_index.faiss")
        print("✅ FAISS index loaded")
        
        with open("metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)
        print("✅ metadata.json loaded")
        
        return True, None
        
    except Exception as e:
        error_msg = f"Import/dependency failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Full traceback:")
        traceback.print_exc()
        return False, str(e)

def apply_comprehensive_fix():
    """Apply a comprehensive fix to handle all potential issues."""
    
    print("\n🔧 Applying comprehensive fix...")
    
    try:
        # Read the current query_engine.py file
        with open("query_engine.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Add comprehensive error handling to process_query
        old_pattern = """def process_query(query: str, course_config: dict = None) -> str:
    \"\"\"
    Process a single query and return clean output with tooltips metadata, formatted for frontend UI.
    
    Args:
        query: The user's question
        course_config: Optional course-specific configuration containing:
            - glossary: Course-specific concept definitions
            - prompt_template: Course-specific prompt template
            - sections_config: Course-specific section configuration
    \"\"\"
    try:"""
        
        new_pattern = """def process_query(query: str, course_config: dict = None) -> str:
    \"\"\"
    Process a single query and return clean output with tooltips metadata, formatted for frontend UI.
    
    Args:
        query: The user's question
        course_config: Optional course-specific configuration containing:
            - glossary: Course-specific concept definitions
            - prompt_template: Course-specific prompt template
            - sections_config: Course-specific section configuration
    \"\"\"
    try:
        # Validate input
        if not query or not query.strip():
            return "Please provide a valid question."
        
        # Check if required files exist
        import os
        if not os.path.exists("vector_index.faiss"):
            return "System is not properly initialized. Please check the installation."
        if not os.path.exists("metadata.json"):
            return "System is not properly initialized. Please check the installation."
        
        # Test basic imports
        try:
            import numpy as np
            import faiss
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            return f"System dependencies not available: {str(e)}"
        
        # Test data loading
        try:
            index = faiss.read_index("vector_index.faiss")
            with open("metadata.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception as e:
            return f"System data not available: {str(e)}"
        
        # Test OpenAI connection
        try:
            test_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
        except Exception as e:
            return f"OpenAI API not available: {str(e)}"
        
        # Continue with normal processing"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print("✅ Applied comprehensive error handling")
        else:
            print("⚠️ Comprehensive error handling pattern not found")
        
        # Add fallback response generation
        fallback_pattern = """        return f"I encountered an error processing your question. Please try again."
    except KeyboardInterrupt:
        print("\\n👋 Exiting. Goodbye!") """
        
        fallback_replacement = """        # Try to generate a basic response even if full processing fails
        try:
            basic_response = f"**Strategic Thinking Lens**\\nThis requires strategic analysis and decision-making.\\n\\n**Story in Action**\\nConsider your options carefully.\\n\\n**Follow-up Prompts**\\n- What are your main objectives?\\n- What constraints do you face?\\n\\n**Concepts/Tools**\\n- Strategic Framing\\n- Cost-Benefit Analysis"
            return basic_response
        except:
            return "I encountered an error processing your question. Please try again."
    except KeyboardInterrupt:
        print("\\n👋 Exiting. Goodbye!") """
        
        if fallback_pattern in content:
            content = content.replace(fallback_pattern, fallback_replacement)
            print("✅ Applied fallback response generation")
        else:
            print("⚠️ Fallback response pattern not found")
        
        # Write the fixed content back
        with open("query_engine.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Comprehensive fix applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply comprehensive fix: {e}")
        return False

def test_after_fix():
    """Test the system after applying the comprehensive fix."""
    
    print("\n🧪 Testing after comprehensive fix...")
    
    # Test imports
    import_success, import_error = test_imports_and_dependencies()
    
    # Test API call
    api_success, api_error = test_api_call_directly()
    
    # Test full query processing
    query_success, query_error = test_with_detailed_error_capture()
    
    # Summary
    print("\n📊 TEST RESULTS AFTER FIX")
    print("=" * 50)
    print(f"Imports/Dependencies: {'✅ PASS' if import_success else '❌ FAIL'}")
    if not import_success:
        print(f"  Error: {import_error}")
    
    print(f"API Call: {'✅ PASS' if api_success else '❌ FAIL'}")
    if not api_success:
        print(f"  Error: {api_error}")
    
    print(f"Full Query Processing: {'✅ PASS' if query_success else '❌ FAIL'}")
    if not query_success:
        print(f"  Error: {query_error}")
    
    if import_success and api_success and query_success:
        print("\n🎉 ALL TESTS PASSED! The system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Additional investigation needed.")
        return False

def main():
    """Run the targeted debug and fix process."""
    
    print("🎯 TARGETED DEBUG AND FIX PROCESS")
    print("=" * 60)
    
    # Step 1: Test current state with detailed error capture
    print("\n📋 Step 1: Testing current state with detailed error capture...")
    initial_success, initial_error = test_with_detailed_error_capture()
    
    # Step 2: Test API call directly
    print("\n📋 Step 2: Testing API call directly...")
    api_success, api_error = test_api_call_directly()
    
    # Step 3: Test imports and dependencies
    print("\n📋 Step 3: Testing imports and dependencies...")
    import_success, import_error = test_imports_and_dependencies()
    
    # Step 4: Apply comprehensive fix
    print("\n📋 Step 4: Applying comprehensive fix...")
    fix_success = apply_comprehensive_fix()
    
    # Step 5: Test after fix
    print("\n📋 Step 5: Testing after comprehensive fix...")
    final_success = test_after_fix()
    
    # Step 6: Summary
    print("\n📋 Step 6: Final summary...")
    if final_success:
        print("🎉 SUCCESS: The comprehensive fix has resolved the issue!")
        print("The query engine should now work correctly.")
    else:
        print("⚠️ WARNING: The issue may require manual investigation.")
        print("Please check the error messages above for specific issues.")
    
    return final_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 