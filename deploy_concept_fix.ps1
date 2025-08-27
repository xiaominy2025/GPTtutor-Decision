# Deploy Lambda function with fixed concept extraction
# Following the exact procedure from the deployment playbook

Write-Host "🚀 Deploying Lambda function with fixed concept extraction..." -ForegroundColor Green

# Set variables according to playbook
$TAG = "concept_extraction_fixed_v1666_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$ECR = "771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-v1666-img"
$FUNCTION_NAME = "engent-v1666-img"
$REGION = "us-east-2"

Write-Host "📦 Building new Docker image with tag: $TAG" -ForegroundColor Yellow

# Set Docker environment variables as per playbook
$env:DOCKER_BUILDKIT = "0"
$env:DOCKER_DEFAULT_PLATFORM = "linux/amd64"

# Build Docker image following playbook procedure
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build --platform linux/amd64 -f Dockerfile.lambda_optimized -t "engent-v1666-img:$TAG" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Login to ECR
Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR login failed!" -ForegroundColor Red
    exit 1
}

# Tag image for ECR
Write-Host "🏷️ Tagging image for ECR..." -ForegroundColor Yellow
docker tag "engent-v1666-img:${TAG}" "${ECR}:${TAG}"

# Push to ECR
Write-Host "📤 Pushing image to ECR..." -ForegroundColor Yellow
docker push "${ECR}:${TAG}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image pushed to ECR successfully" -ForegroundColor Green

# Update Lambda function
Write-Host "🔄 Updating Lambda function..." -ForegroundColor Yellow
aws lambda update-function-code --function-name $FUNCTION_NAME --region $REGION --image-uri "${ECR}:${TAG}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lambda update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green

# Reset handler as per playbook
Write-Host "🔧 Resetting Lambda handler..." -ForegroundColor Yellow
aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $REGION --handler "" --timeout 300 --memory-size 3008

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lambda configuration update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lambda configuration updated successfully!" -ForegroundColor Green

# Set environment variables as per playbook
Write-Host "🔧 Setting environment variables..." -ForegroundColor Yellow
aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $REGION --environment "Variables={OPENAI_API_KEY=<YOUR_API_KEY>,COURSE_ID=decision,FEATURE_DEDUP=1,FEATURE_STORY_MERGE=1}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Environment variables update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Environment variables set successfully!" -ForegroundColor Green

Write-Host "🎯 New image tag: $TAG" -ForegroundColor Cyan
Write-Host "🔗 Function URL: https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/" -ForegroundColor Cyan

Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "✅ Deployment complete! Testing the updated function..." -ForegroundColor Green

# Test the updated function
Write-Host "Testing concept extraction..." -ForegroundColor Yellow
python test_tariff_query.py
