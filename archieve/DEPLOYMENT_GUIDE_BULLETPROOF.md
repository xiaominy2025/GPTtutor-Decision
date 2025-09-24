# 🚀 V1.6.6.6 Bulletproof Deployment Guide

## Quick Start

### Prerequisites
- ✅ AWS CLI installed and configured
- ✅ Docker Desktop installed and running
- ✅ PowerShell (Windows) or Terminal (Mac/Linux)

### One-Command Deployment

```powershell
# Basic deployment
.\deploy_v1666_bulletproof.ps1

# Fresh start (deletes existing function)
.\deploy_v1666_bulletproof.ps1 -FreshStart

# Skip tests (faster deployment)
.\deploy_v1666_bulletproof.ps1 -SkipTests

# Custom function name
.\deploy_v1666_bulletproof.ps1 -LambdaName "my-custom-function"
```

## What This Script Does

### ✅ **Addresses ALL Previous Issues**
- **Windows compatibility**: Uses container deployment, excludes Windows files
- **Proxy issues**: Built-in proxy support with httpx
- **Import errors**: Verifies all imports work in container
- **Environment mismatches**: Uses Amazon Linux base image
- **Permission conflicts**: Uses unique statement IDs
- **Cold start optimization**: Lambda-ready optimizations included

### 🔧 **Comprehensive Error Handling**
- Validates AWS CLI and Docker before starting
- Checks all required files exist
- Verifies imports work in container
- Tests Lambda function after deployment
- Provides detailed error messages and troubleshooting steps

### 🧪 **Built-in Testing**
- Tests Lambda function directly via AWS CLI
- Tests function URL endpoint
- Validates health endpoint
- Provides test results and troubleshooting info

## Deployment Process

1. **Validation** - Checks AWS CLI, Docker, and required files
2. **Cleanup** - Removes old artifacts and Python cache
3. **Docker Build** - Creates optimized container image
4. **Import Verification** - Tests all imports work in container
5. **ECR Setup** - Creates/uses ECR repository
6. **Lambda Setup** - Creates/updates Lambda function
7. **Configuration** - Sets optimal Lambda settings
8. **Function URL** - Creates public endpoint
9. **Testing** - Validates deployment works
10. **Cleanup** - Removes temporary files

## Expected Output

```
🚀 === V1.6.6.6 BULLETPROOF DEPLOYMENT ===
Target: engent-labs-v1666-bulletproof in us-east-2
Account: 771049112957

🔍 Validating AWS CLI...
✅ AWS CLI: aws-cli/2.x.x

🔍 Validating Docker...
✅ Docker: Docker version 20.x.x

🔍 Validating required files...
✅ Found: api_server.py
✅ Found: query_engine_lambda_ready.py
✅ Found: requirements_container_lambda_ready.txt
✅ Found: vector_index.faiss
✅ Found: courses\decision\base_metadata.json

🧹 Cleaning up previous artifacts...
🗑️ Cleaned: build

🔨 Creating bulletproof Dockerfile...
📝 Creating comprehensive .dockerignore...
🔨 Building Docker image...
✅ Docker image built successfully

🔍 Verifying imports in container...
✅ All imports successful

📦 Setting up ECR repository...
✅ ECR repository exists: engent-labs-v1666-bulletproof

🔐 Logging into ECR...
✅ ECR login successful

📤 Pushing image to ECR...
✅ Image pushed successfully

⚡ Setting up Lambda function...
✅ Lambda function created successfully

⚙️ Configuring Lambda settings...
✅ Lambda settings configured

🌐 Creating function URL...
✅ Function URL created
🌐 Function URL: https://abc123.lambda-url.us-east-2.on.aws/

🧪 Testing deployment...
⏳ Waiting 15 seconds for Lambda to be ready...
🔍 Testing Lambda function directly...
✅ Direct Lambda test successful
Response: {"status": "healthy", "version": "v1.6.6.6"}

🔍 Testing via function URL...
✅ Function URL test successful
Status: 200
Response: {"status": "healthy", "version": "v1.6.6.6"}

🧹 Cleaning up temporary files...

🎉 === DEPLOYMENT COMPLETED SUCCESSFULLY ===
Function Name: engent-labs-v1666-bulletproof
Region: us-east-2
ECR Repository: engent-labs-v1666-bulletproof
Image URI: 771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-labs-v1666-bulletproof:latest

🌐 Function URL: https://abc123.lambda-url.us-east-2.on.aws/
Health Check: https://abc123.lambda-url.us-east-2.on.aws/health
Query Endpoint: https://abc123.lambda-url.us-east-2.on.aws/query

📋 Next Steps:
1. Test the health endpoint: https://abc123.lambda-url.us-east-2.on.aws/health
2. Test a query: POST https://abc123.lambda-url.us-east-2.on.aws/query with JSON payload
3. Monitor CloudWatch logs for any issues
4. Update your frontend to use the new function URL

🔧 Troubleshooting:
• Check CloudWatch logs: aws logs tail /aws/lambda/engent-labs-v1666-bulletproof --follow
• Test Lambda directly: aws lambda invoke --function-name engent-labs-v1666-bulletproof --payload '{"httpMethod":"GET","path":"/health"}' response.json
• View function details: aws lambda get-function --function-name engent-labs-v1666-bulletproof

✅ BULLETPROOF DEPLOYMENT COMPLETE!
```

## Troubleshooting

### Common Issues

#### ❌ "AWS CLI not found"
```bash
# Install AWS CLI
# Windows: Download from https://aws.amazon.com/cli/
# Mac: brew install awscli
# Linux: sudo apt install awscli
```

#### ❌ "Docker not found"
```bash
# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop/
```

#### ❌ "Missing required file"
```bash
# Ensure these files exist in your project root:
# - api_server.py
# - query_engine_lambda_ready.py
# - requirements_container_lambda_ready.txt
# - vector_index.faiss
# - courses/decision/base_metadata.json
```

#### ❌ "Docker build failed"
```bash
# Check docker_build.log for details
# Common issues:
# - Docker Desktop not running
# - Insufficient disk space
# - Network connectivity issues
```

#### ❌ "ECR login failed"
```bash
# Ensure AWS credentials are configured
aws configure
# Or set environment variables
$env:AWS_ACCESS_KEY_ID="your-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret"
```

#### ❌ "Lambda function creation failed"
```bash
# Check IAM permissions
# Ensure lambda-execution-role exists
# Verify account ID is correct
```

### Testing Your Deployment

#### Health Check
```bash
curl https://your-function-url.lambda-url.us-east-2.on.aws/health
```

#### Query Test
```bash
curl -X POST https://your-function-url.lambda-url.us-east-2.on.aws/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is decision making?"}'
```

#### CloudWatch Logs
```bash
aws logs tail /aws/lambda/your-function-name --follow
```

## Configuration

### Environment Variables
The script automatically sets these optimal Lambda environment variables:
- `COURSE_ID=decision`
- `METADATA_MODE=baked`
- `OMP_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `HF_HUB_DISABLE_TELEMETRY=1`

### Lambda Settings
- **Timeout**: 30 seconds
- **Memory**: 4096 MB
- **Architecture**: x86_64
- **Runtime**: Python 3.11

## Cost Optimization

### Current Optimizations
- ✅ CPU-only PyTorch (no GPU costs)
- ✅ Single-threaded execution (reduced memory)
- ✅ Lazy loading (faster cold starts)
- ✅ Optimized cache directories
- ✅ Disabled telemetry

### Additional Options
- **Provisioned Concurrency**: Reduces cold starts but increases costs
- **Reserved Concurrency**: Limits concurrent executions
- **Memory Optimization**: Can reduce from 4096MB if needed

## Security

### Current Security Features
- ✅ Function URL with CORS enabled
- ✅ No authentication (for public access)
- ✅ Environment variables for sensitive data
- ✅ IAM role-based permissions

### Additional Security Options
- **API Gateway**: Add authentication, rate limiting
- **VPC**: Deploy in private subnet
- **WAF**: Web Application Firewall
- **CloudTrail**: Audit logging

## Support

If you encounter issues:

1. **Check the logs**: `aws logs tail /aws/lambda/your-function-name --follow`
2. **Verify the deployment**: Test health endpoint
3. **Review error messages**: Look for specific error details
4. **Check prerequisites**: Ensure AWS CLI and Docker are working

The bulletproof script includes extensive error handling and will provide specific guidance for most issues.

