#!/usr/bin/env python3
"""
Flask Application for V1.6.6 Stable
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
        "version": "V1.6.6",
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
        "message": "V1.6.6 API is working",
        "version": "1.6.6",
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
