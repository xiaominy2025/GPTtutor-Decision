#!/usr/bin/env python3
"""
Debug script to trace process_query function execution
"""

import re
import query_engine

def test_process_query_with_debug():
    """Test process_query with debug output"""
    
    query = "How do I choose between two job offers?"
    
    print("🧪 Testing process_query with debug output")
    print("=" * 60)
    
    # Test the raw answer from the API
    print("📋 Step 1: Getting raw answer from API...")
    
    # Import the necessary components
    import openai
    import numpy as np
    
    # Get the raw answer
    query_embedding = query_engine.model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    D, I = query_engine.index.search(query_embedding, 5)
    top_indices = I[0][:2]
    
    if len(top_indices) == 0 or top_indices[0] == -1:
        print("❌ No relevant documents found")
        return
    
    relevant_docs = []
    for idx in top_indices:
        if idx != -1:
            relevant_docs.append(query_engine.documents[idx])
    
    combined_context = query_engine.smart_context_truncation(relevant_docs, max_chars=8000)
    user_message = f"Relevant document excerpts:\n{combined_context}\n\nQuestion: {query}\n\nPlease answer using the required structure."
    optimal_tokens = query_engine.calculate_optimal_tokens(len(query), len(combined_context))
    
    response, error = query_engine.robust_api_call(query_engine.client, query_engine.SYSTEM_PROMPT_ANALYTICS, user_message, max_tokens=optimal_tokens)
    
    if error:
        print(f"❌ API Error: {error}")
        return
    
    if response is None:
        print("❌ No response from API")
        return
    
    content = response.choices[0].message.content
    answer_raw = content.strip() if content is not None else ""
    
    print(f"📊 Raw answer length: {len(answer_raw)} characters")
    
    # Extract raw lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', answer_raw, re.DOTALL | re.IGNORECASE)
    if lens_match:
        raw_lens = lens_match.group(1).strip()
        raw_word_count = len(raw_lens.split())
        print(f"📊 Raw lens word count: {raw_word_count}")
        print(f"📄 Raw lens content: {raw_lens[:200]}...")
    
    # Test enforce_thinkpal_structure
    print("\n📋 Step 2: Testing enforce_thinkpal_structure...")
    enhanced_answer = query_engine.enforce_thinkpal_structure(answer_raw, query)
    
    # Extract enhanced lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', enhanced_answer, re.DOTALL | re.IGNORECASE)
    if lens_match:
        enhanced_lens = lens_match.group(1).strip()
        enhanced_word_count = len(enhanced_lens.split())
        print(f"📊 Enhanced lens word count: {enhanced_word_count}")
        print(f"📄 Enhanced lens content: {enhanced_lens[:200]}...")
        
        if enhanced_word_count >= 120:
            print("✅ PASS: Lens was enhanced correctly")
        else:
            print("❌ FAIL: Lens was not enhanced")
    
    # Test full process_query
    print("\n📋 Step 3: Testing full process_query...")
    final_result = query_engine.process_query(query)
    
    # Extract final lens
    lens_match = re.search(r'\*\*Strategic Thinking Lens\*\*\s*\n(.*?)(?=\n\n\*\*|$)', final_result, re.DOTALL | re.IGNORECASE)
    if lens_match:
        final_lens = lens_match.group(1).strip()
        final_word_count = len(final_lens.split())
        print(f"📊 Final lens word count: {final_word_count}")
        print(f"📄 Final lens content: {final_lens[:200]}...")
        
        if final_word_count >= 120:
            print("✅ PASS: Final result meets requirements")
        else:
            print("❌ FAIL: Final result does not meet requirements")
    
    print("\n" + "=" * 60)
    print("🏁 Debug Test Complete")

if __name__ == "__main__":
    test_process_query_with_debug() 