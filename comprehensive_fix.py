#!/usr/bin/env python3
"""
Comprehensive Fix - Remove all duplicate data loading and ensure proper lazy loading
"""

def fix_query_engine_comprehensive():
    """Fix all data loading issues in query_engine.py"""
    
    print("🔧 COMPREHENSIVE QUERY ENGINE FIX")
    print("=" * 50)
    
    # Read the current file
    with open("query_engine.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"📊 Original file: {len(lines)} lines")
    
    # Find and fix all problematic sections
    fixed_lines = []
    in_process_query = False
    skip_next_lines = 0
    
    for i, line in enumerate(lines):
        # Skip lines we're replacing
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
        
        # Check if we're entering process_query function
        if "def process_query(" in line:
            in_process_query = True
            fixed_lines.append(line)
            continue
        
        # Check if we're exiting process_query function
        if in_process_query and line.startswith("def "):
            in_process_query = False
        
        # Remove the duplicate FAISS loading in process_query
        if in_process_query and "index = faiss.read_index" in line:
            print(f"❌ Found duplicate FAISS loading at line {i+1}")
            # Skip this line and the next few lines that are part of the data loading
            skip_next_lines = 3  # Skip the faiss.read_index, metadata loading, and documents assignment
            continue
        
        # Remove the duplicate metadata loading
        if in_process_query and "with open(\"metadata.json\"" in line:
            print(f"❌ Found duplicate metadata loading at line {i+1}")
            skip_next_lines = 2  # Skip the metadata loading and documents assignment
            continue
        
        # Remove the duplicate documents assignment
        if in_process_query and "documents = metadata[\"documents\"]" in line:
            print(f"❌ Found duplicate documents assignment at line {i+1}")
            skip_next_lines = 1  # Skip this line
            continue
        
        # Remove the duplicate file_names assignment
        if in_process_query and "file_names = metadata.get" in line:
            print(f"❌ Found duplicate file_names assignment at line {i+1}")
            skip_next_lines = 1  # Skip this line
            continue
        
        # Remove the duplicate model loading
        if in_process_query and "model = SentenceTransformer" in line:
            print(f"❌ Found duplicate model loading at line {i+1}")
            skip_next_lines = 1  # Skip this line
            continue
        
        # Remove the duplicate nlp loading
        if in_process_query and "nlp = spacy.load" in line:
            print(f"❌ Found duplicate nlp loading at line {i+1}")
            skip_next_lines = 1  # Skip this line
            continue
        
        # Add the data loading call at the beginning of process_query
        if in_process_query and "course_config = {" in line:
            # Insert the data loading call before this line
            fixed_lines.append("        # Load data lazily\n")
            fixed_lines.append("        index, metadata, documents, file_names, model, nlp = load_data_lazily()\n")
            fixed_lines.append("\n")
            fixed_lines.append(line)
            continue
        
        # Keep all other lines
        fixed_lines.append(line)
    
    # Write the fixed file
    with open("query_engine.py", "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed file: {len(fixed_lines)} lines")
    print("💡 Removed all duplicate data loading")
    
    return True

def test_fixed_import():
    """Test if the comprehensive fix works"""
    print("\n🧪 Testing comprehensive fix...")
    
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
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main comprehensive fix function"""
    print("🚀 COMPREHENSIVE QUERY ENGINE FIX")
    print("=" * 50)
    
    # Fix the file
    if fix_query_engine_comprehensive():
        # Test the fix
        if test_fixed_import():
            print("\n🎉 SUCCESS: All data loading issues fixed!")
            print("⚡ Query engine should now start instantly")
            print("💡 Data loads only when needed")
        else:
            print("\n❌ Fix didn't work - manual intervention needed")
    else:
        print("\n❌ Could not fix the file")

if __name__ == "__main__":
    main() 