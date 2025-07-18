 import json
import faiss
from openai import OpenAI
import os
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import sys
import traceback

# Load environment variables
print("🔍 Loading environment variables...")
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not set in environment variables.")
    print("   Please set it in your .env file or environment.")
    sys.exit(1)

# Initialize OpenAI client with new API
client = OpenAI(api_key=openai_api_key)

# Load FAISS index and metadata
try:
    index = faiss.read_index("vector_index.faiss")
except Exception as e:
    print(f"❌ Error loading FAISS index: {e}")
    sys.exit(1)

try:
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    documents = metadata["documents"]
    file_names = metadata.get("file_names", ["Unknown"] * len(documents))
    file_paths = metadata.get("file_paths", file_names)
except Exception as e:
    print(f"❌ Error loading metadata: {e}")
    sys.exit(1)

# Load embedding model
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"❌ Error loading embedding model: {e}")
    sys.exit(1)

print("\n✅ Query engine is ready!")
print("💡 This engine will synthesize answers from multiple relevant documents, prioritizing your materials but supplementing with GPT's own knowledge if needed.")

# Main loop
try:
    while True:
        try:
            query = input("\nAsk a question (or type 'exit'): ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting. Goodbye!")
            break
        if query.strip().lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break
        if not query.strip():
            print("⚠️ Please enter a non-empty question.")
            continue
        
        # Default to retrieving 5 documents for synthesis (no prompt)
        k = 5
        
        # Embed the query
        try:
            query_embedding = model.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")
        except Exception as e:
            print(f"❌ Error embedding query: {e}")
            continue
            
        # Search FAISS index
        try:
            D, I = index.search(query_embedding, k)
            top_indices = I[0]
            if len(top_indices) == 0 or top_indices[0] == -1:
                print("⚠️ No results found in the index.")
                continue
        except Exception as e:
            print(f"❌ Error searching FAISS index: {e}")
            continue
            
        # Show retrieved documents
        print(f"\n📚 Retrieved {len(top_indices)} relevant documents:")
        for rank, idx in enumerate(top_indices, 1):
            if idx == -1:
                continue
            print(f"  [{rank}] {file_names[idx]}")
            
        # Combine relevant document content
        relevant_docs = []
        for idx in top_indices:
            if idx != -1:
                relevant_docs.append(documents[idx])
        
        # Create comprehensive context from multiple documents
        combined_context = "\n\n---\n\n".join(relevant_docs)
        
        # Truncate if too long (to avoid token limits)
        max_context_length = 8000  # Conservative limit
        if len(combined_context) > max_context_length:
            combined_context = combined_context[:max_context_length] + "...\n[Content truncated for length]"
            print(f"⚠️ Context was truncated to {max_context_length} characters to fit token limits.")
        
        # Generate synthesized answer using new API
        prompt = f"""You are an expert assistant. Use the following document excerpts from the user's own materials as your primary source to answer the question. 
Give more weight to the provided materials, but if the answer requires information not found in the materials, you may supplement with your own knowledge. 
If you use your own knowledge, clearly indicate which parts are from your own knowledge and which are from the provided materials.

Document excerpts:
{combined_context}

Question: {query}

Synthesized Answer (prioritize the provided materials, supplement with your own knowledge if needed):"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            answer = response.choices[0].message.content.strip()
            print(f"\n🎯 Synthesized Answer:\n{answer}")
            print(f"\n📊 Sources: {len(top_indices)} documents synthesized")
            
        except Exception as e:
            print(f"❌ Error from OpenAI API: {e}")
            traceback.print_exc()
            
except KeyboardInterrupt:
    print("\n👋 Exiting. Goodbye!")