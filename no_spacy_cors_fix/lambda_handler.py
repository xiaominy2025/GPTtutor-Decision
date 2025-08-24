import json
import os
from api_server import app as flask_app

# CORS Configuration
PROD_ALLOWED_ORIGINS = {
    "https://engentlabs.com",
    "https://www.engentlabs.com", 
    "https://d1y6s1joavl0j7.cloudfront.net"
}
DEFAULT_ORIGIN = "https://engentlabs.com"
VERSION = "V1.6.6.6"

def pick_origin(event):
    """Pick the appropriate origin based on the request"""
    try:
        origin = event.get("headers", {}).get("origin") or event.get("headers", {}).get("Origin")
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
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Max-Age": "86400",
        "Content-Type": "application/json"
    }

def handle_options(event):
    """Handle OPTIONS preflight requests"""
    return {
        "statusCode": 200,
        "headers": cors_headers(event),
        "body": ""
    }

def lambda_handler(event, context):
    # Handle Function URL events (different structure than direct Lambda invocations)
    if 'requestContext' in event and 'http' in event.get('requestContext', {}):
        # Function URL event format
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        body = event.get('body', '')
        headers = event.get('headers', {})
    else:
        # Direct Lambda invocation format
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        headers = event.get('headers', {})
    
    # Handle OPTIONS preflight requests
    if method == 'OPTIONS':
        return handle_options(event)
    
    # Parse body if it's a string
    if isinstance(body, str) and body:
        try:
            body_json = json.loads(body)
        except Exception:
            body_json = None
    else:
        body_json = body
    
    # Use Flask test client to handle the request
    with flask_app.test_client() as client:
        if method == 'GET':
            resp = client.get(path)
        elif method == 'POST':
            resp = client.post(path, json=body_json)
        elif method == 'PUT':
            resp = client.put(path, json=body_json)
        else:
            resp = client.get('/health')
        
        return {
            'statusCode': resp.status_code,
            'headers': cors_headers(event),
            'body': resp.get_data(as_text=True)
        }
