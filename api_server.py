"""
Simple Flask API server for Engent Labs Backend V1.6.4
Supports multi-course loading with dynamic configuration
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import time
import os
import json

# Import the correct query engine with V1.6 implementation
import query_engine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Course configuration management
DEFAULT_COURSE = "decision"
COURSES_DIR = "courses"

def load_course_config(course_id: str) -> dict:
    """
    Load course-specific configuration files.
    Falls back to 'decision' course if course_id is missing or invalid.
    """
    # Validate course_id
    if not course_id or not isinstance(course_id, str):
        course_id = DEFAULT_COURSE
    
    course_path = os.path.join(COURSES_DIR, course_id)
    
    # Check if course directory exists
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

# Initialize query engine
print("\U0001F680 Initializing Engent Labs API Server V1.6.4...")
try:
    print("\u2705 Query engine module loaded successfully")
except Exception as e:
    print(f"❌ Failed to load query engine: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.6.5 (FINAL)",
        "engine_ready": True
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
        course_id = data.get('course_id', DEFAULT_COURSE)
        
        # Load course-specific configuration
        course_config = load_course_config(course_id)
        print(f"📚 Using course: {course_config['course_id']}")

        # Process query using V1.6 query engine with course configuration
        answer = query_engine.process_query(query, course_config=course_config)
        
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
                "course_id": course_config['course_id'],
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
    """
    V1.6.5 update: Multi-course metadata route.
    Loads metadata.json and glossary.json for a given course.
    Falls back to 'decision' if the course does not exist.
    """
    import os, json
    base_path = os.path.join('courses', course_id)

    if not os.path.exists(base_path):
        course_id = 'decision'
        base_path = os.path.join('courses', course_id)

    try:
        with open(os.path.join(base_path, 'metadata.json')) as f:
            metadata = json.load(f)
        with open(os.path.join(base_path, 'glossary.json')) as f:
            glossary = json.load(f)

        return jsonify({
            "course_id": course_id,
            "metadata": metadata,
            "glossary": glossary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
    print("🌐 Starting Engent Labs API Server V1.6.5 (FINAL)...")
    print("📱 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health                    - Health check")
    print("   POST /query                     - Process query")
    print("   GET  /courses                   - List available courses")
    print("   GET  /courses/<course_id>/config - Get course configuration")
    print("   GET  /api/course/<course_id>    - Get course metadata (V1.6.5)")
    print("   GET  /stats                     - Get usage statistics")
    print("   GET  /profile                   - Get user profile")
    print("   PUT  /profile                   - Update user profile")

    app.run(debug=True, host='0.0.0.0', port=5000)

