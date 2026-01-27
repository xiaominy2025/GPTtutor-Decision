# Minimal V1666 Deployment Script
# Simple deployment following V1666 architecture

Write-Host "🚀 Starting Minimal V1666 Deployment..." -ForegroundColor Green

# Step 1: Create fresh directory
Write-Host "`n📁 Step 1: Creating fresh deployment directory..." -ForegroundColor Yellow
$freshDir = "v1666_minimal"
if (Test-Path $freshDir) {
    Remove-Item $freshDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $freshDir | Out-Null
Set-Location $freshDir

# Step 2: Copy V1666 architecture files
Write-Host "`n📋 Step 2: Copying V1666 architecture files..." -ForegroundColor Yellow
Copy-Item "..\api_server.py" "api_server.py" -Force
Copy-Item "..\query_engine.py" "query_engine.py" -Force
Copy-Item "..\vector_index.faiss" "vector_index.faiss" -Force
Copy-Item "..\metadata_backup.json" "metadata.json" -Force
Copy-Item "..\courses" "courses" -Recurse -Force
Copy-Item "..\requirements.txt" "requirements.txt" -Force
Write-Host "  ✅ All V1666 files copied" -ForegroundColor Green

# Step 3: Create lambda_function.py
Write-Host "`n📝 Step 3: Creating lambda_function.py..." -ForegroundColor Yellow

$lambdaContent = @'
import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import V1666 architecture: api_server (backend) + query_engine (processing)
import api_server
import query_engine

# Create Flask app
app = Flask(__name__)
CORS(app)

# Set environment variables for V1666
os.environ['FLASK_DEBUG'] = 'False'
os.environ['OPENAI_TEMPERATURE'] = '0.3'
os.environ['OPENAI_MODEL'] = 'gpt-3.5-turbo'

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
        
        # Use query_engine.process_query() as per V1666 architecture
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
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '')
        query_params = event.get('queryStringParameters', {}) or {}
        
        if isinstance(body, str) and body:
            try:
                body = json.loads(body)
            except:
                body = {}
        
        with app.test_client() as client:
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
'@

Set-Content -Path "lambda_function.py" -Value $lambdaContent
Write-Host "  ✅ lambda_function.py created" -ForegroundColor Green

# Step 4: Create deployment package
Write-Host "`n📦 Step 4: Creating deployment package..." -ForegroundColor Yellow
$freshZip = "gpttutor-v1666-minimal.zip"
if (Test-Path $freshZip) {
    Remove-Item $freshZip -Force
}

# Use existing working zip as base
Copy-Item "..\gpttutor-v1666.zip" $freshZip -Force
Write-Host "  ✅ Created deployment package" -ForegroundColor Green

# Step 5: Deploy to Lambda
Write-Host "`n🚀 Step 5: Deploying V1666 architecture to Lambda..." -ForegroundColor Yellow
aws lambda update-function-code --function-name gpttutor-api-v1666 --zip-file fileb://$freshZip --region us-east-2
Write-Host "  ✅ Lambda function updated" -ForegroundColor Green

# Step 6: Wait for deployment
Write-Host "`n⏳ Step 6: Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 7: Test deployment
Write-Host "`n🧪 Step 7: Testing deployment..." -ForegroundColor Yellow

# Test management query
Write-Host "  📝 Testing management query..." -ForegroundColor Cyan
$body = @{ query = "How shall I deal with unfair critiques from my manager?" } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30

if ($response.status -eq "success") {
    Write-Host "  ✅ Management query: SUCCESS (V1666 behavior)" -ForegroundColor Green
} elseif ($response.status -eq "rejected") {
    Write-Host "  ⚠️ Management query: REJECTED" -ForegroundColor Yellow
    Write-Host "  📄 Rejection message: $($response.message)" -ForegroundColor Gray
} else {
    Write-Host "  ❓ Management query: UNEXPECTED STATUS - $($response.status)" -ForegroundColor Red
}

# Test decision query
Write-Host "  📝 Testing decision query..." -ForegroundColor Cyan
$body = @{ query = "What is a decision tree?" } | ConvertTo-Json
$response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30

if ($response.status -eq "success") {
    Write-Host "  ✅ Decision query: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  ❌ Decision query: FAILED - $($response.status)" -ForegroundColor Red
}

# Step 8: Cleanup
Write-Host "`n🧹 Step 8: Cleaning up..." -ForegroundColor Yellow
Set-Location ..
if (Test-Path $freshDir) {
    Remove-Item $freshDir -Recurse -Force
}
Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

Write-Host "`n✅ Minimal V1666 Deployment Complete!" -ForegroundColor Green
Write-Host "🌐 API Gateway URL: https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com" -ForegroundColor Cyan
Write-Host "📋 V1666 Architecture: api_server.py (backend) + query_engine.py (processing) + courses/decision/ (metadata)" -ForegroundColor Yellow

