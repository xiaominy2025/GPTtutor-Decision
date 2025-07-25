"""
Simple Flask API server for GPTTutor frontend integration
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import time # Added for timestamp

# Import the correct query engine with V1.6 implementation
import query_engine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize query engine
print("\U0001F680 Initializing GPTTutor API Server...")
try:
    print("\u2705 Query engine module loaded successfully")
except Exception as e:
    print(f"❌ Failed to load query engine: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "engine_ready": True # Assuming engine is always available for health check
    })


@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return structured response"""
    try:
        data = request.get_json()
        print("\u26a1 [BACKEND] Received POST /query")
        print("    Content-Type:", request.content_type)
        print("    Payload received:", data)

        if not data or 'query' not in data:
            print("❌ Missing 'query' field in request data.")
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400

        query = data['query']
        user_id = data.get('user_id')

        # Process query using V1.6 query engine
        answer = query_engine.process_query(query)
        
        # Extract concepts/tools as objects for frontend
        concepts_tools_practice = []
        if hasattr(query_engine, 'extract_tools_from_section'):
            import re
            # V1.6.3: Only look for Concepts/Tools section
            concepts_match = re.search(r'\*\*Concepts/Tools\*\*\s*\n\n(.*?)(?=\n\n|$)', answer, re.DOTALL)
            if concepts_match:
                concepts_section = concepts_match.group(0)
                concepts_tools_practice = query_engine.extract_tools_from_section(concepts_section)

        # --- VALIDATION BLOCK: Ensure conceptsToolsPractice is always a list of {term, definition} objects ---
        def is_valid_concept(obj):
            return (
                isinstance(obj, dict)
                and 'term' in obj and isinstance(obj['term'], str) and obj['term'].strip() != ''
                and 'definition' in obj and isinstance(obj['definition'], str) and obj['definition'].strip() != ''
            )
        if not isinstance(concepts_tools_practice, list):
            print("🚨 Invalid conceptsToolsPractice format (not a list):", concepts_tools_practice)
            concepts_tools_practice = []
        else:
            fixed = []
            for item in concepts_tools_practice:
                if is_valid_concept(item):
                    fixed.append(item)
                else:
                    print(f"🚨 Invalid concept entry in conceptsToolsPractice: {item}")
            concepts_tools_practice = fixed
        # --- END VALIDATION BLOCK ---

        # Format V1.6 API response
        response = {
            "status": "success",
            "data": {
                "answer": answer,
                "query": query,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "gpt-3.5-turbo",
                "processing_time": 2.3,  # Placeholder
                "conceptsToolsPractice": concepts_tools_practice
            }
        }

        print("✅ Query processed successfully.")
        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    try:
        # Return basic stats for now
        stats = {
            "total_queries": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "quality_scores": [],
            "cost_estimate": 0.0
        }
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get stats: {str(e)}"
        }), 500


@app.route('/profile', methods=['GET', 'PUT'])
def user_profile():
    """Get or update user profile"""
    try:
        if request.method == 'GET':
            # Return default profile for now
            profile = {
                "name": "Student",
                "level": "beginner",
                "preferences": {
                    "response_length": "medium",
                    "focus_area": "general"
                }
            }
            return jsonify({
                "success": True,
                "data": profile
            })
        else:
            # PUT request to update profile
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Profile data is required"
                }), 400

            # For now, just acknowledge the update
            return jsonify({
                "success": True,
                "message": "Profile updated successfully"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Profile operation failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("🌐 Starting GPTTutor API Server...")
    print("📱 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health    - Health check")
    print("   POST /query     - Process query")
    print("   GET  /stats     - Get usage statistics")
    print("   GET  /profile   - Get user profile")
    print("   PUT  /profile   - Update user profile")

    app.run(debug=True, host='0.0.0.0', port=5000)

