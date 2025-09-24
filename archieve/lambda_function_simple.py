#!/usr/bin/env python3
"""
Simple AWS Lambda function for testing
"""
import json
import time

def lambda_handler(event, context):
    """Simple Lambda handler for testing"""
    print(f"🚀 Lambda invoked. Event keys: {list(event.keys())}")
    
    # Support API GW v1, API GW v2, and Lambda Function URL
    path = event.get('path') or event.get('rawPath') or '/'
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    headers = event.get('headers') or {}
    body = event.get('body') or ''
    
    print(f"📝 Request: {method} {path}")
    print(f"📋 Headers: {headers}")
    print(f"📦 Body: {body}")
    
    # Get origin from request headers
    origin = headers.get('origin', '*')
    
    # Define CORS headers
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
    }
    
    # Handle OPTIONS preflight requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    # Handle different endpoints
    if path == '/health' and method == 'GET':
        response_body = {
            "status": "healthy",
            "version": "1.6.6.6-lambda-simple",
            "engine_ready": True,
            "deployment": "aws-lambda",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    elif path == '/query' and method == 'POST':
        try:
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
                
            query = data.get('query', 'No query provided')
            course_id = data.get('course_id', 'decision')
            
            response_body = {
                "status": "success",
                "data": {
                    "answer": f"Simple Lambda response to: {query}",
                    "query": query,
                    "course_id": course_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "model": "lambda-simple-v1.6.6.6",
                    "processing_time": 0.1,
                    "conceptsToolsPractice": []
                }
            }
        except Exception as e:
            response_body = {
                "success": False,
                "error": f"Error processing query: {str(e)}"
            }
    else:
        response_body = {
            "message": "Simple Lambda API is working",
            "version": "1.6.6.6-lambda-simple",
            "deployment": "aws-lambda",
            "timestamp": time.time(),
            "path": path,
            "method": method
        }
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps(response_body)
    }
