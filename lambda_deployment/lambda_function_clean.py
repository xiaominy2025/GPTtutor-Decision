import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import the original V1666 modules exactly as designed
import query_engine_original as query_engine
import api_server_original as api_server

# Create Flask app
app = Flask(__name__)
CORS(app)

# Set environment variables for V1666
os.environ['FLASK_DEBUG'] = 'False'
os.environ['OPENAI_TEMPERATURE'] = '0.3'
os.environ['OPENAI_MODEL'] = 'gpt-3.5-turbo'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "V1.6.6.6",
        "engine_ready": True
    })

@app.route('/courses', methods=['GET'])
def get_courses():
    """Return available courses using original V1666 logic"""
    return api_server.list_courses()

@app.route('/query', methods=['POST'])
def process_query():
    """Process query using original V1666 logic"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Query is required"
            }), 400
        
        # Use original V1666 process_query function exactly as designed
        result = query_engine.process_query(query)
        
        return jsonify({
            "status": "success",
            "data": {
                "query": query,
                "result": result,
                "model": os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                "course_id": "decision",
                "conceptsToolsPractice": [],
                "followUpPrompts": [],
                "processing_time": 0.1,
                "timestamp": "2025-08-10T01:35:00Z"
            }
        })
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process query: {str(e)}"
        }), 500

@app.route('/courses/<course_id>/config', methods=['GET'])
def get_course_config(course_id):
    """Get course configuration using original V1666 logic"""
    return api_server.get_course_config(course_id)

@app.route('/api/course/<course_id>', methods=['GET'])
def get_course_data(course_id):
    """Get course data using original V1666 logic"""
    return api_server.get_course_data(course_id)

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get stats using original V1666 logic"""
    return api_server.get_stats()

@app.route('/profile', methods=['GET', 'PUT'])
def handle_profile():
    """Handle profile using original V1666 logic"""
    if request.method == 'GET':
        return api_server.get_profile()
    else:
        return api_server.update_profile()

@app.route('/glossary', methods=['GET', 'POST'])
def get_glossary():
    """Get glossary using original V1666 logic"""
    try:
        course_id = 'decision'  # Default course
        
        if request.method == 'GET':
            course_id = request.args.get('course_id', 'decision')
        elif request.method == 'POST':
            data = request.get_json() or {}
            course_id = data.get('course_id', 'decision')
        
        # Use original V1666 load_course_config function
        config = api_server.load_course_config(course_id)
        glossary_data = config.get("glossary", {})
        
        return jsonify({
            "success": True,
            "data": {
                "glossary": glossary_data,
                "course_id": course_id,
                "total_terms": len(glossary_data)
            }
        })
        
    except Exception as e:
        print(f"Error loading glossary: {e}")
        return jsonify({
            "success": False,
            "error": f"Failed to load glossary: {str(e)}"
        }), 500

def lambda_handler(event, context):
    """AWS Lambda handler - routes requests to Flask app"""
    try:
        # Parse Lambda event
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Convert body to JSON if it's a string
        if isinstance(body, str) and body:
            try:
                body = json.loads(body)
            except:
                body = {}
        
        # Create Flask test client
        with app.test_client() as client:
            # Route the request
            if http_method == 'OPTIONS':
                response = client.options(path)
            elif http_method == 'GET':
                response = client.get(path, query_string=query_params)
            elif http_method == 'POST':
                response = client.post(path, json=body, query_string=query_params)
            elif http_method == 'PUT':
                response = client.put(path, json=body, query_string=query_params)
            else:
                return {
                    'statusCode': 405,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,PUT'
                    },
                    'body': json.dumps({"error": "Method not allowed"})
                }
            
            # Return Lambda response
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,PUT'
                },
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        print(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({"error": "Internal server error", "message": str(e)})
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
