#!/usr/bin/env python3
"""
Fix Query Engine Import - Move heavy data loading to lazy initialization
"""

def fix_query_engine():
    """Fix the query_engine.py import issue by making data loading lazy"""
    
    print("🔧 Fixing query_engine.py import issue...")
    
    # Read the current file
    with open("query_engine.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the problematic data loading section
    old_loading_section = '''# Load data safely
try:
    index = faiss.read_index("vector_index.faiss")
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    documents = metadata["documents"]
    file_names = metadata.get("file_names", ["Unknown"] * len(documents))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    sys.exit(1)'''
    
    # Replace with lazy loading
    new_loading_section = '''# Global variables for lazy loading
_index = None
_metadata = None
_documents = None
_file_names = None
_model = None
_nlp = None

def load_data_lazily():
    """Load data only when needed"""
    global _index, _metadata, _documents, _file_names, _model, _nlp
    
    if _index is None:
        try:
            _index = faiss.read_index("vector_index.faiss")
            with open("metadata.json", "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            _documents = _metadata["documents"]
            _file_names = _metadata.get("file_names", ["Unknown"] * len(_documents))
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            _nlp = spacy.load("en_core_web_sm")
            print("✅ Data loaded successfully")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            sys.exit(1)
    
    return _index, _metadata, _documents, _file_names, _model, _nlp

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)'''
    
    # Replace the section
    if old_loading_section in content:
        content = content.replace(old_loading_section, new_loading_section)
        print("✅ Replaced data loading section")
    else:
        print("❌ Could not find the data loading section")
        return False
    
    # Write the fixed file
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Fixed query_engine.py")
    print("💡 Data will now load only when needed")
    
    return True

def test_fixed_import():
    """Test if the fixed import works"""
    print("\n🧪 Testing fixed import...")
    
    try:
        import time
        start_time = time.time()
        
        from query_engine import process_query
        
        import_time = time.time() - start_time
        print(f"✅ Import successful: {import_time:.2f}s")
        
        # Test a simple query to trigger data loading
        print("🔍 Testing data loading...")
        start_time = time.time()
        
        result = process_query("test")
        
        query_time = time.time() - start_time
        print(f"✅ Query successful: {query_time:.2f}s")
        print(f"📊 Result length: {len(result)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main fix function"""
    print("🚀 FIX QUERY ENGINE IMPORT")
    print("=" * 40)
    
    # Fix the file
    if fix_query_engine():
        # Test the fix
        if test_fixed_import():
            print("\n🎉 SUCCESS: Import issue fixed!")
            print("⚡ Query engine should now start much faster")
        else:
            print("\n❌ Fix didn't work - manual intervention needed")
    else:
        print("\n❌ Could not fix the file")

if __name__ == "__main__":
    main() 