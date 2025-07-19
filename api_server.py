"""
Simple Flask API server for GPTTutor frontend integration
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

from query_engine_refactored import QueryEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize query engine
print("🚀 Initializing GPTTutor API Server...")
try:
    engine = QueryEngine()
    print("✅ Query engine initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize query engine: {e}")
    engine = None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "engine_ready": engine is not None
    })


@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return structured response"""
    if not engine:
        return jsonify({
            "success": False,
            "error": "Query engine not initialized"
        }), 500
    
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Query is required"
            }), 400
        
        query = data['query']
        user_id = data.get('user_id')
        
        # Process query
        response = engine.process_query(query, user_id)
        
        return jsonify(response.to_json())
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    if not engine:
        return jsonify({
            "success": False,
            "error": "Query engine not initialized"
        }), 500
    
    try:
        stats = engine.get_usage_summary()
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
    if not engine:
        return jsonify({
            "success": False,
            "error": "Query engine not initialized"
        }), 500
    
    try:
        if request.method == 'GET':
            profile = engine.config.user_profile
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
            
            engine.config.update_user_profile(data)
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
    print("📡 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health    - Health check")
    print("   POST /query     - Process query")
    print("   GET  /stats     - Get usage statistics")
    print("   GET  /profile   - Get user profile")
    print("   PUT  /profile   - Update user profile")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 