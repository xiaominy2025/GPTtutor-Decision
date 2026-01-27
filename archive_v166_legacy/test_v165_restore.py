#!/usr/bin/env python3
"""
Quick V1.6.5 Restoration Test
Tests if V1.6.5 is properly restored and working
"""

import sys
import os

def test_imports():
    """Test if core V1.6.5 modules can be imported"""
    print("🔍 Testing V1.6.5 imports...")
    
    try:
        from app import app
        print("✅ app.py imports successfully")
    except Exception as e:
        print(f"❌ app.py import failed: {e}")
        return False
    
    try:
        from query_engine import process_query
        print("✅ query_engine.py imports successfully")
    except Exception as e:
        print(f"❌ query_engine.py import failed: {e}")
        return False
    
    return True

def test_basic_query():
    """Test basic query processing"""
    print("\n🧪 Testing basic query processing...")
    
    try:
        from query_engine import process_query
        
        test_query = "How should I approach a strategic decision?"
        result = process_query(test_query)
        
        if result and isinstance(result, str):
            print("✅ Query processing works")
            print(f"📊 Result length: {len(result)} characters")
            return True
        else:
            print("❌ Query processing returned invalid result")
            return False
            
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        return False

def check_v165_files():
    """Check that V1.6.5 files are present"""
    print("\n📁 Checking V1.6.5 files...")
    
    v165_files = [
        "app.py",
        "query_engine.py",
        "config.py",
        "V1.6.5_FINAL_SUMMARY.md",
        "V1.6.5_README.md",
        "V1.6.5_IMPROVEMENTS_SUMMARY.md"
    ]
    
    missing_files = []
    for file in v165_files:
        if os.path.exists(file):
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} V1.6.5 files")
        return False
    else:
        print("✅ All V1.6.5 files present")
        return True

def main():
    """Run all V1.6.5 tests"""
    print("🚀 V1.6.5 RESTORATION VERIFICATION")
    print("=" * 50)
    
    # Test 1: Check files
    files_ok = check_v165_files()
    
    # Test 2: Test imports
    imports_ok = test_imports()
    
    # Test 3: Test query processing
    query_ok = test_basic_query()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    if files_ok:
        print("✅ V1.6.5 files: PRESENT")
    else:
        print("❌ V1.6.5 files: MISSING")
    
    if imports_ok:
        print("✅ Module imports: WORKING")
    else:
        print("❌ Module imports: FAILED")
    
    if query_ok:
        print("✅ Query processing: WORKING")
    else:
        print("❌ Query processing: FAILED")
    
    if files_ok and imports_ok and query_ok:
        print("\n🎉 V1.6.5 RESTORATION: SUCCESSFUL!")
        print("✅ V1.6.5 is fully restored and working")
        return True
    else:
        print("\n⚠️  V1.6.5 RESTORATION: INCOMPLETE")
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 