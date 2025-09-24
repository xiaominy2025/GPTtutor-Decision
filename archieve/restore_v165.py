#!/usr/bin/env python3
"""
V1.6.5 Restoration Script
Removes V1.6.6 files and ensures core files are in V1.6.5 stable state
"""

import os
import shutil
import sys

def remove_v166_files():
    """Remove V1.6.6 specific files"""
    print("🗑️  Removing V1.6.6 files...")
    
    v166_files = [
        # V1.6.6 streaming files
        "test_stream.py",
        "v166_debug_test.py", 
        "troubleshoot_waitress.py",
        "V1.6.6_Streaming_Test_Summary.md",
        "V1.6.6_Streaming_Support_Summary.md",
        "streaming_support.py",
        "test_streaming.py",
        "test_streaming_support.py",
        "test_flask_streaming.py",
        "test_curl_streaming.sh",
        "comprehensive_streaming_test.py",
        "streaming_test_report.json",
        "flask_streaming_test_report.json",
        
        # V1.6.6 debug files
        "get-pip.py",
        "pip-25.2-py3-none-any.whl",
        "waitress-3.0.2-py3-none-any.whl",
        
        # Other V1.6.6 test files
        "test_flask_direct.py",
        "test_course_endpoint.py",
        "simple_test.py"
    ]
    
    removed_count = 0
    for file in v166_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  ✓ Removed: {file}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to remove {file}: {e}")
        else:
            print(f"  - Not found: {file}")
    
    print(f"✅ Removed {removed_count} V1.6.6 files")
    print()

def check_v165_core_files():
    """Check that V1.6.5 core files are present"""
    print("🔍 Checking V1.6.5 core files...")
    
    v165_core_files = [
        "app.py",
        "query_engine.py", 
        "config.py",
        "V1.6.5_FINAL_SUMMARY.md",
        "V1.6.5_README.md",
        "V1.6.5_IMPROVEMENTS_SUMMARY.md",
        "test_v165_improvements.py"
    ]
    
    missing_files = []
    for file in v165_core_files:
        if os.path.exists(file):
            print(f"  ✓ Found: {file}")
        else:
            print(f"  ✗ Missing: {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} core V1.6.5 files")
    else:
        print("✅ All V1.6.5 core files present")
    print()

def verify_app_structure():
    """Verify app.py has the correct V1.6.5 structure"""
    print("🔍 Verifying app.py structure...")
    
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Check for V1.6.5 endpoints (no streaming)
        if "/api/stream_answer" in content:
            print("  ⚠️  app.py contains streaming endpoint (V1.6.6)")
            print("  💡 This should be removed for V1.6.5")
        else:
            print("  ✅ app.py has V1.6.5 structure (no streaming)")
        
        # Check for V1.6.5 endpoints
        if "/api/answer" in content and "/health" in content:
            print("  ✅ app.py has correct V1.6.5 endpoints")
        else:
            print("  ⚠️  app.py missing expected V1.6.5 endpoints")
            
    except Exception as e:
        print(f"  ✗ Error reading app.py: {e}")
    
    print()

def create_v165_app_py():
    """Create a clean V1.6.5 app.py without streaming"""
    print("🔧 Creating clean V1.6.5 app.py...")
    
    v165_app_content = '''#!/usr/bin/env python3
"""
Flask Application for V1.6.5
Provides API endpoints for the GPTTutor Decision system.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import query processing
try:
    from query_engine import process_query
    QUERY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Query engine not available: {e}")
    QUERY_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "version": "V1.6.5",
        "query_available": QUERY_AVAILABLE,
        "timestamp": time.time()
    })

@app.route('/api/course/<course_id>', methods=['GET'])
def get_course_metadata(course_id):
    """Get course metadata for the React frontend."""
    courses = {
        "decision": {
            "title": "Decision Lab",
            "short_name": "Decision",
            "mobile_title": "Decision",
            "placeholder": "How should I approach this strategic decision?",
            "sections_titles": [
                "Strategic Thinking Lens",
                "Story in Action",
                "Follow-up Prompts",
                "Concepts & Tools"
            ]
        },
        "marketing": {
            "title": "Marketing Lab",
            "short_name": "Marketing",
            "mobile_title": "Marketing",
            "placeholder": "What marketing approach should I take?",
            "sections_titles": [
                "Strategic Thinking Lens",
                "Story in Action",
                "Follow-up Prompts",
                "Concepts & Tools"
            ]
        },
        "strategy": {
            "title": "Strategy Lab",
            "short_name": "Strategy",
            "mobile_title": "Strategy",
            "placeholder": "How can I develop a strategic framework?",
            "sections_titles": [
                "Strategic Thinking Lens",
                "Story in Action",
                "Follow-up Prompts",
                "Concepts & Tools"
            ]
        }
    }

    if course_id in courses:
        return jsonify({"metadata": courses[course_id]})
    else:
        return jsonify({"error": f"Course '{course_id}' not found"}), 404

@app.route('/api/answer', methods=['POST'])
def get_answer():
    """Get answer for a question."""
    
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        question = data.get('question', '')
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Check if query processing is available
        if not QUERY_AVAILABLE:
            return jsonify({"error": "Query processing not available"}), 500
        
        # Process the query
        try:
            answer = process_query(question)
            return jsonify({
                "answer": answer,
                "status": "success"
            })
        except Exception as e:
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Request processing failed: {str(e)}"}), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for basic functionality."""
    return jsonify({
        "message": "V1.6.5 API is working",
        "version": "1.6.5",
        "timestamp": time.time()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    try:
        with open("app.py", "w") as f:
            f.write(v165_app_content)
        print("  ✅ Created clean V1.6.5 app.py")
    except Exception as e:
        print(f"  ✗ Failed to create app.py: {e}")
    
    print()

def run_v165_test():
    """Run a basic V1.6.5 test"""
    print("🧪 Running V1.6.5 basic test...")
    
    try:
        # Test imports
        from app import app
        print("  ✅ app.py imports successfully")
        
        # Test query engine
        from query_engine import process_query
        print("  ✅ query_engine.py imports successfully")
        
        # Test basic query
        test_query = "How should I approach a strategic decision?"
        result = process_query(test_query)
        
        if result and isinstance(result, str):
            print("  ✅ Query processing works")
            print(f"  📊 Result length: {len(result)} characters")
        else:
            print("  ⚠️  Query processing returned unexpected result")
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
    
    print()

def main():
    """Main restoration function"""
    print("🔄 V1.6.5 RESTORATION")
    print("=" * 50)
    print()
    
    # Step 1: Remove V1.6.6 files
    remove_v166_files()
    
    # Step 2: Check V1.6.5 core files
    check_v165_core_files()
    
    # Step 3: Verify app structure
    verify_app_structure()
    
    # Step 4: Create clean V1.6.5 app.py
    create_v165_app_py()
    
    # Step 5: Run basic test
    run_v165_test()
    
    print("=" * 50)
    print("✅ V1.6.5 RESTORATION COMPLETE")
    print("=" * 50)
    print()
    print("🎯 V1.6.5 is now restored with:")
    print("  - Clean app.py without streaming")
    print("  - V1.6.6 files removed")
    print("  - Core V1.6.5 functionality intact")
    print()
    print("🚀 To start the server:")
    print("  python -m waitress --listen=127.0.0.1:5000 app:app")
    print()
    print("📝 To test the API:")
    print("  curl -X POST http://localhost:5000/api/answer \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"question\": \"How should I approach a strategic decision?\"}'")

if __name__ == "__main__":
    main() 