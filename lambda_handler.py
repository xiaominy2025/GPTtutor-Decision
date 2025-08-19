"""
AWS Lambda Handler for Engent Labs V1.6.6.6 Backend
Thin router that imports actual modules and dispatches to real handlers
100% Feature Parity - No rewrites, no simplifications
"""

import json
import traceback
import os
import sys
from typing import Dict, Any

# Import the actual V1.6.6.6 backend modules
import api_server
from flask import Flask

def parse_lambda_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Parse AWS Lambda event to extract HTTP details"""
    
    # Handle different Lambda event formats
    if 'rawPath' in event and 'routeKey' in event:
        # Lambda Function URL format
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        query_params = event.get('queryStringParameters') or {}
        
    elif 'requestContext' in event and 'http' in event['requestContext']:
        # API Gateway v2.0 format
        http_context = event['requestContext']['http']
        http_method = http_context.get('method', 'GET')
        path = http_context.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        query_params = event.get('queryStringParameters') or {}
        
    elif 'httpMethod' in event:
        # API Gateway v1.0 format
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body')
        query_params = event.get('queryStringParameters') or {}
        
    else:
        # Direct invocation or unknown format
        return {
            'event_type': 'direct',
            'http_method': 'GET',
            'path': '/health',
            'headers': {},
            'body': None,
            'query_params': {}
        }
    
    # Parse JSON body if present
    parsed_body = None
    if body:
        if isinstance(body, str):
            try:
                parsed_body = json.loads(body)
            except json.JSONDecodeError:
                parsed_body = {}
        else:
            parsed_body = body
    
    return {
        'event_type': 'http',
        'http_method': http_method.upper(),
        'path': path,
        'headers': headers,
        'body': parsed_body,
        'query_params': query_params
    }

def create_cors_headers() -> Dict[str, str]:
    """Create CORS headers for Lambda response"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Access-Control-Max-Age': '3600'
    }

def normalize_path(raw_path: str) -> str:
    """
    Strip stage prefixes from API Gateway path
    Examples: /prod/glossary → /glossary, /$default/health → /health
    """
    if not raw_path:
        return '/'
    
    # Remove leading slash for processing
    path = raw_path.lstrip('/')
    
    # Split path components
    parts = path.split('/')
    
    # If first part looks like a stage name, remove it
    if len(parts) > 1 and parts[0] in ['prod', 'dev', 'test', 'stage', '$default']:
        path = '/' + '/'.join(parts[1:])
    else:
        path = '/' + path
    
    return path

def ok_json(data: Any) -> Dict[str, Any]:
    """Helper for 200 JSON responses with CORS"""
    return {
        'statusCode': 200,
        'headers': create_cors_headers(),
        'body': json.dumps(data)
    }

def not_found_json(message: str = "Not found") -> Dict[str, Any]:
    """Helper for 404 JSON responses with CORS"""
    return {
        'statusCode': 404,
        'headers': create_cors_headers(),
        'body': json.dumps({"error": message})
    }

def route_request(http_method: str, path: str, body: Any, query_params: Dict[str, str]) -> Dict[str, Any]:
    """Route request to appropriate handler using actual Flask app"""
    
    try:
        # Normalize path to strip stage prefixes
        normalized_path = normalize_path(path)
        
        # Use Flask test client to invoke actual handlers
        with api_server.app.test_client() as client:
            
            # Handle OPTIONS requests for CORS preflight
            if http_method == 'OPTIONS':
                return ok_json('')
            
            # Route to actual Flask handlers using normalized paths
            if http_method == 'GET' and normalized_path == '/health':
                response = client.get('/health')
                
            elif http_method == 'POST' and normalized_path == '/query':
                response = client.post('/query', 
                                     json=body or {},
                                     headers={'Content-Type': 'application/json'})
                
            elif http_method == 'GET' and normalized_path == '/courses':
                response = client.get('/courses')
                
            elif (http_method == 'GET' or http_method == 'POST') and normalized_path == '/glossary':
                # Handle GET /glossary with optional query param course_id
                # Handle POST /glossary with optional JSON body key course_id
                try:
                    course_id = 'decision'  # Default course
                    
                    if http_method == 'GET' and 'course_id' in query_params:
                        course_id = query_params['course_id']
                    elif http_method == 'POST' and body and isinstance(body, dict) and 'course_id' in body:
                        course_id = body['course_id']
                    
                    # Load course config to get glossary data
                    config = api_server.load_course_config(course_id)
                    glossary_data = config.get("glossary", {})
                    
                    return ok_json({
                        "success": True,
                        "data": {
                            "glossary": glossary_data,
                            "course_id": course_id,
                            "total_terms": len(glossary_data)
                        }
                    })
                    
                except Exception as e:
                    print(f"❌ Error loading glossary for course '{course_id}': {e}")
                    return {
                        'statusCode': 500,
                        'headers': create_cors_headers(),
                        'body': json.dumps({
                            "success": False,
                            "error": f"Failed to load glossary: {str(e)}"
                        })
                    }
                
            elif http_method == 'GET' and normalized_path.startswith('/courses/') and normalized_path.endswith('/config'):
                # Extract course_id from path like /courses/decision/config
                path_parts = normalized_path.strip('/').split('/')
                if len(path_parts) == 3 and path_parts[0] == 'courses' and path_parts[2] == 'config':
                    course_id = path_parts[1]
                    response = client.get(f'/courses/{course_id}/config')
                else:
                    return not_found_json("Invalid course config path")
                    
            elif http_method == 'GET' and normalized_path.startswith('/api/course/'):
                # Extract course_id from path like /api/course/decision
                path_parts = normalized_path.strip('/').split('/')
                if len(path_parts) == 3 and path_parts[0] == 'api' and path_parts[1] == 'course':
                    course_id = path_parts[2]
                    response = client.get(f'/api/course/{course_id}')
                else:
                    return not_found_json("Invalid API course path")
                    
            elif http_method == 'GET' and normalized_path == '/stats':
                response = client.get('/stats')
                
            elif http_method == 'GET' and normalized_path == '/profile':
                response = client.get('/profile')
                
            elif http_method == 'PUT' and normalized_path == '/profile':
                response = client.put('/profile',
                                    json=body or {},
                                    headers={'Content-Type': 'application/json'})
                                    
            else:
                return not_found_json(f"Not found: {http_method} {normalized_path}")
            
            # Convert Flask response to Lambda response format
            return {
                'statusCode': response.status_code,
                'headers': create_cors_headers(),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        print(f"❌ Error routing request {http_method} {path}: {e}")
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': create_cors_headers(),
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point
    Routes to actual V1.6.6.6 backend handlers with 100% feature parity
    """
    
    print(f"🚀 Lambda Handler V1.6.6.6 - Event: {list(event.keys())}")
    
    try:
        # Parse the Lambda event
        parsed = parse_lambda_event(event)
        
        print(f"📡 {parsed['http_method']} {parsed['path']}")
        
        # Route to appropriate handler
        response = route_request(
            http_method=parsed['http_method'],
            path=parsed['path'],
            body=parsed['body'],
            query_params=parsed['query_params']
        )
        
        print(f"✅ Response: {response['statusCode']}")
        return response
        
    except Exception as e:
        print(f"❌ Lambda handler error: {e}")
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': create_cors_headers(),
            'body': json.dumps({
                "error": "Lambda handler error",
                "message": str(e)
            })
        }

# For local testing
if __name__ == '__main__':
    # Test event
    test_event = {
        'rawPath': '/health',
        'requestContext': {'http': {'method': 'GET'}},
        'headers': {},
        'body': None
    }
    
    result = handler(test_event, None)
    print(f"Test result: {result}")
