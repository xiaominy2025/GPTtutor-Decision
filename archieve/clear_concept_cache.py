#!/usr/bin/env python3
"""
Clear concept embeddings cache to fix index mismatch
"""
import sys
import os

def clear_concept_cache():
    """Clear the concept embeddings cache"""
    print("🧹 CLEARING CONCEPT EMBEDDINGS CACHE")
    print("=" * 50)
    
    try:
        # Import query engine and clear cache
        import query_engine
        
        # Clear the global cache
        query_engine._concept_embeddings_cache = None
        print("✅ Concept embeddings cache cleared")
        
        # Test concept extraction
        test_query = "my team members are reluctant to give up his legacy projects"
        concepts = query_engine.get_top_ranked_concepts(test_query, top_k=3)
        
        print(f"✅ Concept extraction test successful")
        print(f"   Query: {test_query}")
        print(f"   Found {len(concepts)} concepts:")
        for name, definition in concepts:
            print(f"   - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False

if __name__ == "__main__":
    if clear_concept_cache():
        print("\n✅ Cache cleared successfully")
        print("   V1.6.5 alignment verification can now proceed")
    else:
        print("\n❌ Failed to clear cache") 