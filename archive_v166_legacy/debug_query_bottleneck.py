#!/usr/bin/env python3
"""
Debug Query Bottleneck - Trace through query processing to find where it gets stuck
"""

import time
import sys
import os
import traceback

def debug_query_processing():
    """Debug the query processing step by step"""
    
    print("🔍 DEBUGGING QUERY PROCESSING BOTTLENECK")
    print("=" * 50)
    
    # Test query
    test_query = "How should I approach a strategic decision?"
    
    try:
        # Step 1: Import check
        print("📦 Step 1: Checking imports...")
        start_time = time.time()
        
        try:
            from query_engine import process_query
            import_time = time.time() - start_time
            print(f"✅ Imports successful: {import_time:.2f}s")
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return False
        
        # Step 2: Check if data structures are loaded
        print("\n📊 Step 2: Checking data structures...")
        start_time = time.time()
        
        try:
            # Check if FAISS index exists
            import faiss
            if os.path.exists("vector_index.faiss"):
                print("✅ FAISS index found")
            else:
                print("❌ FAISS index missing")
                return False
            
            # Check if metadata exists
            if os.path.exists("metadata.json"):
                print("✅ Metadata found")
            else:
                print("❌ Metadata missing")
                return False
                
            data_check_time = time.time() - start_time
            print(f"✅ Data structures check: {data_check_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Data structure check failed: {e}")
            return False
        
        # Step 3: Test each major function separately
        print("\n🔧 Step 3: Testing individual functions...")
        
        # Test domain detection
        print("  🔍 Testing domain detection...")
        start_time = time.time()
        try:
            from query_engine import detect_query_domain
            domain = detect_query_domain(test_query)
            domain_time = time.time() - start_time
            print(f"    ✅ Domain detection: {domain_time:.2f}s -> '{domain}'")
        except Exception as e:
            print(f"    ❌ Domain detection failed: {e}")
            return False
        
        # Test concept extraction
        print("  📚 Testing concept extraction...")
        start_time = time.time()
        try:
            from query_engine import get_top_ranked_concepts
            concepts = get_top_ranked_concepts(test_query, top_k=3)
            concept_time = time.time() - start_time
            print(f"    ✅ Concept extraction: {concept_time:.2f}s -> {len(concepts)} concepts")
        except Exception as e:
            print(f"    ❌ Concept extraction failed: {e}")
            return False
        
        # Test entity extraction
        print("  🏷️ Testing entity extraction...")
        start_time = time.time()
        try:
            from query_engine import extract_enhanced_entities
            entities = extract_enhanced_entities(test_query)
            entity_time = time.time() - start_time
            print(f"    ✅ Entity extraction: {entity_time:.2f}s -> {len(entities)} entities")
        except Exception as e:
            print(f"    ❌ Entity extraction failed: {e}")
            return False
        
        # Step 4: Test API call simulation
        print("\n🤖 Step 4: Testing API call simulation...")
        start_time = time.time()
        try:
            from query_engine import robust_api_call
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Test with minimal prompt
            test_prompt = "Test response"
            test_message = "Hello"
            
            api_response = robust_api_call(client, test_prompt, test_message, max_tokens=50)
            api_time = time.time() - start_time
            print(f"    ✅ API call test: {api_time:.2f}s")
            
        except Exception as e:
            print(f"    ❌ API call test failed: {e}")
            return False
        
        # Step 5: Full query test with timing
        print("\n🚀 Step 5: Full query processing test...")
        start_time = time.time()
        
        try:
            result = process_query(test_query)
            full_time = time.time() - start_time
            
            print(f"✅ Full query processing: {full_time:.2f}s")
            print(f"📊 Result length: {len(result)} characters")
            
            if full_time > 10:
                print("⚠️  WARNING: Query processing is very slow!")
            elif full_time > 5:
                print("⚠️  WARNING: Query processing is slow")
            else:
                print("✅ Query processing speed is acceptable")
                
        except Exception as e:
            print(f"❌ Full query processing failed: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return False
        
        # Step 6: Memory usage check
        print("\n💾 Step 6: Memory usage check...")
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"    📊 Memory usage: {memory_mb:.1f} MB")
            
            if memory_mb > 500:
                print("    ⚠️  High memory usage detected")
            else:
                print("    ✅ Memory usage is normal")
                
        except ImportError:
            print("    ℹ️  psutil not available for memory check")
        
        print("\n" + "=" * 50)
        print("🎯 DEBUG SUMMARY")
        print("=" * 50)
        
        if full_time < 5:
            print("✅ Query processing is working normally")
        else:
            print("⚠️  Query processing is slow - check the timing above")
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return False

def main():
    """Main debug function"""
    print("🚀 QUERY BOTTLENECK DEBUG")
    print("=" * 50)
    
    success = debug_query_processing()
    
    if success:
        print("\n✅ Debug completed successfully")
    else:
        print("\n❌ Debug found issues")
    
    print("\n💡 Next steps:")
    print("1. If API calls are slow - check OpenAI API")
    print("2. If imports are slow - restart Python")
    print("3. If data loading is slow - check disk I/O")
    print("4. If memory is high - restart server")

if __name__ == "__main__":
    main() 