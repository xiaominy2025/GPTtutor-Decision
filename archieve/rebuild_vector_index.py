#!/usr/bin/env python3
"""
Script to rebuild vector index with current concept embeddings
"""

import sys
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Add the Repeatability directory to the path
sys.path.insert(0, 'Repeatability')

def rebuild_vector_index():
    """Rebuild the vector index with current concept embeddings"""
    
    try:
        # Import the current query engine to get the concept glossary
        from query_engine import CONCEPT_GLOSSARY
        
        print("Rebuilding vector index with current concept embeddings...")
        
        # Load the sentence transformer model
        model = SentenceTransformer("all-mpnet-base-v2")
        
        # Create concept texts for embedding
        concept_texts = []
        concept_names = []
        
        for name, concept_data in CONCEPT_GLOSSARY.items():
            if isinstance(concept_data, dict):
                definition = concept_data["definition"]
            else:
                definition = concept_data
            
            # Create a more focused text that emphasizes the definition over the name
            concept_text = f"{definition} {name.replace('-', ' ')}"
            concept_texts.append(concept_text)
            concept_names.append(name)
        
        print(f"Creating embeddings for {len(concept_texts)} concepts...")
        
        # Generate embeddings
        embeddings = model.encode(concept_texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        index.add(embeddings.astype('float32'))
        
        # Save the index
        faiss.write_index(index, "Repeatability/vector_index.faiss")
        
        print(f"✅ Vector index rebuilt successfully with {len(concept_names)} concepts")
        print(f"Index saved to: Repeatability/vector_index.faiss")
        
        # Test the index
        print("\nTesting the rebuilt index...")
        test_query = "Under tariff uncertainty, how do I plan my production?"
        query_embedding = model.encode([test_query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = index.search(query_embedding.astype('float32'), 5)
        
        print("Top 5 concept matches:")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            concept_name = concept_names[idx]
            print(f"{i+1}. {concept_name}: {score:.3f}")
        
    except Exception as e:
        print(f"Error rebuilding vector index: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    rebuild_vector_index()
