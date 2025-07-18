import os
import fitz  # PyMuPDF
import json
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import traceback

def main():
    try:
        # Load environment variables (for consistency)
        load_dotenv()

        # Constants
        DOCS_FOLDER = "Documents"

        # Check if Documents folder exists
        if not os.path.exists(DOCS_FOLDER):
            print(f"❌ Error: '{DOCS_FOLDER}' folder not found!")
            print(f"   Current directory: {os.getcwd()}")
            print(f"   Please make sure the '{DOCS_FOLDER}' folder exists in the current directory.")
            return

        # Load sentence transformer model
        print("🔍 Loading embedding model...")
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("   Make sure you have installed sentence-transformers: pip install sentence-transformers")
            return

        # Function to extract text from a PDF file
        def get_text_from_pdf(pdf_path):
            try:
                text = ""
                with fitz.open(pdf_path) as doc:
                    for page in doc:
                        text += page.get_text()
                return text
            except Exception as e:
                print(f"   ⚠️ Warning: Could not process {pdf_path}: {e}")
                return ""

        # Read and embed documents
        documents = []
        file_names = []
        file_paths = []

        print("📂 Scanning for PDFs...")
        pdf_count = 0
        for root, _, files in os.walk(DOCS_FOLDER):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_count += 1
                    path = os.path.join(root, file)
                    print(f"  📄 Processing ({pdf_count}): {file}")
                    text = get_text_from_pdf(path)
                    if text.strip():  # Only add if text was extracted successfully
                        documents.append(text)
                        file_names.append(file)
                        file_paths.append(path)
                    else:
                        print(f"     ⚠️ Skipped {file} (no text extracted)")

        if not documents:
            print("⚠️ No PDF files with extractable text found in 'Documents/' folder.")
            print("   Make sure your PDF files contain text (not just images).")
            return

        print(f"✅ Successfully processed {len(documents)} PDF files")

        # Create embeddings
        print("🧠 Creating embeddings...")
        try:
            embeddings = model.encode(documents)
            # Convert to numpy array if it's not already
            embeddings = np.array(embeddings)
            print(f"✅ Created embeddings with shape: {embeddings.shape}")
        except Exception as e:
            print(f"❌ Error creating embeddings: {e}")
            return

        # Build FAISS index
        print("💾 Building FAISS index...")
        try:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            print(f"✅ FAISS index built with {index.ntotal} vectors")
        except Exception as e:
            print(f"❌ Error building FAISS index: {e}")
            return

        # Save FAISS index
        try:
            faiss.write_index(index, "vector_index.faiss")
            print("✅ FAISS index saved successfully")
        except Exception as e:
            print(f"❌ Error saving FAISS index: {e}")
            return

        # Save metadata
        try:
            metadata = {
                "documents": documents,
                "file_names": file_names,
                "file_paths": file_paths,
                "embedding_dimension": dimension,
                "total_documents": len(documents)
            }
            
            with open("metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            print("✅ Metadata saved successfully")
        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
            return

        print("\n🎉 Document processing complete!")
        print(f"📁 FAISS index saved to: {os.path.abspath('vector_index.faiss')}")
        print(f"📁 Metadata saved to: {os.path.abspath('metadata.json')}")
        print(f"📊 Processed {len(documents)} documents with {dimension}-dimensional embeddings")

    except Exception as e:
        print(f"❌ Unexpected error occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
