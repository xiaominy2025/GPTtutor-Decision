# Deploy Lambda function with fixed concept extraction
# This script updates the Lambda function with the current query engine

Write-Host "🚀 Deploying Lambda function with fixed concept extraction..." -ForegroundColor Green

# Set variables
$FUNCTION_NAME = "engent-v1666-img"
$REGION = "us-east-2"
$ECR_REPO = "engent-v1666-img"
$NEW_TAG = "concept_extraction_fixed_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "📦 Building new Docker image with tag: $NEW_TAG" -ForegroundColor Yellow

# Copy current query engine to lambda_deployment
Write-Host "📋 Copying current query engine to deployment directory..." -ForegroundColor Yellow
Copy-Item "query_engine.py" "lambda_deployment/query_engine.py" -Force

# Build new Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -t "${ECR_REPO}:${NEW_TAG}" lambda_deployment/

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Login to ECR
Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin 771049112957.dkr.ecr.$REGION.amazonaws.com

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR login failed!" -ForegroundColor Red
    exit 1
}

# Tag image for ECR
Write-Host "🏷️ Tagging image for ECR..." -ForegroundColor Yellow
docker tag "${ECR_REPO}:${NEW_TAG}" "771049112957.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}:${NEW_TAG}"

# Push to ECR
Write-Host "📤 Pushing image to ECR..." -ForegroundColor Yellow
docker push "771049112957.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}:${NEW_TAG}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR push failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image pushed to ECR successfully" -ForegroundColor Green

# Update Lambda function
Write-Host "🔄 Updating Lambda function..." -ForegroundColor Yellow
aws lambda update-function-code --function-name $FUNCTION_NAME --image-uri "771049112957.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}:${NEW_TAG}" --region $REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lambda update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green
Write-Host "🎯 New image tag: $NEW_TAG" -ForegroundColor Cyan
Write-Host "🔗 Function URL: https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws/" -ForegroundColor Cyan

Write-Host "⏳ Waiting for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "✅ Deployment complete! Testing the updated function..." -ForegroundColor Green

# Test the updated function
Write-Host "🧪 Testing concept extraction..." -ForegroundColor Yellow
python test_tariff_query.py
