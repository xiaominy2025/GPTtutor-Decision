#!/usr/bin/env python3
"""
Fix Vector Index Mismatch
Resolves the index out of bounds error in semantic concept extraction
"""
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def fix_vector_index_mismatch():
    """Fix the vector index mismatch by recreating the index"""
    print("🔧 FIXING VECTOR INDEX MISMATCH")
    print("=" * 50)
    
    try:
        # Load current glossary
        with open("courses/decision/glossary.json", 'r', encoding='utf-8') as f:
            glossary = json.load(f)
        
        print(f"✅ Current glossary has {len(glossary)} concepts")
        
        # Check if vector index exists
        if os.path.exists("vector_index.faiss"):
            # Load existing index to check size
            old_index = faiss.read_index("vector_index.faiss")
            print(f"📊 Existing index has {old_index.ntotal} vectors")
            
            if old_index.ntotal != len(glossary):
                print(f"❌ Mismatch detected: index has {old_index.ntotal} vectors, glossary has {len(glossary)} concepts")
                
                # Create backup
                if os.path.exists("vector_index.faiss"):
                    os.rename("vector_index.faiss", "vector_index_backup.faiss")
                    print("✅ Created backup: vector_index_backup.faiss")
                
                # Recreate index
                print("🔄 Recreating vector index...")
                model = SentenceTransformer("all-MiniLM-L6-v2")
                
                # Create concept texts
                concept_texts = []
                for name, concept_data in glossary.items():
                    if isinstance(concept_data, dict):
                        definition = concept_data["definition"]
                    else:
                        definition = concept_data
                    concept_text = f"{definition} {name.replace('-', ' ')}"
                    concept_texts.append(concept_text)
                
                # Generate embeddings
                embeddings = model.encode(concept_texts)
                
                # Create new index
                dimension = embeddings.shape[1]
                new_index = faiss.IndexFlatIP(dimension)
                new_index.add(embeddings.astype('float32'))
                
                # Save new index
                faiss.write_index(new_index, "vector_index.faiss")
                print(f"✅ New index created with {new_index.ntotal} vectors")
                
                # Update metadata
                metadata = {
                    "documents": concept_texts,
                    "file_names": [f"concept_{i}" for i in range(len(concept_texts))],
                    "concept_names": list(glossary.keys())
                }
                
                with open("metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                print("✅ Metadata updated")
                return True
            else:
                print("✅ Index size matches glossary size")
                return True
        else:
            print("❌ Vector index not found, creating new one...")
            # Create new index
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            concept_texts = []
            for name, concept_data in glossary.items():
                if isinstance(concept_data, dict):
                    definition = concept_data["definition"]
                else:
                    definition = concept_data
                concept_text = f"{definition} {name.replace('-', ' ')}"
                concept_texts.append(concept_text)
            
            embeddings = model.encode(concept_texts)
            dimension = embeddings.shape[1]
            new_index = faiss.IndexFlatIP(dimension)
            new_index.add(embeddings.astype('float32'))
            
            faiss.write_index(new_index, "vector_index.faiss")
            print(f"✅ New index created with {new_index.ntotal} vectors")
            
            metadata = {
                "documents": concept_texts,
                "file_names": [f"concept_{i}" for i in range(len(concept_texts))],
                "concept_names": list(glossary.keys())
            }
            
            with open("metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print("✅ Metadata created")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing vector index: {e}")
        return False

def test_concept_extraction():
    """Test concept extraction after fix"""
    print("\n🧪 TESTING CONCEPT EXTRACTION")
    print("=" * 50)
    
    try:
        import query_engine
        
        test_query = "my team members are reluctant to give up his legacy projects"
        concepts = query_engine.get_top_ranked_concepts(test_query, top_k=3)
        
        print(f"✅ Concept extraction successful")
        print(f"   Query: {test_query}")
        print(f"   Found {len(concepts)} concepts:")
        for name, definition in concepts:
            print(f"   - {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Concept extraction test failed: {e}")
        return False

if __name__ == "__main__":
    # Fix vector index mismatch
    if fix_vector_index_mismatch():
        print("\n✅ Vector index mismatch fixed")
        
        # Test concept extraction
        if test_concept_extraction():
            print("\n🎯 V1.6.5 alignment verification can now proceed")
        else:
            print("\n⚠️ Concept extraction still has issues")
    else:
        print("\n❌ Failed to fix vector index mismatch") 