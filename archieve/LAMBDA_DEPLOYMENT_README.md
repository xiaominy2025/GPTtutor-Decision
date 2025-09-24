# AWS Lambda Backend Deployment Guide

## Overview
This guide covers deploying the full AWS Lambda backend with proper CORS handling and all dependencies.

## Files Updated

### 1. `lambda_function.py`
- ✅ **CORS Fixed**: Removed manual CORS headers from `lambda_handler`
- ✅ **Flask-CORS**: Now handles CORS automatically via `flask_cors.CORS(app)`
- ✅ **All Endpoints**: Supports `/health`, `/query`, `/courses`, `/api/course/<course_id>`, etc.

### 2. `lambda_requirements.txt`
- ✅ **Complete Dependencies**: All required packages with compatible versions
- ✅ **Flask Ecosystem**: Flask, Werkzeug, Flask-CORS, MarkupSafe, Jinja2
- ✅ **Additional Dependencies**: openai, python-dotenv, etc.

### 3. `deploy_lambda.py`
- ✅ **Dependency Installation**: Properly installs all dependencies
- ✅ **Package Creation**: Creates clean deployment package
- ✅ **AWS Deployment**: Deploys to Lambda function
- ✅ **Error Handling**: Better error handling and reporting

## Deployment Steps

### 1. Prerequisites
```bash
# Ensure you have AWS CLI configured
aws configure

# Verify Python and pip are available
python --version
pip --version
```

### 2. Deploy to AWS Lambda
```bash
# Run the deployment script
python deploy_lambda.py
```

### 3. Verify Deployment
```bash
# Test CORS functionality
python deploy_lambda.py --test
```

## Local Testing

### 1. Test Health Endpoint
```bash
curl -X GET "https://your-lambda-url.amazonaws.com/health"
```

### 2. Test CORS Preflight
```bash
curl -X OPTIONS "https://your-lambda-url.amazonaws.com/query" \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

### 3. Test Query Endpoint
```bash
curl -X POST "https://your-lambda-url.amazonaws.com/query" \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5173" \
  -d '{"query":"test query","course_id":"decision"}'
```

### 4. Test Course Endpoints
```bash
# List all courses
curl -X GET "https://your-lambda-url.amazonaws.com/courses"

# Get course metadata
curl -X GET "https://your-lambda-url.amazonaws.com/api/course/decision"
```

## Expected Responses

### Health Endpoint
```json
{
  "status": "healthy",
  "version": "1.6.6.6-lambda",
  "engine_ready": true,
  "deployment": "aws-lambda"
}
```

### Query Endpoint
```json
{
  "status": "success",
  "data": {
    "answer": "Lambda response to: your query",
    "query": "your query",
    "course_id": "decision",
    "timestamp": "2025-08-08T19:00:00Z",
    "model": "lambda-v1.6.6.6",
    "processing_time": 0.1,
    "conceptsToolsPractice": []
  }
}
```

### Courses Endpoint
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "course_id": "decision",
        "name": "Decision",
        "has_glossary": true,
        "has_prompt_template": true,
        "has_sections_config": true
      }
    ],
    "default_course": "decision"
  }
}
```

## Troubleshooting

### 1. CORS Issues
- ✅ **Fixed**: CORS is now handled by Flask-CORS
- ✅ **No Manual Headers**: Removed conflicting manual CORS headers
- ✅ **Proper Origin**: Supports `http://localhost:5173`

### 2. Dependency Issues
- ✅ **Complete Requirements**: All dependencies included
- ✅ **Proper Installation**: Dependencies installed with dependencies
- ✅ **No Missing Modules**: MarkupSafe, Jinja2, etc. included

### 3. Deployment Issues
- ✅ **Error Handling**: Better error reporting
- ✅ **Package Size**: Reports package size for verification
- ✅ **Clean Deployment**: Proper cleanup after deployment

## Frontend Integration

### Environment Variables
```javascript
// Your frontend should use these environment variables
VITE_API_BASE_URL=https://your-lambda-url.amazonaws.com
VITE_BACKEND_URL=https://your-lambda-url.amazonaws.com
VITE_DEPLOYMENT=aws-lambda
VITE_API_VERSION=v1.6.6.6
```

### Expected Frontend Behavior
- ✅ **Course Selection**: Should work with `/courses` and `/api/course/<course_id>`
- ✅ **Query Processing**: Should work with `/query` endpoint
- ✅ **CORS**: No more CORS errors
- ✅ **Error Handling**: Proper error responses

## Monitoring

### AWS Lambda Logs
```bash
# View recent logs
aws logs tail /aws/lambda/gpttutor-api-v1666 --follow
```

### Function URL
```bash
# Get function URL
aws lambda get-function-url-config --function-name gpttutor-api-v1666
```

## Success Criteria

- ✅ **CORS Working**: No CORS errors in browser console
- ✅ **All Endpoints**: `/health`, `/query`, `/courses`, `/api/course/*` working
- ✅ **Course Selection**: Frontend can fetch course information
- ✅ **Query Processing**: Queries are processed and responses returned
- ✅ **Error Handling**: Proper error responses for invalid requests

## Rollback Plan

If issues occur, you can rollback to the simple version:
```bash
python deploy_simple.py
```

This will deploy the simple Lambda function that was working for basic CORS functionality.
