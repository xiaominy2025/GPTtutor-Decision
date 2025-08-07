#!/usr/bin/env python3
"""
Check vector index size and metadata alignment
"""
import faiss
import json

def check_vector_index():
    """Check vector index size and metadata alignment"""
    print("🔍 CHECKING VECTOR INDEX ALIGNMENT")
    print("=" * 50)
    
    try:
        # Load vector index
        index = faiss.read_index("vector_index.faiss")
        print(f"📊 Vector index has {index.ntotal} vectors")
        
        # Load metadata
        with open("metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"📊 Metadata has {len(metadata['documents'])} documents")
        print(f"📊 Metadata has {len(metadata['file_names'])} file names")
        print(f"📊 Metadata has {len(metadata.get('concept_names', []))} concept names")
        
        # Check if sizes match
        if index.ntotal == len(metadata['documents']):
            print("✅ Vector index and metadata sizes match")
        else:
            print(f"❌ Mismatch: index has {index.ntotal} vectors, metadata has {len(metadata['documents'])} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking vector index: {e}")
        return False

if __name__ == "__main__":
    check_vector_index() 