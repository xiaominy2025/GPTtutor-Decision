# Engent Labs V1.6.6.6 Backend - Container Lambda Deployment

## 🎯 100% Feature Parity Deployment

This deployment preserves **ALL** V1.6.6.6 backend functionality using AWS Lambda containers with API Gateway.

### 📋 Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Docker** installed and running
3. **Node.js** for AWS CDK
4. **Python 3.11** for local testing

### 🔍 Current Backend Analysis

**Routes in api_server.py:**
- `GET /health` - Health check endpoint
- `POST /query` - Main query processing (full V1666.6 pipeline)  
- `GET /courses` - List available courses
- `GET /courses/<course_id>/config` - Get course configuration
- `GET /api/course/<course_id>` - Alternative course endpoint  
- `GET /stats` - Statistics endpoint
- `GET /profile` - User profile endpoint
- `PUT /profile` - Update user profile
- `GET /glossary` - Glossary endpoint (added by lambda_handler.py)

**Environment Variables:**
- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (default: "gpt-3.5-turbo")
- `OPENAI_MAX_TOKENS` (default: 1000)
- `OPENAI_TEMPERATURE` (default: 0.3)

**Heavy Assets (loaded once at import):**
- SentenceTransformer model ("all-MiniLM-L6-v2")
- FAISS vector index ("vector_index.faiss")
- spaCy NLP model ("en_core_web_sm")
- Complete concept glossary and patterns

## 🚀 Deployment Steps

### Step 1: Test Local Server

First, verify your local api_server.py is working:

```bash
# Start local server
python api_server.py

# In another terminal, test it
python test_local_server.py
```

Expected output:
```
🧪 Testing local server at http://localhost:8000
  Testing Health check...
    ✅ Health check - OK
       Keys: ['status', 'version', 'engine_ready']
  Testing Courses list...
    ✅ Courses list - OK
       Keys: ['success', 'data']
  Testing Query processing...
    ✅ Query processing - OK
       Keys: ['status', 'data']
       Answer preview: **Strategic Thinking Lens**...
       Concepts/Tools: 3 items
```

### Step 2: Set Environment Variables

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### Step 3: Deploy to AWS

#### Option A: PowerShell (Windows)
```powershell
# Make script executable and run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
./scripts/deploy_container_lambda.ps1
```

#### Option B: Bash (Linux/macOS)
```bash
# Make script executable and run
chmod +x scripts/deploy_container_lambda.sh
./scripts/deploy_container_lambda.sh
```

#### Option C: Manual Steps
```bash
# 1. Build Docker image
docker build -t engent-labs-backend-v1666 .

# 2. Authenticate with ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 771049112957.dkr.ecr.us-east-2.amazonaws.com

# 3. Create ECR repository (if needed)
aws ecr create-repository --repository-name engent-labs-backend-v1666 --region us-east-2

# 4. Tag and push image
docker tag engent-labs-backend-v1666 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
docker push 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest

# 5. Deploy CDK infrastructure
cd infra
npm install -g aws-cdk
pip install -r requirements.txt
cdk bootstrap aws://771049112957/us-east-2
cdk deploy --require-approval never
```

### Step 4: Run Parity Tests

After deployment completes, test 100% feature parity:

```bash
# Get the API Gateway URL from deployment output
API_URL="https://your-api-id.execute-api.us-east-2.amazonaws.com"

# Run parity tests
python tests/parity/parity_check.py --local http://localhost:8000 --remote $API_URL
```

Expected output:
```
🚀 Running 8 parity tests
   Local:  http://localhost:8000
   Remote: https://your-api-id.execute-api.us-east-2.amazonaws.com

🧪 Testing Health Check...
   ✅ PASSED
🧪 Testing Glossary...
   ✅ PASSED  
🧪 Testing Courses List...
   ✅ PASSED
🧪 Testing Query - Short Strategic...
   ✅ PASSED
🧪 Testing Query - Long Analytical...
   ✅ PASSED
🧪 Testing Query - Noisy Input...
   ✅ PASSED
🧪 Testing Query - Multi-Domain...
   ✅ PASSED
🧪 Testing Query - Glossary Heavy...
   ✅ PASSED

📊 Results: 8/8 tests passed
🎉 All parity tests PASSED - 100% feature parity confirmed!
```

## 🎯 Acceptance Criteria

✅ **All V1666.6 sections returned:**
- Strategic Thinking Lens
- Follow-Up Prompts  
- Concepts & Tools (with aliases)
- Application Field analysis

✅ **Single import-time initialization:**
- Models loaded once at container start
- No per-request reloading
- CloudWatch logs show single init

✅ **All endpoints working:**
- `/health` - Health check
- `/glossary` - Course glossary
- `/query` - Full V1666.6 pipeline
- All other api_server.py routes

## 📊 Performance Expectations

- **Cold start:** 15-30 seconds (model loading)
- **Warm requests:** 2-5 seconds (query processing)
- **Memory usage:** ~2-3 GB (ML models)
- **Timeout:** 60 seconds max

## 🔧 Troubleshooting

### Container Build Issues
```bash
# If Docker build fails, check requirements
docker build --no-cache -t engent-labs-backend-v1666 .
```

### Lambda Function Issues
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/engent-labs-backend-v1666 --follow

# Update function with new image
aws lambda update-function-code \
    --function-name engent-labs-backend-v1666 \
    --image-uri 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
```

### Parity Test Failures
```bash
# Run with detailed output
python tests/parity/parity_check.py \
    --local http://localhost:8000 \
    --remote $API_URL \
    --output parity_results.json

# Check specific endpoint
curl -X POST $API_URL/query \
    -H "Content-Type: application/json" \
    -d '{"query": "test query"}'
```

## 🎉 Success Confirmation

When deployment is successful, you should see:

1. **Deployment script output:**
   ```
   🎉 Deployment Complete!
      API Gateway URL: https://your-api-id.execute-api.us-east-2.amazonaws.com
      Lambda Function: engent-labs-backend-v1666
      ECR Image: 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-backend-v1666:latest
   ```

2. **Parity tests passing:**
   ```
   📊 Results: 8/8 tests passed
   🎉 All parity tests PASSED - 100% feature parity confirmed!
   ```

3. **CloudWatch logs showing single init:**
   ```
   🚀 Initializing Engent Labs API Server V1.6.6.6 Final...
   🔁 Loading V1666 models...
   ✅ V1666 models loaded in 4.24s
   ```

Your V1.6.6.6 backend is now deployed with **100% feature parity**! 🚀
