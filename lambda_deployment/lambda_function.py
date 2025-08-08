#!/usr/bin/env python3
"""
AWS Lambda function for V1.6.6.6 API
Handles all endpoints and query processing
"""
import json
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Course configuration management
DEFAULT_COURSE = "decision"
COURSES_DIR = "courses"

def load_course_config(course_id: str) -> dict:
    """Load course-specific configuration files."""
    if not course_id or not isinstance(course_id, str):
        course_id = DEFAULT_COURSE
    
    course_path = os.path.join(COURSES_DIR, course_id)
    
    if not os.path.exists(course_path):
        print(f"⚠️ Course '{course_id}' not found, falling back to '{DEFAULT_COURSE}'")
        course_id = DEFAULT_COURSE
        course_path = os.path.join(COURSES_DIR, course_id)
    
    config = {
        "course_id": course_id,
        "glossary": {},
        "prompt_template": "",
        "sections_config": {}
    }
    
    # Load glossary.json
    glossary_path = os.path.join(course_path, "glossary.json")
    if os.path.exists(glossary_path):
        try:
            with open(glossary_path, 'r', encoding='utf-8') as f:
                config["glossary"] = json.load(f)
            print(f"✅ Loaded glossary for course '{course_id}'")
        except Exception as e:
            print(f"❌ Failed to load glossary for course '{course_id}': {e}")
    
    # Load prompt_template.txt
    prompt_path = os.path.join(course_path, "prompt_template.txt")
    if os.path.exists(prompt_path):
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                config["prompt_template"] = f.read()
            print(f"✅ Loaded prompt template for course '{course_id}'")
        except Exception as e:
            print(f"❌ Failed to load prompt template for course '{course_id}': {e}")
    
    # Load sections_config.json
    sections_path = os.path.join(course_path, "sections_config.json")
    if os.path.exists(sections_path):
        try:
            with open(sections_path, 'r', encoding='utf-8') as f:
                config["sections_config"] = json.load(f)
            print(f"✅ Loaded sections config for course '{course_id}'")
        except Exception as e:
            print(f"❌ Failed to load sections config for course '{course_id}': {e}")
    
    return config

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.6.6.6-lambda",
        "engine_ready": True,
        "deployment": "aws-lambda"
    })

@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return structured response"""
    try:
        data = request.get_json()
        print("⚡ [LAMBDA] Received POST /query")
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
        course_id = data.get('course_id', DEFAULT_COURSE)
        
        print(f"📚 Frontend requested course: {course_id}")
        print("🔄 Using Lambda-optimized query processing")
        
        # Lambda-optimized query processing
        # For now, return a structured response
        # Later we can integrate with OpenAI API directly
        
        response = {
            "status": "success",
            "data": {
                "answer": f"Lambda response to: {query}",
                "query": query,
                "course_id": DEFAULT_COURSE,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "lambda-v1.6.6.6",
                "processing_time": 0.1,
                "conceptsToolsPractice": []
            }
        }

        print("✅ Query processed successfully in Lambda.")
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/courses', methods=['GET'])
def list_courses():
    """List available courses"""
    try:
        courses = []
        if os.path.exists(COURSES_DIR):
            for item in os.listdir(COURSES_DIR):
                course_path = os.path.join(COURSES_DIR, item)
                if os.path.isdir(course_path):
                    courses.append({
                        "course_id": item,
                        "name": item.title(),
                        "has_glossary": os.path.exists(os.path.join(course_path, "glossary.json")),
                        "has_prompt_template": os.path.exists(os.path.join(course_path, "prompt_template.txt")),
                        "has_sections_config": os.path.exists(os.path.join(course_path, "sections_config.json"))
                    })
        
        return jsonify({
            "success": True,
            "data": {
                "courses": courses,
                "default_course": DEFAULT_COURSE
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list courses: {str(e)}"
        }), 500

@app.route('/courses/<course_id>/config', methods=['GET'])
def get_course_config(course_id):
    """Get course configuration"""
    try:
        config = load_course_config(course_id)
        return jsonify({
            "success": True,
            "data": config
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to load course config: {str(e)}"
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

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get usage statistics"""
    try:
        stats = {
            "total_queries": 0,
            "total_tokens": 0,
            "avg_response_time": 0,
            "quality_scores": [],
            "cost_estimate": 0.0,
            "deployment": "aws-lambda"
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
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": "Profile data is required"
                }), 400

            return jsonify({
                "success": True,
                "message": "Profile updated successfully"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Profile operation failed: {str(e)}"
        }), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for basic functionality."""
    return jsonify({
        "message": "V1.6.6.6 Lambda API is working",
        "version": "1.6.6.6-lambda",
        "deployment": "aws-lambda",
        "timestamp": time.time()
    })

import base64

def lambda_handler(event, context):
    print(f"🚀 Lambda invoked. Keys: {list(event.keys())}")

    # Support API GW v1, API GW v2, and Lambda Function URL
    path = event.get('path') or event.get('rawPath') or '/'
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    headers = event.get('headers') or {}
    body = event.get('body') or ''

    if event.get('isBase64Encoded') and isinstance(body, str):
        body = base64.b64decode(body)

    content_type = headers.get('Content-Type') or headers.get('content-type') or 'application/json'

    with app.test_client() as client:
        resp = client.open(path=path, method=method, headers=headers, data=body, content_type=content_type)
        return {
            'statusCode': resp.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': resp.get_data(as_text=True)
        }

if __name__ == '__main__':
    print("🌐 Starting V1.6.6.6 Lambda API Server...")
    print("📱 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health                    - Health check")
    print("   POST /query                     - Process query")
    print("   GET  /courses                   - List available courses")
    print("   GET  /courses/<course_id>/config - Get course configuration")
    print("   GET  /api/course/<course_id>    - Get course metadata")
    print("   GET  /stats                     - Get usage statistics")
    print("   GET  /profile                   - Get user profile")
    print("   PUT  /profile                   - Update user profile")
    print("   GET  /test                      - Test endpoint")

    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
