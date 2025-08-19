#!/usr/bin/env python3
"""
AWS Lambda Handler for Real V1666 Backend (api_server.py + query_engine.py)
This handler imports the actual Flask app from api_server.py and adapts it for Lambda
"""

import json
import time
import os
import sys
import traceback
from pathlib import Path

# Import the real V1666 Flask app
from api_server import app as flask_app

def lambda_handler(event, context):
    """
    AWS Lambda entry point for real V1666 backend
    Uses the actual api_server.py Flask application
    """
    print("🚀 V1666 Real Backend Lambda Handler Starting")
    print(f"Event keys: {list(event.keys())}")
    
    try:
        # Parse different AWS Lambda event formats
        event_type = "unknown"
        http_method = "GET"
        path = "/"
        headers = {}
        body = None
        
        # Detect event format and extract data
        if 'rawPath' in event and 'routeKey' in event:
            # AWS Lambda Function URL format
            event_type = "Lambda Function URL"
            http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
            path = event.get('rawPath', '/')
            headers = event.get('headers', {})
            body = event.get('body')
            
        elif 'requestContext' in event and 'http' in event['requestContext']:
            # API Gateway v2.0 (HTTP API) format
            event_type = "API Gateway v2.0"
            http_context = event['requestContext']['http']
            http_method = http_context.get('method', 'GET')
            path = http_context.get('path', '/')
            headers = event.get('headers', {})
            body = event.get('body')
            
        elif 'requestContext' in event and 'resourcePath' in event['requestContext']:
            # API Gateway v1.0 (REST API) format
            event_type = "API Gateway v1.0"
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            headers = event.get('headers', {})
            body = event.get('body')
            
        elif 'httpMethod' in event:
            # Legacy API Gateway format
            event_type = "API Gateway (Legacy)"
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            headers = event.get('headers', {})
            body = event.get('body')
            
        else:
            # Direct Lambda invocation or unknown format
            event_type = "Direct Invocation"
            
        # Parse JSON body if it's a string
        parsed_body = None
        if body:
            if isinstance(body, str):
                try:
                    parsed_body = json.loads(body)
                except json.JSONDecodeError:
                    print(f"⚠️ Failed to parse JSON body: {body}")
                    parsed_body = {}
            else:
                parsed_body = body
        
        print(f"🔍 Event Type Detected: {event_type}")
        print(f"📡 HTTP {http_method} {path}")
        
        # Handle HTTP requests using the real Flask app
        if event_type != "Direct Invocation":
            # Create Flask test client for processing
            with flask_app.test_client() as client:
                # Handle different HTTP methods and paths
                if http_method == 'GET' and path == '/health':
                    response = client.get('/health')
                elif http_method == 'GET' and path == '/courses':
                    response = client.get('/courses')
                elif http_method == 'POST' and path == '/query':
                    print(f"📦 Parsed body: {parsed_body}")
                    
                    response = client.post('/query', 
                                         json=parsed_body or {},
                                         headers={'Content-Type': 'application/json'})
                elif http_method == 'GET' and path.startswith('/courses/'):
                    # Handle course-specific routes
                    response = client.get(path)
                elif http_method == 'GET' and path.startswith('/api/course/'):
                    # Handle API course routes
                    response = client.get(path)
                elif http_method == 'GET' and path == '/stats':
                    response = client.get('/stats')
                elif http_method in ['GET', 'PUT'] and path == '/profile':
                    if http_method == 'GET':
                        response = client.get('/profile')
                    else:
                        response = client.put('/profile', 
                                            json=parsed_body or {},
                                            headers={'Content-Type': 'application/json'})
                elif http_method == 'OPTIONS':
                    # Handle CORS preflight
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                            'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS',
                            'Access-Control-Max-Age': '3600'
                        },
                        'body': ''
                    }
                else:
                    # Unknown endpoint
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({"error": f"Not found: {http_method} {path}"})
                    }
                
                # Return Flask response as Lambda response
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization,Origin',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS'
                    },
                    'body': response.get_data(as_text=True)
                }
        
        else:
            # Direct Lambda invocation
            print("📞 Direct Lambda invocation detected")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "message": "V1666 Real Backend Lambda function is running",
                    "version": "V1666-Real",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "event_type": "Direct Invocation"
                })
            }
            
    except Exception as e:
        print(f"❌ Lambda handler error: {e}")
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }

if __name__ == '__main__':
    # Local development server
    print("🧪 Running V1666 Real Backend Lambda Function locally for testing")
    flask_app.run(debug=True, host='0.0.0.0', port=5000)
