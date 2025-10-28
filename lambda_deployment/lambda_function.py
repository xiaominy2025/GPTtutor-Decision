import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import original V1666 modules - NO MODIFICATIONS
import query_engine
import api_server

# Create Flask app
app = Flask(__name__)
CORS(app)

# Set environment variables for V1666
os.environ['FLASK_DEBUG'] = 'False'
os.environ['OPENAI_TEMPERATURE'] = '0.3'
os.environ['OPENAI_MODEL'] = 'gpt-3.5-turbo'

# CORS Configuration for Lambda Function URLs
PROD_ALLOWED_ORIGINS = {
    "https://engentlabs.com",
    "https://www.engentlabs.com", 
    "https://d1y6s1joavl0j7.cloudfront.net"
}
DEFAULT_ORIGIN = "https://engentlabs.com"

def pick_origin(event):
    """Pick the appropriate origin based on the request"""
    try:
        headers = event.get("headers", {})
        origin = headers.get("origin") or headers.get("Origin")
        if origin in PROD_ALLOWED_ORIGINS:
            return origin
    except Exception:
        pass
    return DEFAULT_ORIGIN

def cors_headers(event):
    """Generate CORS headers based on the request"""
    origin = pick_origin(event)
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS,PUT",
        "Access-Control-Allow-Headers": "Content-Type,Authorization,Origin",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "V1.6.6.6",
        "engine_ready": True
    })

@app.route('/courses', methods=['GET'])
def get_courses():
    return api_server.list_courses()

@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "Query is required"
            }), 400
        
        # Use original V1666 process_query function - NO CHANGES
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
                "timestamp": "2025-08-10T03:00:00Z"
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
    return api_server.get_course_config(course_id)

@app.route('/api/course/<course_id>', methods=['GET'])
def get_course_data(course_id):
    return api_server.get_course_data(course_id)

@app.route('/stats', methods=['GET'])
def get_stats():
    return api_server.get_stats()

@app.route('/profile', methods=['GET', 'PUT'])
def handle_profile():
    if request.method == 'GET':
        return api_server.get_profile()
    else:
        return api_server.update_profile()

@app.route('/glossary', methods=['GET', 'POST'])
def get_glossary():
    try:
        course_id = 'decision'
        
        if request.method == 'GET':
            course_id = request.args.get('course_id', 'decision')
        elif request.method == 'POST':
            data = request.get_json() or {}
            course_id = data.get('course_id', 'decision')
        
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
    try:
        # Handle Lambda Function URL events (different structure)
        if 'requestContext' in event and 'http' in event.get('requestContext', {}):
            # Function URL event format
            http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
            path = event.get('rawPath', '/')
            body = event.get('body', '')
            query_params = event.get('queryStringParameters', {}) or {}
        else:
            # Direct Lambda invocation format
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            body = event.get('body', '')
            query_params = event.get('queryStringParameters', {}) or {}
        
        # Handle OPTIONS preflight requests
        if http_method == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": cors_headers(event),
                "body": ""
            }
        
        if isinstance(body, str) and body:
            try:
                body = json.loads(body)
            except:
                body = {}
        
        with app.test_client() as client:
            if http_method == 'GET':
                response = client.get(path, query_string=query_params)
            elif http_method == 'POST':
                response = client.post(path, json=body, query_string=query_params)
            elif http_method == 'PUT':
                response = client.put(path, json=body, query_string=query_params)
            else:
                return {
                    'statusCode': 405,
                    'headers': cors_headers(event),
                    'body': json.dumps({"error": "Method not allowed"})
                }
            
            return {
                'statusCode': response.status_code,
                'headers': cors_headers(event),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        print(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'headers': cors_headers(event),
            'body': json.dumps({"error": "Internal server error", "message": str(e)})
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
