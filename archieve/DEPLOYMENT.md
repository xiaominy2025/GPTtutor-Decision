# Engent Labs V1.6.6.6 Backend - Container Lambda Deployment

## 🎯 Overview

This deployment maintains **100% feature parity** with the existing V1.6.6.6 backend by:
- Using actual `api_server.py` and `query_engine.py` modules (no rewrites)
- Packaging as AWS Lambda container image
- Exposing all endpoints via API Gateway
- Loading heavy assets (models, glossary) once at import

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- Node.js and npm (for CDK)
- Python 3.11+

## 🚀 Quick Deployment

### Option 1: PowerShell (Windows)
```powershell
# Deploy everything in one command
.\scripts\deploy_container_lambda.ps1

# Or with custom parameters
.\scripts\deploy_container_lambda.ps1 -Region "us-east-2" -AccountId "771049112957" -ImageTag "v1.6.6.6"
```

### Option 2: Bash (Linux/Mac)
```bash
# Deploy everything in one command
./scripts/deploy_container_lambda.sh

# Or with custom parameters
./scripts/deploy_container_lambda.sh us-east-2 771049112957 v1.6.6.6
```

## 📝 Manual Step-by-Step

### 1. Test Local Server First
```bash
# Start local server
python api_server.py

# Test in another terminal
python test_local_server.py
```

### 2. Build Container Image
```bash
# Copy container requirements
cp requirements_container.txt requirements.txt

# Build Docker image
docker build -t engent-labs-backend-v1666 .
```

### 3. Push to ECR
```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 771049112957.dkr.ecr.us-east-2.amazonaws.com

# Create repository (if needed)
aws ecr create-repository --repository-name engent-labs-backend-v1666 --region us-east-2

# Tag and push
docker tag engent-labs-backend-v1666 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
docker push 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
```

### 4. Deploy Infrastructure
```bash
cd infra

# Install CDK dependencies
npm install -g aws-cdk
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap aws://771049112957/us-east-2

# Deploy stack
cdk deploy --require-approval never

cd ..
```

### 5. Update Lambda Function
```bash
aws lambda update-function-code \
    --function-name "engent-labs-backend-v1666" \
    --image-uri "771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest" \
    --region us-east-2

# Wait for update to complete
aws lambda wait function-updated --function-name "engent-labs-backend-v1666" --region us-east-2
```

## 🧪 Testing Deployment

### Run Parity Tests
```bash
# Get API Gateway URL from CDK output
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "EngentLabsBackendStack" \
    --region us-east-2 \
    --query "Stacks[0].Outputs[?OutputKey=='APIGatewayURL'].OutputValue" \
    --output text)

# Run comprehensive parity tests
python tests/parity/parity_check.py --local http://localhost:8000 --remote $API_URL

# Save detailed results
python tests/parity/parity_check.py --local http://localhost:8000 --remote $API_URL --output parity_results.json
```

### Manual Testing
```bash
# Health check
curl $API_URL/health

# Glossary
curl $API_URL/glossary

# Query test
curl -X POST $API_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How should I make a strategic business decision?"}'
```

## 📊 Expected Results

### Successful Deployment Should Show:
- ✅ All 8 parity tests PASS
- ✅ /health returns V1.6.6.6 version
- ✅ /query returns structured response with Strategic Thinking Lens, Follow-up Prompts, Concepts/Tools
- ✅ /glossary returns course concepts with aliases
- ✅ CloudWatch logs show single model loading at startup

### Response Structure Validation:
```json
{
  "status": "success",
  "data": {
    "answer": "**Strategic Thinking Lens**\n\n[narrative text]...\n\n**Follow-up Prompts**\n\n1. [question]\n2. [question]\n3. [question]\n\n**Concepts/Tools**\n\n- **Concept**: Definition...",
    "query": "original query",
    "course_id": "decision",
    "timestamp": "2025-01-09T...",
    "model": "gpt-3.5-turbo",
    "processing_time": 2.3,
    "conceptsToolsPractice": [
      {"term": "Strategic Framing", "definition": "..."},
      {"term": "SWOT Analysis", "definition": "..."}
    ]
  }
}
```

## 🔧 Environment Variables

Set these in AWS Lambda console or via CDK:
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_MODEL` - Model name (default: gpt-3.5-turbo)
- `OPENAI_MAX_TOKENS` - Max tokens (default: 1000)
- `OPENAI_TEMPERATURE` - Temperature (default: 0.3)

## 📍 Endpoints

All V1.6.6.6 endpoints are preserved:
- `GET /health` - Health check
- `POST /query` - Main query processing (full V1666.6 pipeline)
- `GET /courses` - List available courses
- `GET /courses/{course_id}/config` - Course configuration
- `GET /api/course/{course_id}` - Alternative course endpoint
- `GET /stats` - Statistics
- `GET /profile` - User profile
- `PUT /profile` - Update profile
- `GET /glossary` - Course glossary (added for container)

## 🚨 Troubleshooting

### Container Build Issues:
```bash
# Check Docker is running
docker info

# Clean build (if needed)
docker system prune -f
docker build --no-cache -t engent-labs-backend-v1666 .
```

### Lambda Cold Start:
- First request may take 10-15 seconds (model loading)
- Subsequent requests should be <3 seconds
- Consider provisioned concurrency for production

### Memory/Timeout Issues:
- Current: 3GB memory, 60s timeout
- Increase if needed via CDK or console
- Monitor CloudWatch metrics

### Parity Test Failures:
- Check local server is running on port 8000
- Verify API Gateway URL is correct
- Check CloudWatch logs for Lambda errors
- Compare response structures manually

## 🔄 Updates

To deploy code changes:
```bash
# Rebuild and push image
docker build -t engent-labs-backend-v1666 .
docker tag engent-labs-backend-v1666 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
docker push 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest

# Update Lambda function
aws lambda update-function-code \
    --function-name "engent-labs-backend-v1666" \
    --image-uri "771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest" \
    --region us-east-2
```
