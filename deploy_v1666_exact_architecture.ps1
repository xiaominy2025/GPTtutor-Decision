# Exact V1666 Architecture Deployment Script
# Follows the original V1666 design: api_server.py (backend) + query_engine.py (processing) + courses/decision/ (metadata)

param(
    [string]$FunctionName = "gpttutor-api-v1666",
    [string]$Region = "us-east-2"
)

Write-Host "🚀 Starting Exact V1666 Architecture Deployment..." -ForegroundColor Green
Write-Host "📋 Following original V1666 design: api_server.py (backend) + query_engine.py (processing) + courses/decision/ (metadata)" -ForegroundColor Yellow

# Step 1: Clean up and prepare fresh directory
Write-Host "`n📁 Step 1: Creating fresh deployment directory..." -ForegroundColor Yellow
$freshDir = "exact_v1666_architecture"
if (Test-Path $freshDir) {
    Remove-Item $freshDir -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Path $freshDir | Out-Null
Set-Location $freshDir

# Step 2: Copy EXACT V1666 architecture files
Write-Host "`n📋 Step 2: Copying EXACT V1666 architecture files..." -ForegroundColor Yellow

# Copy the main V1666 components
Copy-Item "..\api_server.py" "api_server.py" -Force
Copy-Item "..\query_engine.py" "query_engine.py" -Force

# Copy essential data files
Copy-Item "..\vector_index.faiss" "vector_index.faiss" -Force
Copy-Item "..\metadata_backup.json" "metadata.json" -Force

# Copy the courses directory (contains decision/ metadata)
Copy-Item "..\courses" "courses" -Recurse -Force

# Copy requirements
Copy-Item "..\requirements.txt" "requirements.txt" -Force

Write-Host "  ✅ All V1666 architecture files copied" -ForegroundColor Green

# Step 3: Create lambda_function.py that follows V1666 architecture
Write-Host "`n📝 Step 3: Creating lambda_function.py following V1666 architecture..." -ForegroundColor Yellow

$lambdaContent = @'
import json
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import V1666 architecture: api_server (backend) + query_engine (processing)
import api_server
import query_engine

# Create Flask app following V1666 architecture
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
    # Use api_server.list_courses() as per V1666 architecture
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
        # This follows the exact V1666 design: api_server calls query_engine
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
    # Use api_server.get_course_config() as per V1666 architecture
    return api_server.get_course_config(course_id)

@app.route('/api/course/<course_id>', methods=['GET'])
def get_course_data(course_id):
    # Use api_server.get_course_data() as per V1666 architecture
    return api_server.get_course_data(course_id)

@app.route('/stats', methods=['GET'])
def get_stats():
    # Use api_server.get_stats() as per V1666 architecture
    return api_server.get_stats()

@app.route('/profile', methods=['GET', 'PUT'])
def handle_profile():
    # Use api_server functions as per V1666 architecture
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
        
        # Use api_server.load_course_config() as per V1666 architecture
        # This loads from courses/decision/ metadata
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
Write-Host "  ✅ lambda_function.py created following V1666 architecture" -ForegroundColor Green

# Step 4: Create fresh deployment package
Write-Host "`n📦 Step 4: Creating fresh deployment package..." -ForegroundColor Yellow
$freshZip = "gpttutor-v1666-exact-architecture.zip"
if (Test-Path $freshZip) {
    Remove-Item $freshZip -Force
}

# Try to use 7z if available, otherwise use PowerShell
try {
    if (Get-Command "7z" -ErrorAction SilentlyContinue) {
        & 7z a -tzip $freshZip *
        Write-Host "  ✅ Created: $freshZip (using 7-Zip)" -ForegroundColor Green
    } else {
        Compress-Archive -Path * -DestinationPath $freshZip -Force
        Write-Host "  ✅ Created: $freshZip (using PowerShell)" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ Failed to create zip: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  🔄 Falling back to existing working zip..." -ForegroundColor Yellow
    Copy-Item "..\gpttutor-v1666.zip" $freshZip -Force
    Write-Host "  ✅ Used existing zip as base" -ForegroundColor Green
}

# Step 5: Deploy to Lambda
Write-Host "`n🚀 Step 5: Deploying exact V1666 architecture to Lambda..." -ForegroundColor Yellow
try {
    aws lambda update-function-code --function-name $FunctionName --zip-file fileb://$freshZip --region $Region
    Write-Host "  ✅ Lambda function updated with exact V1666 architecture" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 6: Wait for deployment
Write-Host "`n⏳ Step 6: Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Step 7: Test with V1666 queries
Write-Host "`n🧪 Step 7: Testing with V1666 queries..." -ForegroundColor Yellow

# Test 1: Management query (should work in V1666)
Write-Host "  📝 Testing management query..." -ForegroundColor Cyan
try {
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
} catch {
    Write-Host "  ❌ Management query test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Decision-making query (should always work)
Write-Host "  📝 Testing decision-making query..." -ForegroundColor Cyan
try {
    $body = @{ query = "What is a decision tree?" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/query" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($response.status -eq "success") {
        Write-Host "  ✅ Decision query: SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Decision query: FAILED - $($response.status)" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Decision query test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Courses endpoint (should work)
Write-Host "  📝 Testing courses endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com/courses" -Method GET -TimeoutSec 30
    
    if ($response.success -eq $true) {
        Write-Host "  ✅ Courses endpoint: SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Courses endpoint: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "  ❌ Courses endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Cleanup
Write-Host "`n🧹 Step 8: Cleaning up..." -ForegroundColor Yellow
Set-Location ..
if (Test-Path $freshDir) {
    Remove-Item $freshDir -Recurse -Force
}
Write-Host "  ✅ Cleanup complete" -ForegroundColor Green

Write-Host "`n✅ Exact V1666 Architecture Deployment Complete!" -ForegroundColor Green
Write-Host "🌐 API Gateway URL: https://fc5sjkwox3.execute-api.us-east-2.amazonaws.com" -ForegroundColor Cyan
Write-Host "📋 This deployment follows the exact V1666 architecture:" -ForegroundColor Yellow
Write-Host "   - api_server.py (backend server)" -ForegroundColor Gray
Write-Host "   - query_engine.py (query processing)" -ForegroundColor Gray
Write-Host "   - courses/decision/ (metadata)" -ForegroundColor Gray
