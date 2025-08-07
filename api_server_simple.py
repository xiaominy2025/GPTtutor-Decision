#!/usr/bin/env python3
"""
Simplified Flask API server for Render deployment
Basic version without heavy ML dependencies
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.6.6.6-simple",
        "message": "API server is running (simplified version)"
    })

@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return structured response"""
    try:
        data = request.get_json()
        print("📝 [BACKEND] Received POST /query")
        print("    Content-Type:", request.content_type)
        print("    Payload received:", data)

        if not data or 'query' not in data:
            print("❌ Missing 'query' field in request data.")
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400

        query = data['query']
        
        # Simple response for now
        response = {
            "status": "success",
            "data": {
                "answer": f"This is a simplified response to: {query}",
                "query": query,
                "course_id": "decision",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "simplified",
                "processing_time": 0.1,
                "conceptsToolsPractice": []
            }
        }

        print("✅ Query processed successfully.")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

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
        }
    }

    if course_id in courses:
        return jsonify({"metadata": courses[course_id]})
    else:
        return jsonify({"error": f"Course '{course_id}' not found"}), 404

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for basic functionality."""
    return jsonify({
        "message": "Simplified API is working",
        "version": "1.6.6.6-simple",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    print("🌐 Starting Simplified API Server...")
    print("📱 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health                    - Health check")
    print("   POST /query                     - Process query (simplified)")
    print("   GET  /api/course/<course_id>    - Get course metadata")
    print("   GET  /test                      - Test endpoint")

    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
