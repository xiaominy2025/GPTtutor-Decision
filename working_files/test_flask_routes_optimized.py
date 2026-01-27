import json
import traceback

def lambda_handler(event, context):
    try:
        # Test importing the Flask app
        print("Testing Flask app import...")
        from api_server import app as flask_app
        print("✅ Flask app imported successfully")
        
        # Check if routes are registered
        print("Checking Flask routes...")
        routes = []
        for rule in flask_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        print(f"✅ Found {len(routes)} routes:")
        for route in routes:
            print(f"  - {route['rule']} -> {route['endpoint']} ({route['methods']})")
        
        # Test query endpoint specifically
        print("Testing query endpoint...")
        with flask_app.test_client() as client:
            resp = client.post('/query', json={
                'course_id': 'decision',
                'question': 'Under tariff uncertainty, how do I plan my production?'
            })
            print(f"✅ Query endpoint returned: {resp.status_code}")
            print(f"Response: {resp.get_data(as_text=True)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Flask routes test successful',
                'routes_count': len(routes),
                'routes': routes,
                'query_status': resp.status_code,
                'query_response': resp.get_data(as_text=True)
            })
        }
    except Exception as e:
        print(f"❌ Error during Flask test: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
