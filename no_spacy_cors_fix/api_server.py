"""
Simple Flask API server for Engent Labs Backend V1.6.6.6 Final
Supports multi-course loading with dynamic configuration
"""
from flask import Flask, request, jsonify
import traceback
import time
import os
import json
from pathlib import Path

# Import the correct query engine with V1.6 implementation
import query_engine

app = Flask(__name__)

# Course configuration management
DEFAULT_COURSE = "decision"
COURSES_DIR = "courses"

# Define metadata loading constants
COURSE_ID = os.getenv("COURSE_ID", "decision")

# 1. Runtime metadata location (Lambda cold start creates this in rebuild mode)
TMP_META_PATH = Path(f"/tmp/courses/{COURSE_ID}/metadata.json")

# 2. Baked base metadata location
COURSE_DIR_PATH = Path(f"courses/{COURSE_ID}")
BASE_META_PATH = COURSE_DIR_PATH / "base_metadata.json"

# 3. Legacy metadata location (pre-transition)
LEGACY_META_PATH = COURSE_DIR_PATH / "metadata.json"

# Select the highest-priority existing file
if TMP_META_PATH.exists():
    SELECTED_META_PATH = TMP_META_PATH
elif BASE_META_PATH.exists():
    SELECTED_META_PATH = BASE_META_PATH
elif LEGACY_META_PATH.exists():
    SELECTED_META_PATH = LEGACY_META_PATH
else:
    raise FileNotFoundError(f"No metadata file found for course {COURSE_ID}")

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
print("\U0001F680 Initializing Engent Labs API Server V1.6.6.6 Final...")
try:
    print("\u2705 Query engine module loaded successfully")
except Exception as e:
    print(f"❌ Failed to load query engine: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "data": {
            "status": "healthy",
            "version": "V1.6.6.6",
            "engine_ready": True
        },
        "status": "success",
        "version": "V1.6.6.6",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })


@app.route('/query', methods=['POST'])
def process_query():
    """Process a query and return structured response"""
    # Process query request
    
    try:
        print("DEBUG: raw data", request.data)
        print("DEBUG: parsed json", request.get_json(force=True, silent=True))
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
        
        # V1.6.6.6 Final: Bypass course configuration to ensure 100% alignment
        # Still accept course_id from frontend for compatibility, but ignore it for processing
        print(f"📚 Frontend requested course: {course_id}")
        print("🔄 TEMPORARY: Bypassing course config, using direct query engine call")
        
        # Process query using V1.6 query engine directly (no course_config parameter)
        answer = query_engine.process_query(query)
        
        # Check if query was rejected by relevance filter
        if isinstance(answer, str) and answer.startswith("⚠️ This question doesn't appear to be related to the course"):
            print("⚠️ Query rejected by relevance filter")
            return jsonify({
                "status": "rejected",
                "message": answer,
                "data": {
                    "query": query,
                    "course_id": DEFAULT_COURSE,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "model": "gpt-3.5-turbo",
                    "processing_time": 0.1,  # Quick rejection
                    "conceptsToolsPractice": []
                }
            })
        
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

        # Format V1.6.6.6 API response
        response = {
            "data": {
                "answer": answer,
                "query": query,
                "course_id": DEFAULT_COURSE,  # Always return "decision" for compatibility
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "model": "gpt-3.5-turbo",
                "processing_time": 2.3,  # Placeholder timing
                "conceptsToolsPractice": concepts_tools_practice
            },
            "status": "success",
            "version": "V1.6.6.6",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
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
            "data": {
                "courses": courses,
                "default_course": DEFAULT_COURSE
            },
            "status": "success",
            "version": "V1.6.6.6",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
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
    V1.6.6.6 Final: Multi-course metadata route.
    Loads base_metadata.json and glossary.json for a given course.
    Falls back to 'decision' if the course does not exist.
    """
    import os, json
    base_path = os.path.join('courses', course_id)

    if not os.path.exists(base_path):
        course_id = 'decision'
        base_path = os.path.join('courses', course_id)

    try:
        # Use the selected metadata path based on priority
        with open(SELECTED_META_PATH) as f:
            metadata = json.load(f)
        with open(os.path.join(base_path, 'glossary.json')) as f:
            glossary = json.load(f)

        return jsonify({
            "data": {
                "course_id": course_id,
                "metadata": metadata,
                "glossary": glossary
            },
            "status": "success",
            "version": "V1.6.6.6",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
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
    print("🌐 Starting Engent Labs API Server V1.6.6.6 Final...")
    print("📱 Server will be available at http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /health                    - Health check")
    print("   POST /query                     - Process query")
    print("   GET  /courses                   - List available courses")
    print("   GET  /courses/<course_id>/config - Get course configuration")
    print("   GET  /api/course/<course_id>    - Get course metadata (V1.6.6.6)")
    print("   GET  /stats                     - Get usage statistics")
    print("   GET  /profile                   - Get user profile")
    print("   PUT  /profile                   - Update user profile")

    # Use environment variable for debug mode
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

