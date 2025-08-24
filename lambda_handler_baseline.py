import json
from api_server_baseline import app as flask_app

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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*'
            },
            'body': resp.get_data(as_text=True)
        }
