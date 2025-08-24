# Deploy V1666 Fix
# This script updates the Lambda function with the fixed response format

# Configuration
$ECR_REPO = "771049112957.dkr.ecr.us-east-2.amazonaws.com/engent-v1666-img"
$LAMBDA_FUNCTION = "engent-v1666-img"
$REGION = "us-east-2"
$TAG = "v1666_fixed"

Write-Host "🔧 Deploying V1666 Fix..." -ForegroundColor Green
Write-Host "ECR Repo: $ECR_REPO" -ForegroundColor Yellow
Write-Host "Lambda Function: $LAMBDA_FUNCTION" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Tag: $TAG" -ForegroundColor Yellow

# Step 1: Copy fixed lambda function
Write-Host "`n📝 Copying fixed lambda function..." -ForegroundColor Cyan
Copy-Item "Repeatability/lambda_function_fixed.py" "Repeatability/lambda_function.py" -Force

# Step 2: Login to ECR
Write-Host "`n📦 Logging into ECR..." -ForegroundColor Cyan
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}

# Step 3: Build Docker image with fixed lambda function
Write-Host "`n🔨 Building Docker image with fixed lambda function..." -ForegroundColor Cyan

# Force single-arch build for Lambda compatibility
$env:DOCKER_BUILDKIT = "0"
$env:DOCKER_DEFAULT_PLATFORM = "linux/amd64"

docker build -f Dockerfile.lambda_optimized -t $ECR_REPO:$TAG .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Step 4: Tag and push to ECR
Write-Host "`n📤 Pushing image to ECR..." -ForegroundColor Cyan
docker tag $ECR_REPO:$TAG $ECR_REPO:lambda-amd64
docker push $ECR_REPO:lambda-amd64

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

# Step 5: Update Lambda function
Write-Host "`n⚡ Updating Lambda function..." -ForegroundColor Cyan
aws lambda update-function-code --function-name $LAMBDA_FUNCTION --image-uri "$ECR_REPO:lambda-amd64" --region $REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to update Lambda function" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎉 V1666 Fix deployed successfully!" -ForegroundColor Green
Write-Host "Function URL: https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws" -ForegroundColor Cyan
Write-Host "Ready for testing!" -ForegroundColor Yellow
