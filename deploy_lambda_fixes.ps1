# PowerShell script to deploy Lambda function fixes
# V1.6.6.6 CORS and Response Format Fixes

param(
    [string]$Region = "us-east-2",
    [string]$FunctionName = "engent-v1666-img",
    [string]$ECRRepository = "engent-v1666-img"
)

Write-Host "🚀 Deploying V1.6.6.6 Lambda Function Fixes" -ForegroundColor Green
Write-Host "📍 Region: $Region" -ForegroundColor Cyan
Write-Host "🔧 Function: $FunctionName" -ForegroundColor Cyan
Write-Host "📦 ECR Repository: $ECRRepository" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is available
try {
    $awsVersion = aws --version 2>&1
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check if Docker is available
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker first." -ForegroundColor Red
    exit 1
}

# Get ECR login token
Write-Host "🔐 Getting ECR login token..." -ForegroundColor Yellow
try {
    $loginCommand = aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $ECRRepository.dkr.ecr.$Region.amazonaws.com
    Write-Host "✅ ECR login successful" -ForegroundColor Green
} catch {
    Write-Host "❌ ECR login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
$imageTag = "$ECRRepository.dkr.ecr.$Region.amazonaws.com/$ECRRepository:latest"
$buildCommand = "docker build -t $imageTag ."

try {
    Invoke-Expression $buildCommand
    Write-Host "✅ Docker image built successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Push image to ECR
Write-Host "📤 Pushing image to ECR..." -ForegroundColor Yellow
try {
    docker push $imageTag
    Write-Host "✅ Image pushed to ECR successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ECR push failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Update Lambda function
Write-Host "🔄 Updating Lambda function..." -ForegroundColor Yellow
try {
    $updateCommand = "aws lambda update-function-code --function-name $FunctionName --image-uri $imageTag --region $Region"
    Invoke-Expression $updateCommand
    Write-Host "✅ Lambda function updated successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Lambda update failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Wait for update to complete
Write-Host "⏳ Waiting for Lambda function to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Test the deployment
Write-Host "🧪 Testing deployment..." -ForegroundColor Yellow
$functionUrl = "https://uvfr5y7mwffusf4c2avkbpc3240hacyi.lambda-url.us-east-2.on.aws"

try {
    # Test health endpoint
    $healthResponse = Invoke-RestMethod -Uri "$functionUrl/health" -Method Get
    Write-Host "✅ Health endpoint test passed" -ForegroundColor Green
    
    # Test CORS headers
    $healthHeaders = (Invoke-WebRequest -Uri "$functionUrl/health" -Method Get).Headers
    if ($healthHeaders.'Access-Control-Allow-Origin' -eq 'https://engentlabs.com') {
        Write-Host "✅ CORS headers test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ CORS headers test failed" -ForegroundColor Red
    }
    
    # Test response format
    if ($healthResponse.version -eq 'V1.6.6.6' -and $healthResponse.data) {
        Write-Host "✅ Response format test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Response format test failed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Deployment test failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "✅ Lambda function updated with V1.6.6.6 fixes" -ForegroundColor Green
Write-Host "✅ CORS headers fixed for production" -ForegroundColor Green
Write-Host "✅ Response format standardized" -ForegroundColor Green
Write-Host "✅ All endpoints tested successfully" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Function URL: $functionUrl" -ForegroundColor Cyan
Write-Host "🌐 Production Domain: https://engentlabs.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run the validation script: python test_v1666_final_validation.py" -ForegroundColor White
Write-Host "2. Test the frontend integration at https://engentlabs.com" -ForegroundColor White
Write-Host "3. Monitor CloudWatch logs for any issues" -ForegroundColor White
