import json
import traceback

def lambda_handler(event, context):
    try:
        # Test importing the Flask app
        print("Testing Flask app import...")
        from api_server import app as flask_app
        print("✅ Flask app imported successfully")
        
        # Test importing query engine
        print("Testing query engine import...")
        import query_engine
        print("✅ Query engine imported successfully")
        
        # Test basic Flask functionality
        print("Testing Flask app functionality...")
        with flask_app.test_client() as client:
            resp = client.get('/health')
            print(f"✅ Flask health endpoint returned: {resp.status_code}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'V1666 imports successful',
                'flask_status': 'working',
                'query_engine_status': 'working'
            })
        }
    except Exception as e:
        print(f"❌ Error during import: {e}")
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
